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
        print(f'Downloading {url} to temp directory {tempdir}')
        ftpstream = urllib.request.urlopen(url)
        tf = tarfile.open(fileobj=ftpstream, mode="r|gz")
        directory = tf.next().name
        
        print(f'Extracting archive {directory}')
        tf.extractall(tempdir)
        
        print(f'Moving {os.path.join(tempdir, directory)} -> redis.submodule')
        shutil.move(os.path.join(tempdir, directory), 'redis.submodule')
        
        # print('Updating jemalloc')
        # os.system('(cd redis.submodule;./deps/update-jemalloc.sh 4.0.4)')
        
        print('Adding new redis.submodule files to git')
        os.system('git add redis.submodule')
