import os
import collections
import random
import signal
import subprocess
import time

import pytest


ServerFixture = collections.namedtuple('ServerFixture', 'pid, port')
SshdFixture = collections.namedtuple('SshdFixture', 'addr, port')


@pytest.fixture(scope='module')
def server_process():
    port = random.randint(10000, 65535)
    proc = subprocess.Popen(['python', 'server.py', '--port', str(port)])
    yield ServerFixture(proc, port)
#    time.sleep(.3)
    os.kill(proc.pid, signal.SIGINT)
    proc.wait()


@pytest.fixture(scope='session')
def sshd():
    fromenv = os.environ.get('TESTS_SSHD', None)
    if fromenv:
        addr, port = fromenv.split(':')
        listen_addr, listen_port = addr, int(port)
    else:
        proc = subprocess.Popen(['netstat', '-nlp'], stdout=subprocess.PIPE)
        proc.wait()
        listen_addr, listen_port = None, None
        for line in proc.stdout.readlines():
            spl = line.decode().split()
            if 'tcp' not in spl:
                continue
            listen = spl[3].split(':')
            if listen[1] == '22':
                listen_addr, listen_port = listen[0], 22
                break
    yield SshdFixture(listen_addr, listen_port)
