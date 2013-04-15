import paramiko
from plumbum.remote_machine import BaseRemoteMachine
from plumbum.paramiko_machine import ParamikoMachine

def monkey(self, host, encoding='utf8'):
    self.host = host
    self._client = paramiko.SSHClient()
    self._client.load_system_host_keys()
    self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self._client.connect(host, username='ucb_268_measure', password=None)
    BaseRemoteMachine.__init__(self, encoding)

#ParamikoMachine.__init__ = monkey

CustomMachine = ParamikoMachine
