import string, os, subprocess
from datetime import datetime
from threading import Thread, Lock
from PlanetLabNode import PlanetLabNode
from utilities import threaded_map
from termcolor import colored
from itertools import count

pl_hosts = [line.split(' ')[0:4] for line in map(string.strip,open('pl-host-list-geo').readlines())]
pl_nodes = map(lambda args: PlanetLabNode(*args), pl_hosts)
thread_count = count()
thread_count.next()
#print_lock = Lock()

def perNode(node):
    for x in range(5):
        try:
            node.connectPL()
            if node.conn.root.test() == 1:
                #print_lock.acquire()
                #print thread_count.next(), colored(node.host, 'green') 
                #print_lock.release()
                print thread_count.next(), node.host, True
                return node.host, True
        except Exception as e:
            ##print_lock.acquire()
            ##print node.host, e
            ##print_lock.release()
            try:
                FNULL = open(os.devnull, 'w')
                subprocess.call(["ssh", "-t", "-i", "~/.ssh/id_rsa", "-o StrictHostKeyChecking no",
                                 "-o UserKnownHostsFile=/dev/null", "-o ConnectTimeout=60", "ucb_268_measure@%s" % node.host,
                                 "sudo tking-server stop; sudo tking-server start;"],
                                 stdout=FNULL, stderr=FNULL)
            except Exception, e:
                pass
            continue
    #print_lock.acquire()
    #print thread_count.next(), colored(node.host, 'red', timeout=)
    #print_lock.release()
    print thread_count.next(), node.host, False
    return node.host, False

results = threaded_map(perNode, pl_nodes)

import smtplib


msg = "\n\nTking-Status %s\n" % str(datetime.now())
msg += "Operational:\n"
for host, success in results:
    if success:
        msg += "%s\n" % host
msg += "\nNon-Operational:\n"
for host, success in results:
    if not success:
        msg += "%s\n" % host

from DataPoint import DataPoint, Session
db_successes = Session().query(DataPoint).filter(DataPoint.success == True,).count()
db_fails = Session().query(DataPoint).filter(DataPoint.success == False,).count()

msg += '\nSuccessful Measurements: %i\n' % db_successes
msg += 'Failed Measurements: %i\n' % db_fails

# Send the mail
server = smtplib.SMTP('smtp.gmail.com',587) #port 465 or 587
server.ehlo()
server.starttls()
server.ehlo()
server.login('ucb.268.measure@gmail.com','ahirandben')
server.sendmail('ucb.268.measure@gmail.com',["ahirreddy@gmail.com", "nebgnahz@gmail.com"],msg)
server.close()
