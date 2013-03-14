from twisted.internet import reactor
from twisted.names import dns, client, server

class DNSServerFactory(server.DNSServerFactory):
	def handleQuery(self, message, protocol, address):
		print message, protocol, address

factory = DNSServerFactory()
protocol = dns.DNSDatagramProtocol(factory)

reactor.listenUDP(53, protocol)
reactor.listenTCP(53, factory)
reactor.run()
