from rpyc.utils.factory import ssh_connect
from plumbum import SshMachine

host = 'planetlab-1.imperial.ac.uk'

rem = SshMachine(host, user='ucb_268_measure', keyfile='~/.ssh/id_rsa')

conn = ssh_connect(rem, 18861)
#conn = rpyc.connect('pl2.planetlab.ics.tut.ac.jp', 18861)

conn.root.test()
a = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')
b = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')
c = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')

print a, b, c
