from twisted.internet import reactor, defer
from twisted.names import client

semaphore = defer.DeferredSemaphore(5)

def got_ptr(args, addr, level):
	semaphore.release()
	if level == 2:
		print addr, args
	else:
		lookup(postfix=addr, level=level + 1)

def no_ptr(*args):
	semaphore.release()
	pass

def lookup(postfix=None, level=1):
	for octet in range(0,256):
		if postfix:
			addr = "%i.%s" % (octet, postfix)
		else:
			addr = "%i.in-addr.arpa" % octet

		semaphore.acquire()
		client.lookupPointer(addr).addCallback(got_ptr, addr, level).addErrback(no_ptr)

lookup()
reactor.run()
