import time
from twisted.internet import reactor, defer
from twisted.names import dns, client, server

target1 = '8.8.8.8'
target2 = 'google.com'

def queryResponse(args):
    end_time = time.time()
    answer, authority, additional = args
    reactor.stop()

class DNSServerFactory(server.DNSServerFactory):
    def handleQuery(self, message, protocol, address):
        try:
            query = message.queries[0]
            target = query.name.name
            origin = target.split('.')[0]
            origin = origin.split('-')

            origin_ns = origin[-1]
            origin_ns_name = "%s.nbappuns.com" % origin_ns
            origin_ip = '.'.join(origin[:4])

            NS = dns.RRHeader(name=target, type=dns.NS, cls=dns.IN, ttl=0, auth=True,
                             payload=dns.Record_NS(name=origin_ns_name, ttl=0))
            A = dns.RRHeader(name=origin_ns_name, type=dns.A, cls=dns.IN, ttl=0,
                            payload=dns.Record_A(address=origin_ip, ttl=None))

            ans = []
            auth = [NS]
            add = [A]
            args = (self, (ans, auth, add), protocol, message, address)

            return server.DNSServerFactory.gotResolverResponse(*args)
        except Exception:
            print "Bad Request"

##########
# Server #
##########
factory = DNSServerFactory()
protocol = dns.DNSDatagramProtocol(factory)
reactor.listenUDP(53, protocol)
reactor.listenTCP(53, factory)

##########
# Client #
##########
resolver = client.createResolver([target1, 53])
resolver.lookupAddress(target2, timeout=[1,2,3]).addCallback(queryResponse, args)
start_time = time.time()

reactor.run()
