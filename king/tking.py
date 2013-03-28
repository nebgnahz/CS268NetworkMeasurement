import exceptions, sys
from twisted.internet import reactor, defer
from twisted.names import dns as twisted_dns
from twisted.names import server
from datetime import datetime
from random import randrange
from threading import Thread
from time import sleep
from datetime import datetime
import dns.query, dns.rdatatype

myAddr = '219-243-208-60-planet3.nbapuns.com'
target1 = '8.8.8.8'
target2 = 'ns1.google.com'
target2_ip = '216.239.32.10'

start_time = None

class DNSServerFactory(server.DNSServerFactory):
    def handleQuery(self, message, protocol, address):
        print "Recieved Query"
        print address
        print message

        global start_time, query_id
        try:
            start_time = datetime.now()
            query = message.queries[0]
            target = query.name.name
            print target
            id, origin = target.split('.')[0:2]

            if int(id) != query_id:
                print "Query ID Doesn't Match"
                raise Exception

            NS = twisted_dns.RRHeader(name=target, type=twisted_dns.NS, cls=twisted_dns.IN, ttl=0, auth=True,
                             payload=twisted_dns.Record_NS(name=target2, ttl=0))
            A = twisted_dns.RRHeader(name=target2, type=twisted_dns.A, cls=twisted_dns.IN, ttl=0,
                            payload=twisted_dns.Record_A(address=target2_ip, ttl=None))

            ans = []
            auth = [NS]
            add = [A]
            args = (self, (ans, auth, add), protocol, message, address)

            return server.DNSServerFactory.gotResolverResponse(*args)
        except Exception, e:
            print "Bad Request", e

query_id = randrange(0, sys.maxint)

##########
# Server #
##########
factory = DNSServerFactory()
protocol = twisted_dns.DNSDatagramProtocol(factory)
reactor.listenUDP(53, protocol)
reactor.listenTCP(53, factory)

##########
# Client #
##########
def client():
    sleep(1)
    addr = "%i.%s" % (query_id, myAddr)
    query = dns.message.make_query(addr, dns.rdatatype.A)
    response = dns.query.udp(query, target1, timeout=5)
    end_time = datetime.now()
    print "Recieved Response:"
    print "Time: ", end_time - start_time
    print response
    reactor.callFromThread(reactor.stop)

t=Thread(target=client)
t.start()

reactor.run()
