from twisted.internet import reactor, defer
from twisted.names import client

def got_ptr(*args):
	print "Good", args

def no_ptr(*args):
	print "Bad", args

def lookup(postfix=None):
	for octet in range(0,256):
		if postfix:
			addr = "%i.%s" % (octet, postfix)
		else:
			addr = "%i.in-addr.arpa" % octet

		d = client.lookupPointer(addr).addCallback(got_ptr,addr).addErrback(no_ptr, addr)

lookup()
reactor.run()
