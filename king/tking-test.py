from rpyc.utils.factory import ssh_connect
from plumbum import SshMachine
from termcolor import colored
import string
from time import sleep

hosts = map(string.strip,open('pl-host-list').readlines())

for host in hosts:
    print '\n', host
    try:
        try:
            conn = rpyc.connect(host, 18861)
            print colored('Service Is Exposed Externally', 'red')
        except:
            print colored("Service Not Exposed Exterally",'green')

        rem = SshMachine(host, user='ucb_268_measure', keyfile='~/.ssh/id_rsa')
        print colored('SSH Connected', 'green')
        try:
            conn = ssh_connect(rem, 18861)
            conn.root.test()
        except Exception, e:
            print colored('Service is not Running', 'red')
            print 'Attempting to Start Service...'
            start = rem['start-server.sh']
            print start()
            print rem['ps']['aux']()
            try:
                sleep(4)
                conn = ssh_connect(rem, 18861)
                conn.root.test()
            except:
                print colored('Could not start service', 'red')
                continue

        a = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')
        b = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')
        c = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')

        if type(a) == type('') and type(b) == type('') and type(c) == type(''):
            print colored('Amazon NS maybe inactive, or Node DNS server cannot bind', 'red')
            print a, b, c
        elif a and b and c:
            print colored('Recieved Latencies','green'), a, b, c
        else:
            print ('Other Issue with latencies', 'red'), a, b, c
    except Exception, e:
        print colored('Could not connect', 'red')
