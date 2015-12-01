#!/usr/bin/env python3
""" Update the redis.submodule in the redislite repo to the latest stable version """
import os
import shutil
import urllib.request
import tarfile
import tempfile


url = 'http://download.redis.io/releases/redis-stable.tar.gz'


if __name__ == "__main__":
    shutil.rmtree('redis.submodule')
    with tempfile.TemporaryDirectory() as tempdir:
        ftpstream = urllib.request.urlopen(url)
        tf = tarfile.open(fileobj=ftpstream, mode="r|gz")
        directory = tf.next().name
        print(directory)
        tf.extractall(tempdir)
        shutil.move(os.path.join(tempdir, directory), 'redis.submodule')
        os.system('(cd redis.submodule;./deps/update-jemalloc.sh 4.0.4)')
	os.system('git add redis.submodule')
