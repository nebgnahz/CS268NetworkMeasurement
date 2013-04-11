from twisted.internet import reactor
from twisted.names import dns, client, server
from rpyc.utils.factory import ssh_connect
from plumbum import SshMachine

class DNSServerFactory(server.DNSServerFactory):
    def handleQuery(self, message, protocol, address):
        try:
            query = message.queries[0]
            target = query.name.name
            print 'Target:', target

            query_type = target.split('.')[0]
            if query_type == 'ns1':
                A = dns.RRHeader(name=target, type=dns.A, cls=dns.IN, ttl=0,
                                payload=dns.Record_A(address='54.244.114.147', ttl=None))
                args = (self, ([A], [], []), protocol, message, address)
                return server.DNSServerFactory.gotResolverResponse(*args)
            elif query_type == 'ns2':
                A = dns.RRHeader(name=target, type=dns.A, cls=dns.IN, ttl=0,
                                payload=dns.Record_A(address='54.244.114.167', ttl=None))
                args = (self, ([A], [], []), protocol, message, address)
                return server.DNSServerFactory.gotResolverResponse(*args)
            elif query_type == 'full':
                origin = target.split('.')[3].split('---')
                origin_ns_name = '.'.join(origin[4:])
                origin_ip = '.'.join(origin[:4])
                target = '.'.join(target.split('.')[3:])
                node_ip = '.'.join(target.split('.')[1].split('---'))
                print 'Full', query_type, origin_ip, origin_ns_name, node_ip
            else:
                origin = target.split('.')[2].split('---')
                origin_ns_name = '.'.join(origin[4:])
                origin_ip = '.'.join(origin[:4])
                target = '.'.join(target.split('.')[2:])
                print query_type, origin_ip, origin_ns_name

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
