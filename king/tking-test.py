from rpyc.utils.factory import ssh_connect
from plumbum import SshMachine
from termcolor import colored
import string

hosts = map(string.strip,open('pl-host-list').readlines())

for host in hosts:
    print host
    try:
        try:
            conn = rpyc.connect(host, 18861)
            print colored('Service Is Exposed Externally', 'red')
        except:
            print colored("Service Not Exposed Exterally",'green')

        rem = SshMachine(host, user='ucb_268_measure', keyfile='~/.ssh/id_rsa')
        conn = ssh_connect(rem, 18861)
        conn.root.test()
        a = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')
        b = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')
        c = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')

        if a and b and c:
            print colored('Recieved Latencies','green'), a, b, c
        else:
            print ('Issue with latencies', 'red'), a, b, c
    except Exception, e:
        print colored('Could not connect', 'red')
    print
