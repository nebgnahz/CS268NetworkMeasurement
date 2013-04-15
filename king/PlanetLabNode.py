import os, paramiko, rpyc, subprocess
from plumbum.remote_machine import BaseRemoteMachine
from plumbum.paramiko_machine import ParamikoMachine
from rpyc.utils.factory import ssh_connect
from utilities import distance, outputException

def monkey(self, host, encoding='utf8'):
    self.host = host
    self._client = paramiko.SSHClient()
    self._client.load_system_host_keys()
    self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self._client.connect(host, username='ucb_268_measure', password=None)
    BaseRemoteMachine.__init__(self, encoding)

ParamikoMachine.__init__ = monkey

class PlanetLabNode(object):
    def __init__(self, host, ip, lat, lon):
        self.host = host
        self.ip = ip
        self.lat = float(lat)
        self.lon = float(lon)
        self.connected = False

    def connect(self):
        try:
            self.connectPL()
        except Exception, e:
            
            try:
                self.restartPL()
                self.connectPL()
            except Exception, e:
                outputException(e)  
                self.connected = False

    def connectPL(self):
        rem = ParamikoMachine(self.host)
        conn = ssh_connect(rem, 18861, config={'allow_pickle' : True})
        assert conn.root.test() == 1, "%s: RPC Failure" % self.host
        self.conn = conn
        self.connected = True

    def restartPL(self):
        FNULL = open(os.devnull, 'w')
        subprocess.call(["ssh", "-t", "-i", "~/.ssh/id_rsa", "-o StrictHostKeyChecking no",
                         "-o UserKnownHostsFile=/dev/null", "ucb_268_measure@%s" % self.host,
                         "sudo tking-server stop; sudo tking-server start;"],
                         stdout=FNULL, stderr=FNULL)

    def handleConnExceptions(fn):
        def wrapped(self, *args, **kwargs):
            if not self.connected:
                self.connect()

            if self.connected:
                try:
                    return fn(self, *args, **kwargs)
                except Exception, e:
                    outputException(e)
                    self.connected = False
                    try:
                        self.connect()
                        return fn(self, *args, **kwargs)
                    except Exception, e:
                        outputException(e)
                        self.connected = False
                        return None
            else:
                return None
        return wrapped

    @handleConnExceptions
    def get_latency(self, target1, ip1, target2, ip2):
        timed_latency = rpyc.timed(self.conn.root.get_latency, 10)
        return timed_latency(target1, ip1, target2, ip2).value

    @handleConnExceptions
    def get_k(self, target, ip):
        timed_k = rpyc.timed(self.conn.get_k, 10)
        return timed_k(target, ip).value

    def get_distance(self, lat, lon):
        return distance((self.lat, self.lon), (lat, lon))
