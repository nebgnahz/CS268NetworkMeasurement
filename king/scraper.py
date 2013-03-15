import sqlite3, socket, struct
from twisted.internet import reactor, defer
from twisted.names import client, dns

conn = sqlite3.connect('dns.db')
c = conn.cursor()

c.execute('''CREATE TABLE dns (name TEXT, ip INTEGER)''')

sem = defer.DeferredSemaphore(112)

def ip2int(addr):                       
    return struct.unpack("!I", socket.inet_aton(addr))[0]                 

def int2ip(addr):                                                               
    return socket.inet_ntoa(struct.pack("!I", addr))

def got_ptr(args, addr, level):
	(ans, auth, add) = args
	if level == 4:
		records = {}
		#print '\n', addr
		#print 'Additional:'
		for A in add:
			if A.type is dns.A:
				#print A.name, A.payload.dottedQuad()
				records[A.name.name] = A.payload.dottedQuad()
		#print 'Authoritative:'
		for NS in auth:
			if NS.type is dns.NS:
				if NS.payload.name.name not in records:
					records[NS.payload.name.name] = None
					#print NS.payload.name.name, "No IP"
		for name, ip in records.items():
			if ip:
				#print "INSERT INTO dns VALUES ('%s',%i)" % (name, ip2int(ip))
				c.execute("INSERT INTO dns VALUES ('%s',%i)" % (name, ip2int(ip)))
			else:
				#print "INSERT INTO dns VALUES ('%s', NULL)" % name
				c.execute("INSERT INTO dns VALUES ('%s', NULL)" % name)
			conn.commit()
			print 'Commit %s', ip
	else:
		lookup(postfix=addr, level=level + 1)

def no_ptr(*args):
	pass

def crypt_error(*args):
	print "crypt_error", args
	f = lambda addr: client.lookupPointer(addr).addCallback(got_ptr, addr, args[2]).addErrback(no_ptr)
	sem.run(f, args[1]).addErrback(crypt_error, args[1], args[2])
	print "end error"

def lookup(postfix=None, level=1):
	for octet in range(0,10):
		if postfix:
			addr = "%i.%s" % (octet, postfix)
		else:
			addr = "%i.in-addr.arpa" % octet

		f = lambda addr: client.lookupPointer(addr).addCallback(got_ptr, addr, level).addErrback(no_ptr)

		sem.run(f, addr).addErrback(crypt_error, addr, level)

lookup()
reactor.run()
