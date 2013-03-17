import psycopg2, socket, struct
from twisted.internet import reactor
from twisted.names import client, dns

concurrent = 500
reactor.suggestThreadPoolSize(concurrent)

conn = psycopg2.connect('dbname=dns user=ahirreddy host=localhost')
c = conn.cursor()

def processResponse(args, addr, level):
    if level == 4:
        processRecords(*args)
    else:
        lookup(postfix=addr, level=level+1)

def processError(*args):
    pass

def processRecords(ans, auth, add):
    records = {}
    for A in filter(lambda x: x.type is dns.A, add):
        records[A.name.name] = A.payload.dottedQuad()
    for NS in filter(lambda x: x.type is dns.NS, auth):
        if NS.payload.name.name not in records:
            records[NS.payload.name.name] = None
    try:
        insertDB(records)
    except e:
        print e

def insertDB(records):
    for name, ip in records.items():
        if ip:
            query = '''INSERT INTO dns (name, ip) SELECT '%s', %i WHERE NOT EXISTS (SELECT 1 FROM dns WHERE name = '%s' and ip IS NOT NULL);''' % (name, ip2int(ip), name)
        else:
            query = '''INSERT INTO dns (name, ip) SELECT '%s', NULL WHERE NOT EXISTS (SELECT 1 FROM dns WHERE name = '%s');''' % (name, name)
        c.execute(query)
    conn.commit()

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def addTask(addr, level):
    req = client.lookupPointer(addr)
    req.addCallback(processResponse, addr, level)
    req.addErrback(processError, addr)

def lookup(postfix=None, level=1):
    for octet in range(0,20):
        if postfix:
            addr = "%i.%s" % (octet, postfix)
        else:
            addr = "%i.in-addr.arpa" % octet

        addTask(addr, level)

lookup()
try:
    reactor.run()
except KeyboardInterrupt:
    reactor.stop()
