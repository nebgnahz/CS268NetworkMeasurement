from rpyc.utils.factory import ssh_connect
from plumbum import SshMachine
from termcolor import colored
import string, subprocess, StringIO
from time import sleep
from threading import Thread

hosts = map(string.strip,open('pl-host-list').readlines())

def testHost(host, buff):
    print >> buff, '\n', host
    try:
        try:
            conn = rpyc.connect(host, 18861)
            print >> buff, colored('Service Is Exposed Externally', 'red')
        except:
            print >> buff, colored("Service Not Exposed Exterally",'green')

        rem = SshMachine(host, user='ucb_268_measure', keyfile='~/.ssh/id_rsa')
        print >> buff, colored('SSH Connected', 'green')
        try:
            conn = ssh_connect(rem, 18861)
            print >> buff, conn.root.test()
        except Exception, e:
            print >> buff, colored('Service is not Running', 'red')
            print >> buff, 'Attempting to Start Service...'
            subprocess.call(["ssh", "-t", "-i", "~/.ssh/id_rsa", "ucb_268_measure@%s" % host, "sudo tking-server stop"])
            subprocess.call(["ssh", "-t", "-i", "~/.ssh/id_rsa", "ucb_268_measure@%s" % host, "sudo tking-server start"])
            try:
                sleep(4)
                conn = ssh_connect(rem, 18861)
                print >> buff, conn.root.test()
            except:
                print >> buff, colored('Could not start service', 'red')
                return

        a = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')
        b = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')
        c = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')

        if type(a) == type('') and type(b) == type('') and type(c) == type(''):
            print >> buff, colored('Amazon NS maybe inactive, or Node DNS server cannot bind', 'red')
            print >> buff, a, b, c
        elif a and b and c:
            print >> buff, colored('Recieved Latencies','green'), a, b, c
        else:
            print >> buff, colored ('Other Issue with latencies', 'red'), a, b, c
    except Exception, e:
        print >> buff, colored('Could not connect', 'red')

threads = []
for host in hosts:
    buff = StringIO.StringIO()
    t = Thread(target=testHost, args=(host,buff))
    t.start()
    threads.append((t,buff))

for t, buff in threads:
    t.join()

for t, buff in threads:
    print buff.getvalue()
