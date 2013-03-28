import exceptions, sys
from twisted.internet import reactor, defer
from twisted.names import dns as twisted_dns
from twisted.names import server
from datetime import datetime
from random import randrange
from threading import Thread
from time import sleep
from datetime import datetime
import dns.query, dns.rdatatype, dns.exception
import socket
import rpyc

myHostName = socket.gethostname().replace('.', '-')
myIP = socket.gethostbyname(socket.gethostname()).replace('.', '-')
myAddr = '%s-%s.nbapuns.com' % (myIP, myHostName)


# target1 = '8.8.8.8'
# target2 = 'ns1.google.com'
# target2_ip = '216.239.32.10'

###############
# RPC Service #
###############
class TurboKingService(rpyc.Service):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def exposed_test(self):
        return 1

    def exposed_get_latency(self, t1, ip1, t2, ip2):
        query_id = randrange(0, sys.maxint)
        
        # Setup DNS Server
        factory = DNSServerFactory(query_id, t2, ip2)
        protocol = twisted_dns.DNSDatagramProtocol(factory)
        reactor.listenUDP(53, protocol)
        reactor.listenTCP(53, factory)

        # Start DNS Client
        t=DNSClient(query_id, t1, ip1)
        t.start()

        # Start DNS Server
        reactor.run(installSignalHandlers=0)

        if factory.start_time:
            return t.end_time - factory.start_time
        else:
            return None

##########
# Client #
##########
class DNSClient(Thread):
    def __init__(self, query_id, target1, target1_ip):
        Thread.__init__(self)
        self.query_id = query_id
        self.target1 = target1
        self.target1_ip = target1_ip
        self.end_time = None

    def run(self):
        sleep(1) # Wait for DNS Server to Start
        addr = "final.%i.%s" % (self.query_id, myAddr)
        query = dns.message.make_query(addr, dns.rdatatype.A)
        try:
            response = dns.query.udp(query, self.target1_ip, timeout=5)
            self.end_time = datetime.now()
            print "Recieved Response:"
            print response
        except dns.exception.Timeout, e:
            print e
        reactor.callFromThread(reactor.stop)
        print "Stopped Reactor"


##############
# DNS Server #
##############
class DNSServerFactory(server.DNSServerFactory):
    def __init__(self, query_id, t2, ip2, authorities=None, caches=None, clients=None, verbose=0):
        server.DNSServerFactory.__init__(self,authorities,caches,clients,verbose)
        self.query_id = query_id
        self.target2 = t2
        self.target2_ip = ip2
        self.start_time = None

    #TODO: Stop Handling of Queries after seeing a valid one
    def handleQuery(self, message, protocol, address):
        print "Recieved Query"
        print address
        print message

        global start_time, query_id
        try:
            query = message.queries[0]
            target = query.name.name
            print target
            dummy, id, origin = target.split('.')[0:3]

            if int(id) != self.query_id:
                print "Query ID Doesn't Match"
                raise Exception
            else:
                self.start_time = datetime.now()

            NS = twisted_dns.RRHeader(name=target, type=twisted_dns.NS, cls=twisted_dns.IN, ttl=0, auth=True,
                             payload=twisted_dns.Record_NS(name=self.target2, ttl=0))
            A = twisted_dns.RRHeader(name=self.target2, type=twisted_dns.A, cls=twisted_dns.IN, ttl=0,
                            payload=twisted_dns.Record_A(address=self.target2_ip, ttl=None))

            ans = []
            auth = [NS]
            add = [A]
            args = (self, (ans, auth, add), protocol, message, address)

            return server.DNSServerFactory.gotResolverResponse(*args)
        except Exception, e:
            print "Bad Request", e

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(TurboKingService, port = 18861)
    t.start()
