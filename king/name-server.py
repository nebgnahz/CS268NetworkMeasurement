from twisted.internet import reactor
from twisted.names import dns, client, server

class DNSServerFactory(server.DNSServerFactory):
    def handleQuery(self, message, protocol, address):
        try:
            query = message.queries[0]
            target = query.name.name
            print 'Target:', target

            origin = target.split('.')[2].split('---')
            origin_ns_name = '.'.join(origin[4:])
            origin_ip = '.'.join(origin[:4])
            target = '.'.join(target.split('.')[2:])

            print target, origin_ip, origin_ns_name

            NS = dns.RRHeader(name=target, type=dns.NS, cls=dns.IN, ttl=0, auth=True,
                             payload=dns.Record_NS(name=origin_ns_name, ttl=0))
            A = dns.RRHeader(name=origin_ns_name, type=dns.A, cls=dns.IN, ttl=0,
                            payload=dns.Record_A(address=origin_ip, ttl=None))

            ans = []
            auth = [NS]
            add = [A]
            args = (self, (ans, auth, add), protocol, message, address)

            return server.DNSServerFactory.gotResolverResponse(*args)
        except Exception, e:
            print "Bad Request", e

factory = DNSServerFactory()
protocol = dns.DNSDatagramProtocol(factory)

reactor.listenUDP(53, protocol)
reactor.listenTCP(53, factory)
reactor.run()
