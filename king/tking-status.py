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
                return node.host, True
        except Exception as e:
            ##print_lock.acquire()
            ##print node.host, e
            ##print_lock.release()
            try:
                FNULL = open(os.devnull, 'w')
                subprocess.call(["ssh", "-t", "-i", "~/.ssh/id_rsa", "-o StrictHostKeyChecking no",
                                 "-o UserKnownHostsFile=/dev/null", "ucb_268_measure@%s" % node.host,
                                 "sudo tking-server stop; sudo tking-server start;"],
                                 stdout=FNULL, stderr=FNULL)
            except Exception, e:
                pass
            continue
    #print_lock.acquire()
    #print thread_count.next(), colored(node.host, 'red', timeout=)
    #print_lock.release()
    return node.host, False

results = threaded_map(perNode, pl_nodes)

import smtplib
TO = ["ahirreddy@gmail.com"] # must be a list
SUBJECT = "Tking-Status %s" % str(datetime.now())

TEXT = "Operational:\n"
for host, success in results:
    if success:
        TEXT += "%s\n" % host
TEXT = "\nNon-Operational:\n"
for host, success in results:
    if not success:
        TEXT += "%s\n" % host

# Prepare actual message

message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, TEXT)

# Send the mail
server = smtplib.SMTP('smtp.gmail.com',587) #port 465 or 587
server.ehlo()
server.starttls()
server.ehlo()
server.login('ucb.268.measure@gmail.com','ahirandben')
server.sendmail('ucb.268.measure@gmail.com',TO,TEXT)
server.close()
