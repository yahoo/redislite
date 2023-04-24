source tests/support/cli.tcl

if {$::singledb} {
    set ::dbnum 0
} else {
    set ::dbnum 9
}

start_server {tags {"cli"}} {
    proc open_cli {{opts ""} {infile ""}} {
        if { $opts == "" } {
            set opts "-n $::dbnum"
        }
        set ::env(TERM) dumb
        set cmdline [rediscli [srv host] [srv port] $opts]
        if {$infile ne ""} {
            set cmdline "$cmdline < $infile"
            set mode "r"
        } else {
            set mode "r+"
        }
        set fd [open "|$cmdline" $mode]
        fconfigure $fd -buffering none
        fconfigure $fd -blocking false
        fconfigure $fd -translation binary
        set _ $fd
    }

    proc close_cli {fd} {
        close $fd
    }

    proc read_cli {fd} {
        set ret [read $fd]
        while {[string length $ret] == 0} {
            after 10
            set ret [read $fd]
        }

        # We may have a short read, try to read some more.
        set empty_reads 0
        while {$empty_reads < 5} {
            set buf [read $fd]
            if {[string length $buf] == 0} {
                after 10
                incr empty_reads
            } else {
                append ret $buf
                set empty_reads 0
            }
        }
        return $ret
    }

    proc write_cli {fd buf} {
        puts $fd $buf
        flush $fd
    }

    # Helpers to run tests in interactive mode

    proc format_output {output} {
        set _ [string trimright [regsub -all "\r" $output ""] "\n"]
    }

    proc run_command {fd cmd} {
        write_cli $fd $cmd
        set _ [format_output [read_cli $fd]]
    }

    proc test_interactive_cli {name code} {
        set ::env(FAKETTY) 1
        set fd [open_cli]
        test "Interactive CLI: $name" $code
        close_cli $fd
        unset ::env(FAKETTY)
    }

    # Helpers to run tests where stdout is not a tty
    proc write_tmpfile {contents} {
        set tmp [tmpfile "cli"]
        set tmpfd [open $tmp "w"]
        puts -nonewline $tmpfd $contents
        close $tmpfd
        set _ $tmp
    }

    proc _run_cli {host port db opts args} {
        set cmd [rediscli $host $port [list -n $db {*}$args]]
        foreach {key value} $opts {
            if {$key eq "pipe"} {
                set cmd "sh -c \"$value | $cmd\""
            }
            if {$key eq "path"} {
                set cmd "$cmd < $value"
            }
        }

        set fd [open "|$cmd" "r"]
        fconfigure $fd -buffering none
        fconfigure $fd -translation binary
        set resp [read $fd 1048576]
        close $fd
        set _ [format_output $resp]
    }

    proc run_cli {args} {
        _run_cli [srv host] [srv port] $::dbnum {} {*}$args
    }

    proc run_cli_with_input_pipe {mode cmd args} {
        if {$mode == "x" } {
            _run_cli [srv host] [srv port] $::dbnum [list pipe $cmd] -x {*}$args
        } elseif {$mode == "X"} {
            _run_cli [srv host] [srv port] $::dbnum [list pipe $cmd] -X tag {*}$args
        }
    }

    proc run_cli_with_input_file {mode path args} {
        if {$mode == "x" } {
            _run_cli [srv host] [srv port] $::dbnum [list path $path] -x {*}$args
        } elseif {$mode == "X"} {
            _run_cli [srv host] [srv port] $::dbnum [list path $path] -X tag {*}$args
        }
    }

    proc run_cli_host_port_db {host port db args} {
        _run_cli $host $port $db {} {*}$args
    }

    proc test_nontty_cli {name code} {
        test "Non-interactive non-TTY CLI: $name" $code
    }

    # Helpers to run tests where stdout is a tty (fake it)
    proc test_tty_cli {name code} {
        set ::env(FAKETTY) 1
        test "Non-interactive TTY CLI: $name" $code
        unset ::env(FAKETTY)
    }

    test_interactive_cli "INFO response should be printed raw" {
        set lines [split [run_command $fd info] "\n"]
        foreach line $lines {
            if {![regexp {^$|^#|^[^#:]+:} $line]} {
                fail "Malformed info line: $line"
            }
        }
    }

    test_interactive_cli "Status reply" {
        assert_equal "OK" [run_command $fd "set key foo"]
    }

    test_interactive_cli "Integer reply" {
        assert_equal "(integer) 1" [run_command $fd "incr counter"]
    }

    test_interactive_cli "Bulk reply" {
        r set key foo
        assert_equal "\"foo\"" [run_command $fd "get key"]
    }

    test_interactive_cli "Multi-bulk reply" {
        r rpush list foo
        r rpush list bar
        assert_equal "1) \"foo\"\n2) \"bar\"" [run_command $fd "lrange list 0 -1"]
    }

    test_interactive_cli "Parsing quotes" {
        assert_equal "OK" [run_command $fd "set key \"bar\""]
        assert_equal "bar" [r get key]
        assert_equal "OK" [run_command $fd "set key \" bar \""]
        assert_equal " bar " [r get key]
        assert_equal "OK" [run_command $fd "set key \"\\\"bar\\\"\""]
        assert_equal "\"bar\"" [r get key]
        assert_equal "OK" [run_command $fd "set key \"\tbar\t\""]
        assert_equal "\tbar\t" [r get key]

        # invalid quotation
        assert_equal "Invalid argument(s)" [run_command $fd "get \"\"key"]
        assert_equal "Invalid argument(s)" [run_command $fd "get \"key\"x"]

        # quotes after the argument are weird, but should be allowed
        assert_equal "OK" [run_command $fd "set key\"\" bar"]
        assert_equal "bar" [r get key]
    }

    test_tty_cli "Status reply" {
        assert_equal "OK" [run_cli set key bar]
        assert_equal "bar" [r get key]
    }

    test_tty_cli "Integer reply" {
        r del counter
        assert_equal "(integer) 1" [run_cli incr counter]
    }

    test_tty_cli "Bulk reply" {
        r set key "tab\tnewline\n"
        assert_equal "\"tab\\tnewline\\n\"" [run_cli get key]
    }

    test_tty_cli "Multi-bulk reply" {
        r del list
        r rpush list foo
        r rpush list bar
        assert_equal "1) \"foo\"\n2) \"bar\"" [run_cli lrange list 0 -1]
    }

    test_tty_cli "Read last argument from pipe" {
        assert_equal "OK" [run_cli_with_input_pipe x "echo foo" set key]
        assert_equal "foo\n" [r get key]

        assert_equal "OK" [run_cli_with_input_pipe X "echo foo" set key2 tag]
        assert_equal "foo\n" [r get key2]
    }

    test_tty_cli "Read last argument from file" {
        set tmpfile [write_tmpfile "from file"]

        assert_equal "OK" [run_cli_with_input_file x $tmpfile set key]
        assert_equal "from file" [r get key]

        assert_equal "OK" [run_cli_with_input_file X $tmpfile set key2 tag]
        assert_equal "from file" [r get key2]

        file delete $tmpfile
    }

    test_tty_cli "Escape character in JSON mode" {
        # reverse solidus
        r hset solidus \/ \/
        assert_equal \/ \/ [run_cli hgetall solidus]
        set escaped_reverse_solidus \"\\"
        assert_equal $escaped_reverse_solidus $escaped_reverse_solidus [run_cli --json hgetall \/]
        # non printable (0xF0 in ISO-8859-1, not UTF-8(0xC3 0xB0))
        set eth "\u00f0\u0065"
        r hset eth test $eth
        assert_equal \"\\xf0e\" [run_cli hget eth test]
        assert_equal \"\u00f0e\" [run_cli --json hget eth test]
        assert_equal \"\\\\xf0e\" [run_cli --quoted-json hget eth test]
        # control characters
        r hset control test "Hello\x00\x01\x02\x03World"
        assert_equal \"Hello\\u0000\\u0001\\u0002\\u0003World" [run_cli --json hget control test]
        # non-string keys
        r hset numkey 1 One
        assert_equal \{\"1\":\"One\"\} [run_cli --json hgetall numkey]
        # non-string, non-printable keys
        r hset npkey "K\u0000\u0001ey" "V\u0000\u0001alue"
        assert_equal \{\"K\\u0000\\u0001ey\":\"V\\u0000\\u0001alue\"\} [run_cli --json hgetall npkey]
        assert_equal \{\"K\\\\x00\\\\x01ey\":\"V\\\\x00\\\\x01alue\"\} [run_cli --quoted-json hgetall npkey]
    }

    test_nontty_cli "Status reply" {
        assert_equal "OK" [run_cli set key bar]
        assert_equal "bar" [r get key]
    }

    test_nontty_cli "Integer reply" {
        r del counter
        assert_equal "1" [run_cli incr counter]
    }

    test_nontty_cli "Bulk reply" {
        r set key "tab\tnewline\n"
        assert_equal "tab\tnewline" [run_cli get key]
    }

    test_nontty_cli "Multi-bulk reply" {
        r del list
        r rpush list foo
        r rpush list bar
        assert_equal "foo\nbar" [run_cli lrange list 0 -1]
    }

if {!$::tls} { ;# fake_redis_node doesn't support TLS
    test_nontty_cli "ASK redirect test" {
        # Set up two fake Redis nodes.
        set tclsh [info nameofexecutable]
        set script "tests/helpers/fake_redis_node.tcl"
        set port1 [find_available_port $::baseport $::portcount]
        set port2 [find_available_port $::baseport $::portcount]
        set p1 [exec $tclsh $script $port1 \
                "SET foo bar" "-ASK 12182 127.0.0.1:$port2" &]
        set p2 [exec $tclsh $script $port2 \
                "ASKING" "+OK" \
                "SET foo bar" "+OK" &]
        # Make sure both fake nodes have started listening
        wait_for_condition 50 50 {
            [catch {close [socket "127.0.0.1" $port1]}] == 0 && \
            [catch {close [socket "127.0.0.1" $port2]}] == 0
        } else {
            fail "Failed to start fake Redis nodes"
        }
        # Run the cli
        assert_equal "OK" [run_cli_host_port_db "127.0.0.1" $port1 0 -c SET foo bar]
    }
}

    test_nontty_cli "Quoted input arguments" {
        r set "\x00\x00" "value"
        assert_equal "value" [run_cli --quoted-input get {"\x00\x00"}]
    }

    test_nontty_cli "No accidental unquoting of input arguments" {
        run_cli --quoted-input set {"\x41\x41"} quoted-val
        run_cli set {"\x41\x41"} unquoted-val
        assert_equal "quoted-val" [r get AA]
        assert_equal "unquoted-val" [r get {"\x41\x41"}]
    }

    test_nontty_cli "Invalid quoted input arguments" {
        catch {run_cli --quoted-input set {"Unterminated}} err
        assert_match {*exited abnormally*} $err

        # A single arg that unquotes to two arguments is also not expected
        catch {run_cli --quoted-input set {"arg1" "arg2"}} err
        assert_match {*exited abnormally*} $err
    }

    test_nontty_cli "Read last argument from pipe" {
        assert_equal "OK" [run_cli_with_input_pipe x "echo foo" set key]
        assert_equal "foo\n" [r get key]

        assert_equal "OK" [run_cli_with_input_pipe X "echo foo" set key2 tag]
        assert_equal "foo\n" [r get key2]
    }

    test_nontty_cli "Read last argument from file" {
        set tmpfile [write_tmpfile "from file"]

        assert_equal "OK" [run_cli_with_input_file x $tmpfile set key]
        assert_equal "from file" [r get key]

        assert_equal "OK" [run_cli_with_input_file X $tmpfile set key2 tag]
        assert_equal "from file" [r get key2]

        file delete $tmpfile
    }

    proc test_redis_cli_rdb_dump {functions_only} {
        r flushdb
        r function flush

        set dir [lindex [r config get dir] 1]

        assert_equal "OK" [r debug populate 100000 key 1000]
        assert_equal "lib1" [r function load "#!lua name=lib1\nredis.register_function('func1', function() return 123 end)"]
        if {$functions_only} {
            set args "--functions-rdb $dir/cli.rdb"
        } else {
            set args "--rdb $dir/cli.rdb"
        }
        catch {run_cli {*}$args} output
        assert_match {*Transfer finished with success*} $output

        file delete "$dir/dump.rdb"
        file rename "$dir/cli.rdb" "$dir/dump.rdb"

        assert_equal "OK" [r set should-not-exist 1]
        assert_equal "should_not_exist_func" [r function load "#!lua name=should_not_exist_func\nredis.register_function('should_not_exist_func', function() return 456 end)"]
        assert_equal "OK" [r debug reload nosave]
        assert_equal {} [r get should-not-exist]
        assert_equal {{library_name lib1 engine LUA functions {{name func1 description {} flags {}}}}} [r function list]
        if {$functions_only} {
            assert_equal 0 [r dbsize]
        } else {
            assert_equal 100000 [r dbsize]
        }
    }

    foreach {functions_only} {no yes} {

    test "Dumping an RDB - functions only: $functions_only" {
        # Disk-based master
        assert_match "OK" [r config set repl-diskless-sync no]
        test_redis_cli_rdb_dump $functions_only

        # Disk-less master
        assert_match "OK" [r config set repl-diskless-sync yes]
        assert_match "OK" [r config set repl-diskless-sync-delay 0]
        test_redis_cli_rdb_dump $functions_only
    } {} {needs:repl needs:debug}

    } ;# foreach functions_only

    test "Scan mode" {
        r flushdb
        populate 1000 key: 1

        # basic use
        assert_equal 1000 [llength [split [run_cli --scan]]]

        # pattern
        assert_equal {key:2} [run_cli --scan --pattern "*:2"]

        # pattern matching with a quoted string
        assert_equal {key:2} [run_cli --scan --quoted-pattern {"*:\x32"}]
    }

    proc test_redis_cli_repl {} {
        set fd [open_cli "--replica"]
        wait_for_condition 500 100 {
            [string match {*slave0:*state=online*} [r info]]
        } else {
            fail "redis-cli --replica did not connect"
        }

        for {set i 0} {$i < 100} {incr i} {
           r set test-key test-value-$i
        }

        wait_for_condition 500 100 {
            [string match {*test-value-99*} [read_cli $fd]]
        } else {
            fail "redis-cli --replica didn't read commands"
        }

        fconfigure $fd -blocking true
        r client kill type slave
        catch { close_cli $fd } err
        assert_match {*Server closed the connection*} $err
    }

    test "Connecting as a replica" {
        # Disk-based master
        assert_match "OK" [r config set repl-diskless-sync no]
        test_redis_cli_repl

        # Disk-less master
        assert_match "OK" [r config set repl-diskless-sync yes]
        assert_match "OK" [r config set repl-diskless-sync-delay 0]
        test_redis_cli_repl
    } {} {needs:repl}

    test "Piping raw protocol" {
        set cmds [tmpfile "cli_cmds"]
        set cmds_fd [open $cmds "w"]

        set cmds_count 2101

        if {!$::singledb} {
            puts $cmds_fd [formatCommand select 9]
            incr cmds_count
        }
        puts $cmds_fd [formatCommand del test-counter]

        for {set i 0} {$i < 1000} {incr i} {
            puts $cmds_fd [formatCommand incr test-counter]
            puts $cmds_fd [formatCommand set large-key [string repeat "x" 20000]]
        }

        for {set i 0} {$i < 100} {incr i} {
            puts $cmds_fd [formatCommand set very-large-key [string repeat "x" 512000]]
        }
        close $cmds_fd

        set cli_fd [open_cli "--pipe" $cmds]
        fconfigure $cli_fd -blocking true
        set output [read_cli $cli_fd]

        assert_equal {1000} [r get test-counter]
        assert_match "*All data transferred*errors: 0*replies: ${cmds_count}*" $output

        file delete $cmds
    }

    test "Options -X with illegal argument" {
        assert_error "*-x and -X are mutually exclusive*" {run_cli -x -X tag}

        assert_error "*Unrecognized option or bad number*" {run_cli -X}

        assert_error "*tag not match*" {run_cli_with_input_pipe X "echo foo" set key wrong_tag}
    }

    test "DUMP RESTORE with -x option" {
        set cmdline [rediscli [srv host] [srv port]]

        exec {*}$cmdline DEL set new_set
        exec {*}$cmdline SADD set 1 2 3 4 5 6
        assert_equal 6 [exec {*}$cmdline SCARD set]

        assert_equal "OK" [exec {*}$cmdline -D "" --raw DUMP set | \
                                {*}$cmdline -x RESTORE new_set 0]

        assert_equal 6 [exec {*}$cmdline SCARD new_set]
        assert_equal "1\n2\n3\n4\n5\n6" [exec {*}$cmdline SMEMBERS new_set]
    }

    test "DUMP RESTORE with -X option" {
        set cmdline [rediscli [srv host] [srv port]]

        exec {*}$cmdline DEL zset new_zset
        exec {*}$cmdline ZADD zset 1 a 2 b 3 c
        assert_equal 3 [exec {*}$cmdline ZCARD zset]

        assert_equal "OK" [exec {*}$cmdline -D "" --raw DUMP zset | \
                                {*}$cmdline -X dump_tag RESTORE new_zset 0 dump_tag REPLACE]

        assert_equal 3 [exec {*}$cmdline ZCARD new_zset]
        assert_equal "a\n1\nb\n2\nc\n3" [exec {*}$cmdline ZRANGE new_zset 0 -1 WITHSCORES]
    }
}
