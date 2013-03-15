import sqlite3, socket, struct
from twisted.internet import reactor, defer
from twisted.names import client

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
		print addr
		for a in add:
			print a.name, a.payload.dottedQuad()
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
