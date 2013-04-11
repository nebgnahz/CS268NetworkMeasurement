#!/usr/bin/python
import exceptions, sys, os, socket, rpyc, pickle
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
from pyping import ping

myHostName = socket.gethostname().replace('.', '---')
myIP = socket.gethostbyname(socket.gethostname()).replace('.', '---')
myAddr = '%s---%s.nbapuns.com' % (myIP, myHostName)
outstandingQueries = {}
returnedQueries = {}

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

    def exposed_get_ping(self, ip1):
        ping_response = ping(ip1)
        avg_ping_rtt = ping_response.avg_rtt
        mil, mic = avg_ping_rtt.split('.')
        mil = int(mil)
        mic = int(mic)
        ping_time = timedelta(milliseconds = mil, microseconds=mic)
        return ping_time

    def exposed_get_latency(self, t1, ip1, t2, ip2):
        query_id = self.generate_query_id()
        outstandingQueries[query_id] = (t2, ip2)

        # Start DNS Client
        end_time = dnsClient(query_id, ip1)

        try:
            start_time, address = returnedQueries[query_id]
            del returnedQueries[query_id]
            ping_time = self.exposed_get_ping(ip1)
            return end_time, start_time, ping_time, address
        except Exception, e:
            print e
            return None, None, None, None

    def exposed_get_k(self, t1, ip1):
        query_id = self.generate_query_id()
        outstandingQueries[query_id] = (t1, ip1)

        dnsClient(query_id, ip1, query_type="kvalue", timeout=20)
        try:
            k = returnedQueries[query_id]
            del returnedQueries[query_id]
            return k
        except Exception, e:
            print e
            return None

##########
# Client #
##########
def dnsClient(query_id, target1_ip, query_type="latency", timeout=5):
    addr = "%s.%i.%s" % (query_type, query_id, myAddr)
    print addr
    query = dns.message.make_query(addr, dns.rdatatype.A)
    try:
        response = dns.query.udp(query, target1_ip, timeout=timeout)
        end_time = datetime.now()
        print "Recieved Response:", response
    except dns.exception.Timeout, e:
        end_time = None
        print "Error:", e
    return end_time

##############
# DNS Server #
##############
class DNSServerFactory(server.DNSServerFactory):
    def handleQuery(self, message, protocol, address):
        query_time = datetime.now()
        print "Recieved Query", address, message
        try:
            encoded_url, query_id, origin, query_type = processMessage(message)
            print encoded_url

            if query_type is 'kvalue':
                if query_id not in returnedQueries:
                    returnedQueries[query_id] = 1
                else:
                    returnedQueries[query_id] += 1
            elif query_type is 'latency':
                returnedQueries[query_id] = (query_time, address)
                target2, target2_ip = outstandingQueries[query_id]
                del outstandingQueries[query_id]

                response = createReferral(encoded_url, target2, target2_ip)
                return server.DNSServerFactory.gotResolverResponse(*response)
        except Exception, e:
            print "Bad Request", e
            return None

    def processMessage(self, message):
        query = message.queries[0]
        encoded_url = query.name.name
        query_type, query_id, origin = encoded_url.split('.')[0:3]
        return encoded_url, query_id, origin, query_type

    def createReferral(self, encoded_url, target2, target2_ip):
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
    udp = reactor.listenUDP(53, protocol)
    tcp = reactor.listenTCP(53, factory)
    # Start DNS Server
    reactor.run()
    udp.stopListening()
    tcp.stopListening()
    print "Reactor Stopped"


class TkingServerDaemon(Daemon):
    def run(self):
        # Start RPYC
        t = ThreadedServer(TurboKingService, hostname='localhost', port = 18861)
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
