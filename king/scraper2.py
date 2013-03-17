import psycopg2, socket, struct, threading
from twisted.internet import reactor, defer
from twisted.names import client, dns
from twisted.names.error import DNSNameError
import itertools

concurrent = 120
finished=itertools.count(1)
count = 0;
sem = defer.DeferredSemaphore(concurrent)

# comment for different machines
# conn = psycopg2.connect('dbname=dns user=ahirreddy host=localhost')
conn = psycopg2.connect('dbname=postgres user=benzh host=localhost')
c = conn.cursor()

def processResponse(args, addr, level):
    processOne()
    if level < 4:
        lookup(postfix=addr, level=level+1)

def processError(*args):
    processOne()
    if isinstance(args[0],DNSNameError):
        reactor.stop()
        exit()

def processOne():
	#print finished
    if finished.next()==count:
        reactor.stop()

def processRecords(addr, level, auth, add):
    if auth == add == []:
        return
    else:
		    pass #print addr, level, auth, add
    records = {}
    for A in add:
        if A.type is dns.A:
            records[A.name.name] = A.payload.dottedQuad()
    for NS in auth:
        if NS.type is dns.NS:
            if NS.payload.name.name not in records:
                records[NS.payload.name.name] = None
    try:
        insertDB(records)
    except e:
        print "DB Error", e

def insertDB(records):
    for name, ip in records.items():
        if ip:
            query = '''INSERT INTO dns (name, ip) SELECT '%s', %i WHERE NOT EXISTS (SELECT 1 FROM dns WHERE name = '%s' and ip IS NOT NULL);''' % (name, ip2int(ip), name)
        else:
            query = '''INSERT INTO dns (name, ip) SELECT '%s', NULL WHERE NOT EXISTS (SELECT 1 FROM dns WHERE name = '%s');''' % (name, name)
						#print name, ip
        c.execute(query)
    conn.commit()

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def addTask(addr, level):
    req = sem.run(client.lookupPointer, addr).addCallback(processResponse, addr, level)
    req.addErrback(processError, addr)
		

def lookup(postfix, level):
    for octet in range(0,20):
        if postfix:
            addr = "%i.%s" % (octet, postfix)
        else:
            addr = "%i.in-addr.arpa" % octet

        addTask(addr, level)
        global count
        count = count + 1

lookup(None, 1)
try:
    reactor.run()
except KeyboardInterrupt:
    reactor.stop()
