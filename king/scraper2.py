from twisted.internet import reactor, threads
from twisted.names import client, dns

concurrent = 2000
reactor.suggestThreadPoolSize(concurrent)

def processResponse(args, addr, level):
	if level == 4:
		print "Response", args, addr
	else:
		lookup(postfix=addr, level=level+1)

def processError(*args):
	pass

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
