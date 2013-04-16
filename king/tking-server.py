#!/usr/bin/python
import exceptions, sys, os, socket, rpyc, pickle, cPickle
import dns.query, dns.rdatatype, dns.exception
from twisted.internet import reactor
from twisted.names import dns as twisted_dns
from twisted.names import server
from datetime import datetime, timedelta
from random import randrange
from threading import Thread
from time import sleep
from datetime import datetime
from rpyc.utils.server import ThreadedServer
from daemon import Daemon
from sysping import ping

myHostName = socket.gethostname().replace('.', '---')
myIP = socket.gethostbyname(socket.gethostname()).replace('.', '---')
myAddr = '%s---%s.nbapuns.com' % (myIP, myHostName)
outstandingQueries = {}
returnedQueries = {}
fullQueries = {}

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

    def exposed_exit(self):
        exit(0)

    def generate_query_id(self):
        query_id = randrange(0, sys.maxint)
        while query_id in outstandingQueries or query_id in returnedQueries:
            query_id = randrange(0, sys.maxint)
        return query_id

    def exposed_get_ping(self, t1, ip1):
        times = []
        random_int = randrange(0, sys.maxint)
        for i in range(6):
            addr = "%i.%s" % (random_int, t1)
            query = dns.message.make_query(addr, dns.rdatatype.A)
            start_time = datetime.now()
            try:
                response = dns.query.udp(query, ip1, timeout=5.0)
                end_time = datetime.now()
                times.append(end_time-start_time)
            except Exception, e:
                pass
        return times[1:] #Only take times after the first query, because the DNS server will have cached its response

    def exposed_get_latency(self, t1, ip1, t2, ip2):
        query_id = self.generate_query_id()
        outstandingQueries[query_id] = (t2, ip2)

        print 'QID1', query_id, type(query_id)

        # Start DNS Client
        end_time = dnsClientQuery(query_id, ip1)

        try:
            print '...1'
            start_time, address = returnedQueries[query_id]
            print '...2'
            del returnedQueries[query_id]
            print '...3'
            ping_time = self.exposed_get_ping(t1, ip1)
            print '...4'
            return cPickle.dumps((end_time, start_time, ping_time, address))
        except Exception, e:
            print "End error:", e
            return cPickle.dumps((None, None, None, None))

    def exposed_get_k(self, t1, ip1):
        query_id = self.generate_query_id()
        outstandingQueries[query_id] = (t1, ip1)

        dnsClientQuery(query_id, ip1, query_type="kvalue", timeout=20)
        try:
            k = returnedQueries[query_id]
            del returnedQueries[query_id]
            return k
        except Exception, e:
            print e
            return None

    def exposed_full_response(self, query_id, msg):
        fullQueries[query_id] = msg

    def exposed_full_test(self, t1, ip1, t2, ip2):
        query_id = self.generate_query_id()
        outstandingQueries[query_id] = (t2, ip2)
        dnsClientQuery(query_id, ip1, query_type="full")
        # Wait 10 seconds to get a response from the remote server
        sleep(10)
        try:
            return fullQueries[query_id]
        except Exception, e:
            print "Did Not Recieve RPC from Last Hop"
            return "Did Not Recieve RPC from Last Hop"

##########
# Client #
##########
def dnsClientQuery(query_id, target1_ip, query_type="latency", timeout=10):
    addr = "%s.%i.%s" % (query_type, query_id, myAddr)
    print addr
    query = dns.message.make_query(addr, dns.rdatatype.A)
    end_time = None
    try:
        response = dns.query.udp(query, target1_ip, timeout=timeout)
        end_time = datetime.now()
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.FormError):
        end_time = datetime.now()
    except Exception:
        pass
    return end_time

##############
# DNS Server #
##############
class DNSServerFactory(server.DNSServerFactory):
    def __init__(self, authorities=None, caches=None, clients=None, verbose=0):
        print 'Starting Server'
        server.DNSServerFactory.__init__(self)

    def handleQuery(self, message, protocol, address):
        query_time = datetime.now()
        print "Recieved Query"
        try:
            encoded_url, query_id, origin, query_type = self.processMessage(message)
            query_id = int(query_id)
            print encoded_url

            if query_type == 'kvalue':
                #print 'kv'
                if query_id not in returnedQueries:
                    returnedQueries[query_id] = 1
                else:
                    returnedQueries[query_id] += 1
                #print 'kv end'
            elif query_type == 'latency' or query_type == 'full':
                #print 'latency'
                returnedQueries[query_id] = (query_time, address)
                #print 'outstanding queries'
                print 'QID2', query_id, type(query_id)
                target2, target2_ip = outstandingQueries[query_id]
                del outstandingQueries[query_id]
                #print 'delete'
                response = self.createReferral(encoded_url, target2, target2_ip, protocol, message, address)
                #print 'latency end'
                return server.DNSServerFactory.gotResolverResponse(*response)
        except Exception, e:
            print "Bad Request", e
            return None

    def processMessage(self, message):
        query = message.queries[0]
        encoded_url = query.name.name
        query_type, query_id, origin = encoded_url.split('.')[0:3]
        return encoded_url, query_id, origin, query_type

    def createReferral(self, encoded_url, target2, target2_ip, protocol, message, address):
        NS = twisted_dns.RRHeader(name=encoded_url, type=twisted_dns.NS, cls=twisted_dns.IN, ttl=0, auth=True,
                         payload=twisted_dns.Record_NS(name=target2, ttl=0))
        A = twisted_dns.RRHeader(name=target2, type=twisted_dns.A, cls=twisted_dns.IN, ttl=0,
                        payload=twisted_dns.Record_A(address=target2_ip, ttl=None))

        ans = []
        auth = [NS]
        add = [A]
        return (self, (ans, auth, add), protocol, message, address)

def startDnsServer():
    # Setup DNS Server
    factory = DNSServerFactory()
    protocol = twisted_dns.DNSDatagramProtocol(factory)
    try:
        udp = reactor.listenUDP(53, protocol)
        tcp = reactor.listenTCP(53, factory)
        # Start DNS Server
        reactor.run()
    except:
        print 'Could Not Bind/Start Reactor'
        exit(1)
    udp.stopListening()
    tcp.stopListening()
    print "Reactor Stopped"


class TkingServerDaemon(Daemon):
    def run(self):
        # Start RPYC
        t = ThreadedServer(TurboKingService, hostname='localhost', port = 18861, protocol_config={'allow_pickle': True})
        dnsClient = Thread(target=t.start)
        dnsClient.daemon = True
        dnsClient.start()
        startDnsServer()


if __name__ == "__main__":
    daemon = TkingServerDaemon('/tmp/tking-daemon.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
            print 'Started Server'
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'normal' == sys.argv[1]:
            daemon.run()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
