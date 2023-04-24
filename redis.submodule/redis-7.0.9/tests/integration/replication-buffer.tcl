# This test group aims to test that all replicas share one global replication buffer,
# two replicas don't make replication buffer size double, and when there is no replica,
# replica buffer will shrink.
start_server {tags {"repl external:skip"}} {
start_server {} {
start_server {} {
start_server {} {
    set replica1 [srv -3 client]
    set replica2 [srv -2 client]
    set replica3 [srv -1 client]

    set master [srv 0 client]
    set master_host [srv 0 host]
    set master_port [srv 0 port]

    $master config set save ""
    $master config set repl-backlog-size 16384
    $master config set repl-diskless-sync-delay 5
    $master config set repl-diskless-sync-max-replicas 1
    $master config set client-output-buffer-limit "replica 0 0 0"

    # Make sure replica3 is synchronized with master
    $replica3 replicaof $master_host $master_port
    wait_for_sync $replica3

    # Generating RDB will take some 100 seconds
    $master config set rdb-key-save-delay 1000000
    populate 100 "" 16

    # Make sure replica1 and replica2 are waiting bgsave
    $master config set repl-diskless-sync-max-replicas 2
    $replica1 replicaof $master_host $master_port
    $replica2 replicaof $master_host $master_port
    wait_for_condition 50 100 {
        ([s rdb_bgsave_in_progress] == 1) &&
        [lindex [$replica1 role] 3] eq {sync} &&
        [lindex [$replica2 role] 3] eq {sync}
    } else {
        fail "fail to sync with replicas"
    }

    test {All replicas share one global replication buffer} {
        set before_used [s used_memory]
        populate 1024 "" 1024 ; # Write extra 1M data
        # New data uses 1M memory, but all replicas use only one
        # replication buffer, so all replicas output memory is not
        # more than double of replication buffer.
        set repl_buf_mem [s mem_total_replication_buffers]
        set extra_mem [expr {[s used_memory]-$before_used-1024*1024}]
        assert {$extra_mem < 2*$repl_buf_mem}

        # Kill replica1, replication_buffer will not become smaller
        catch {$replica1 shutdown nosave}
        wait_for_condition 50 100 {
            [s connected_slaves] eq {2}
        } else {
            fail "replica doesn't disconnect with master"
        }
        assert_equal $repl_buf_mem [s mem_total_replication_buffers]
    }

    test {Replication buffer will become smaller when no replica uses} {
        # Make sure replica3 catch up with the master
        wait_for_ofs_sync $master $replica3

        set repl_buf_mem [s mem_total_replication_buffers]
        # Kill replica2, replication_buffer will become smaller
        catch {$replica2 shutdown nosave}
        wait_for_condition 50 100 {
            [s connected_slaves] eq {1}
        } else {
            fail "replica2 doesn't disconnect with master"
        }
        assert {[expr $repl_buf_mem - 1024*1024] > [s mem_total_replication_buffers]}
    }
}
}
}
}

