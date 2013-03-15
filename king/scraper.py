import sqlite3, socket, struct
from twisted.internet import reactor, defer
from twisted.names import client, dns

conn = sqlite3.connect('dns.db')
c = conn.cursor()

#c.execute('''CREATE TABLE dns (name varchar(255), ip int)''')


sem = defer.DeferredSemaphore(112)

def dottedQuadToNum(ip):
    "convert decimal dotted quad string to long integer"
    return struct.unpack('L',socket.inet_aton(ip))[0]

def got_ptr(args, addr, level):
	(ans, auth, add) = args
	if level == 4:
		records = {}
		print '\n', addr
		print 'Additional:'
		for A in add:
			if A.type is dns.A:
				print A.name, A.payload.dottedQuad()
				records[A.name] = A.payload.dottedQuad()
		print 'Authoritative:'
		for NS in auth:
			if NS.type is dns.NS:
				if NS.payload.name not in records:
					records[NS.payload.name] = None
					print NS.payload.name, "No IP"
	else:
		lookup(postfix=addr, level=level + 1)

def no_ptr(*args):
	pass

def lookup(postfix=None, level=1):
	for octet in range(0,10):
		if postfix:
			addr = "%i.%s" % (octet, postfix)
		else:
			addr = "%i.in-addr.arpa" % octet

		f = lambda addr: client.lookupPointer(addr).addCallback(got_ptr, addr, level).addErrback(no_ptr)

		sem.run(f, addr)

lookup()
reactor.run()
