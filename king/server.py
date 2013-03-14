from twisted.internet import reactor
from twisted.names import dns, client, server
from io import BytesIO

class DNSServerFactory(server.DNSServerFactory):
	def handleQuery(self, message, protocol, address):
		query = message.queries[0]

		x = dns.RRHeader(name=query.name.name, type=dns.NS, cls=dns.IN, ttl=0, auth=False,
						 payload=dns.Record_NS(name='nbapuns.com', ttl=0))

		ans = [x]
		auth = []
		add = []
		args = (self, (ans, auth, add), protocol, message, address)

		return server.DNSServerFactory.gotResolverResponse(*args)

factory = DNSServerFactory()
protocol = dns.DNSDatagramProtocol(factory)

reactor.listenUDP(53, protocol)
reactor.listenTCP(53, factory)
reactor.run()
