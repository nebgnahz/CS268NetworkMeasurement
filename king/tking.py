import exceptions, sys
from twisted.internet import reactor, defer
from twisted.names import dns, client, server
from datetime import datetime
from random import randrange

myAddr = '169-229-50-3-planet1.nbapuns.com'
target1 = '8.8.8.8'
target2 = 'ns1.google.com'

start_time = None
end_time = None

def queryResponse(args):
    try:
        global end_time
        end_time = datetime.now()
        answer, authority, additional = args
        print end_time - start_time
    except exceptions.TypeError:
        print "Sever Thread Never Recieved Query"
    reactor.stop()

def error(args):
    print args

class DNSServerFactory(server.DNSServerFactory):
    def handleQuery(self, message, protocol, address):
        global start_time, query_id
        try:
            start_time = datetime.now()
            query = message.queries[0]
            target = query.name.name
            id, origin = target.split('.')[0:2]

            if id != query_id:
                raise Exception

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

query_id = randrange(0, sys.maxint)

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
resolver = client.createResolver([(target1, 53)])
lookup = "%s.%i.%s" % ('dummy', query_id, myAddr)
resolver.lookupAddress(lookup, timeout=[1,2,3]).addCallback(queryResponse).addErrback(error)

reactor.run()
