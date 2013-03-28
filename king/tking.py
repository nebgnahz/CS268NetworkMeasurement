import exceptions, sys
from twisted.internet import reactor, defer
from twisted.names import dns, server
from datetime import datetime
from random import randrange
from threading import Thread
from time import sleep
import dns as pydns

myAddr = '219-243-208-60-planet3.nbapuns.com'
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
def client():
    sleep(1)
    addr = "%s.%i.%s" % ('dummy', query_id, myAddr)
    query = pydns.message.make_query(addr, dns.rdatatype.A)
    response = pydns.query.udp(query, target1, timeout=5)
    print response

t=Thread(target=client)
t.start()

reactor.run()