# This test group aims to test replication backlog size can outgrow the backlog
# limit config if there is a slow replica which keep massive replication buffers,
# and replicas could use this replication buffer (beyond backlog config) for
# partial re-synchronization. Of course, replication backlog memory also can
# become smaller when master disconnects with slow replicas since output buffer
# limit is reached.
start_server {tags {"repl external:skip"}} {
start_server {} {
start_server {} {
    set replica1 [srv -2 client]
    set replica1_pid [s -2 process_id]
    set replica2 [srv -1 client]
    set replica2_pid [s -1 process_id]

    set master [srv 0 client]
    set master_host [srv 0 host]
    set master_port [srv 0 port]

    $master config set save ""
    $master config set repl-backlog-size 16384
    $master config set client-output-buffer-limit "replica 0 0 0"

    # Executing 'debug digest' on master which has many keys costs much time
    # (especially in valgrind), this causes that replica1 and replica2 disconnect
    # with master.
    $master config set repl-timeout 1000
    $replica1 config set repl-timeout 1000
    $replica2 config set repl-timeout 1000

    $replica1 replicaof $master_host $master_port
    wait_for_sync $replica1

    test {Replication backlog size can outgrow the backlog limit config} {
        # Generating RDB will take 1000 seconds
        $master config set rdb-key-save-delay 1000000
        populate 1000 master 10000
        $replica2 replicaof $master_host $master_port
        # Make sure replica2 is waiting bgsave
        wait_for_condition 5000 100 {
            ([s rdb_bgsave_in_progress] == 1) &&
            [lindex [$replica2 role] 3] eq {sync}
        } else {
            fail "fail to sync with replicas"
        }
        # Replication actual backlog grow more than backlog setting since
        # the slow replica2 kept replication buffer.
        populate 10000 master 10000
        assert {[s repl_backlog_histlen] > [expr 10000*10000]}
    }

    # Wait replica1 catch up with the master
    wait_for_condition 1000 100 {
        [s -2 master_repl_offset] eq [s master_repl_offset]
    } else {
        fail "Replica offset didn't catch up with the master after too long time"
    }

    test {Replica could use replication buffer (beyond backlog config) for partial resynchronization} {
        # replica1 disconnects with master
        $replica1 replicaof [srv -1 host] [srv -1 port]
        # Write a mass of data that exceeds repl-backlog-size
        populate 10000 master 10000
        # replica1 reconnects with master
        $replica1 replicaof $master_host $master_port
        wait_for_condition 1000 100 {
            [s -2 master_repl_offset] eq [s master_repl_offset]
        } else {
            fail "Replica offset didn't catch up with the master after too long time"
        }

        # replica2 still waits for bgsave ending
        assert {[s rdb_bgsave_in_progress] eq {1} && [lindex [$replica2 role] 3] eq {sync}}
        # master accepted replica1 partial resync
        assert_equal [s sync_partial_ok] {1}
        assert_equal [$master debug digest] [$replica1 debug digest]
    }

    test {Replication backlog memory will become smaller if disconnecting with replica} {
        assert {[s repl_backlog_histlen] > [expr 2*10000*10000]}
        assert_equal [s connected_slaves] {2}

        exec kill -SIGSTOP $replica2_pid
        r config set client-output-buffer-limit "replica 128k 0 0"
        # trigger output buffer limit check
        r set key [string repeat A [expr 64*1024]]
        # master will close replica2's connection since replica2's output
        # buffer limit is reached, so there only is replica1.
        wait_for_condition 100 100 {
            [s connected_slaves] eq {1}
        } else {
            fail "master didn't disconnect with replica2"
        }

        # Since we trim replication backlog inrementally, replication backlog
        # memory may take time to be reclaimed.
        wait_for_condition 1000 100 {
            [s repl_backlog_histlen] < [expr 10000*10000]
        } else {
            fail "Replication backlog memory is not smaller"
        }
        exec kill -SIGCONT $replica2_pid
    }
}
}
}

test {Partial resynchronization is successful even client-output-buffer-limit is less than repl-backlog-size} {
    start_server {tags {"repl external:skip"}} {
        start_server {} {
            r config set save ""
            r config set repl-backlog-size 100mb
            r config set client-output-buffer-limit "replica 512k 0 0"

            set replica [srv -1 client]
            $replica replicaof [srv 0 host] [srv 0 port]
            wait_for_sync $replica

            set big_str [string repeat A [expr 10*1024*1024]] ;# 10mb big string
            r multi
            r client kill type replica
            r set key $big_str
            r set key $big_str
            r debug sleep 2 ;# wait for replica reconnecting
            r exec
            # When replica reconnects with master, master accepts partial resync,
            # and don't close replica client even client output buffer limit is
            # reached.
            r set key $big_str ;# trigger output buffer limit check
            wait_for_ofs_sync r $replica
            # master accepted replica partial resync
            assert_equal [s sync_full] {1}
            assert_equal [s sync_partial_ok] {1}

            r multi
            r set key $big_str
            r set key $big_str
            r exec
            # replica's reply buffer size is more than client-output-buffer-limit but
            # doesn't exceed repl-backlog-size, we don't close replica client.
            wait_for_condition 1000 100 {
                [s -1 master_repl_offset] eq [s master_repl_offset]
            } else {
                fail "Replica offset didn't catch up with the master after too long time"
            }
            assert_equal [s sync_full] {1}
            assert_equal [s sync_partial_ok] {1}
        }
    }
}
