import sqlite3, socket, struct
from twisted.internet import reactor, defer
from twisted.names import client, dns

conn = sqlite3.connect('dns.db')
c = conn.cursor()

c.execute('''CREATE TABLE dns (name varchar(255), ip int)''')


sem = defer.DeferredSemaphore(112)

def ip2int(addr):                                                               
    return struct.unpack("!I", socket.inet_aton(addr))[0]                       

def int2ip(addr):                                                               
    return socket.inet_ntoa(struct.pack("!I", addr))   

def got_ptr(args, addr, level):
	(ans, auth, add) = args
	if level == 4:
		records = {}
		print '\n', addr
		print 'Additional:'
		for A in add:
			if A.type is dns.A:
				print A.name, A.payload.dottedQuad()
				records[A.name.name] = A.payload.dottedQuad()
		print 'Authoritative:'
		for NS in auth:
			if NS.type is dns.NS:
				if NS.payload.name.name not in records:
					records[NS.payload.name.name] = None
					print NS.payload.name.name, "No IP"
		for name, ip in records.items():
			if ip:
				t = name, ip, ip2int(ip), int2ip(ip2int(ip))
			else:
				t = name,
			print t
			#c.execute("INSERT INTO dns VALUES (?,?)", t)
			#c.commit()
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
