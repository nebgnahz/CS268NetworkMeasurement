from rpyc.utils.factory import ssh_connect
from plumbum import SshMachine
from termcolor import colored
import string, subprocess, StringIO
from time import sleep
from threading import Thread

hosts = map(string.strip,open('pl-host-list').readlines())

def testHost(host, buff):
    try:
        try:
            conn = rpyc.connect(host, 18861)
            print >> buff, colored('Service Is Exposed Externally', 'red')
        except:
            pass
            #print >> buff, colored("Service Not Exposed Exterally",'green')

        rem = SshMachine(host, user='ucb_268_measure', keyfile='~/.ssh/id_rsa')
        #print >> buff, colored('SSH Connected', 'green')
        try:
            conn = ssh_connect(rem, 18861)
            #print >> buff, conn.root.test()
            conn.root.test()
        except Exception, e:
            print >> buff, colored('Service is not Running', 'red')
            print >> buff, 'Attempting to Start Service...'
            subprocess.call(["ssh", "-t", "-i", "~/.ssh/id_rsa", "ucb_268_measure@%s" % host, "sudo tking-server stop"])
            subprocess.call(["ssh", "-t", "-i", "~/.ssh/id_rsa", "ucb_268_measure@%s" % host, "sudo tking-server start"])
            try:
                sleep(4)
                conn = ssh_connect(rem, 18861)
                #print >> buff, conn.root.test()
                conn.root.test()
            except:
                #print >> buff, colored('Could not start service', 'red')
                return

        responses = []
        for i in range(3):
            try:
                response = conn.root.get_latency('ns.nwt.cz','217.197.152.132','ns1.google.com','216.239.32.10')
                if type(response) == type(''):
                    responses.append(response)

                end_time, start_time, ping_time, address = response

                latency = end_time - start_time - ping_time
                responses.append((latency, address))
            except:
                response.append(None)

        a = responses[0]
        b = responses[1]
        c = responses[2]
        k = conn.root.exposed_get_k('google.com', '8.8.8.8')

        print >> buff, "K:", k

        if type(a[0]) == type('') and type(b[0]) == type('') and type(c[0]) == type(''):
            print >> buff, colored('Amazon NS maybe inactive, or Node DNS server cannot bind', 'red')
            print >> buff, a, '\n', b, '\n', c
        elif a and b and c:
            print >> buff, colored('Recieved Latencies','green'), '\n', a, '\n', b, '\n', c
        else:
            print >> buff, colored ('Other Issue with latencies', 'red'), a, b, c
    except Exception, e:
        pass
        #print >> buff, colored('Could not connect', 'red')

threads = []
for host in hosts:
    buff = StringIO.StringIO()
    t = Thread(target=testHost, args=(host,buff))
    t.start()
    t.daemon = True
    threads.append((host, t, buff))

for host, t, buff in threads:
    t.join(timeout=60.0)

for host, t, buff in threads:
    print '-----------------'
    print host
    print buff.getvalue(),
