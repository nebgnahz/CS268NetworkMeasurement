from twisted.internet import reactor
from twisted.names import dns, client, server

class DNSServerFactory(server.DNSServerFactory):
    def handleQuery(self, message, protocol, address):
        query = message.queries[0]

        print query.name.name
        NS = dns.RRHeader(name=query.name.name, type=dns.NS, cls=dns.IN, ttl=0, auth=True,
                         payload=dns.Record_NS(name='ns1.nbapuns.com', ttl=0))
        A = dns.RRHeader(name='ns1.nbapuns.com', type=dns.A, cls=dns.IN, ttl=0,
                        payload=dns.Record_A(address='127.0.0.1', ttl=None))

        ans = []
        auth = [NS]
        add = [A]
        args = (self, (ans, auth, add), protocol, message, address)

        return server.DNSServerFactory.gotResolverResponse(*args)

factory = DNSServerFactory()
protocol = dns.DNSDatagramProtocol(factory)

reactor.listenUDP(53, protocol)
reactor.listenTCP(53, factory)
reactor.run()
