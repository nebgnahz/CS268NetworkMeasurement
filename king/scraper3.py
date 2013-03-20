import argparse, dns.query, dns.resolver, dns.rdatatype, redis, socket, struct
from dns.exception import DNSException
from time import time
from sys import stderr

parser = argparse.ArgumentParser(description='Reverse DNS Scraper')
parser.add_argument('range', metavar='octet', type=int, nargs='+',
                   help='Specify first octet range')
parser.add_argument('--threading', action='store_true', help='Use threads instead of processes')
parser.add_argument('--debug', action='store_true', help='Launch interactive console on exception or forced exit')
parser.add_argument('--octet', type=int, action='store', default=256)
parser.add_argument('--concurrent', type=int, action='store', default=500)

arguments = parser.parse_args()

try:
    ip_start, ip_end = arguments.range
    octet_range = arguments.octet
    concurrent = arguments.concurrent
    print "IP Range: %i - %i" % (ip_start, ip_end)
    print "Octet Range: %i" % octet_range
    print "Concurrent: %i" % concurrent
    ip_end += 1
except Exception as e:
    print >> stderr, e
    exit(1)

try:
    import redis
    r_server = redis.Redis('localhost')
except:
    print >> stderr, 'Could not connect to Redis'

default = dns.resolver.get_default_resolver()
default.timeout = .5
default_ns = default.nameservers[0]

if arguments.threading:
    print 'Using Threading'
    from threading import Thread as Split
    from Queue import Queue
    from array import array as Array
else:
    print 'Using Multiprocessing'
    from multiprocessing import Process as Split
    from multiprocessing import JoinableQueue as Queue
    from multiprocessing import Array
q = Queue()

def main():
    start = time()
    if arguments.threading:
        arr = Array('d', (0,)*concurrent)
    else:
        arr = Array('d', concurrent, lock=False)
    for i in range(concurrent):
        t=Split(target=doWork, args=(arr, i))
        t.daemon=True
        t.start()
    q.put((None, 1, default_ns))
    q.join()
    end = max(arr)
    print "Total Time: %f seconds" % (end - start)

def doWork(arr, id):
    while True:
        try:
            prefix, level, ns = q.get(timeout=1)
        except:
            continue

        if prefix:
            prefix = tuple2ip(prefix)
            ips = ("%s.%i" % (prefix, octet) for octet in range(0,octet_range))
        else:
            ips = ("%i" % octet for octet in range(ip_start,ip_end))
        
        for ip in ips:
            addr, auth, add = lookup(ip, ns, level, arr, id)
            if not auth and not add:
                pass
            else:
                next_ns_name = processRecords(auth, add)
                if level < 3:
                    next_ns = lookupHost(next_ns_name, level)
                    if next_ns:
                        q.put((ip2tuple(ip), level+1, next_ns))
        q.task_done()

def lookupHost(host, level):
    if host:
        for i in range(5-level):
            try:
                return default.query(host).rrset[0].address
            except dns.exception.Timeout:
                print >> stderr, host, 'Timeout'
            except dns.resolver.NXDOMAIN:
                print >> stderr, host, 'NXDOMAIN'
            except dns.resolver.NoAnswer:
                print >> stderr, host, 'NoAnswer'
            except dns.resolver.NoNameservers:
                print >> stderr, host, 'NoNameservers'
            except Exception:
                print >> stderr, host, 'Unknown Error'
    return None

def lookup(ip, ns, level, arr, id):
    addr = ip2reverse(ip)
    query = dns.message.make_query(addr, dns.rdatatype.PTR)
    for i in range(5-level):
        try:
            response = dns.query.udp(query, ns, timeout=.5)
            arr[id] = time()
            rcode = response.rcode()
            if rcode == dns.rcode.NOERROR:
                return addr, response.authority, response.additional
            else:
                return addr, None, None
        except dns.exception.Timeout:
            print >> stderr, 'Timeout, Count: %i, Level: %i' % (i, level)
        except dns.query.BadResponse:
            print >> stderr, 'Bad Response, Count: %i, Level: %i' % (i, level)
        except dns.query.UnexpectedSource:
            print >> stderr, 'Unexpected Source, Count: %i, Level: %i' % (i, level)
        except Exception:
            print >> stderr, 'Unknown Error, Count: %i, Level: %i' % (i, level)
    return addr, None, None

#############
# Utilities #
#############
def ip2tuple(addr):
    return tuple(addr.split('.'))

def tuple2ip(addr):
    return '.'.join(addr)

def ip2int(addr):
    return struct.unpack("!L", socket.inet_aton(addr))[0]

def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!L", addr))

def ip2reverse(ip):
    ip = ip.split('.')
    ip.reverse()
    return '%s.in-addr.arpa' % '.'.join(ip)

def processRecords(auth, add):
    records = {}
    ret = None
    for rrset in auth:
        for rec in rrset:
            if rec.rdtype is dns.rdatatype.NS:
                records[str(rec).lower()] = None
            if rec.rdtype is dns.rdatatype.SOA:
                ret = rec.mname
    for rrset in add:
        name = rrset.name.to_text().lower()
        for rec in rrset:
            if rec.rdtype is dns.rdatatype.A:
                records[name] = rec.to_text()
                #assert int2ip(ip2int(rec.to_text())) == rec.to_text()
    if records:
        try:
            insertDB(records)
        except Exception as e:
            print "DB Error", e
            print records

    return ret

def insertDB(records):
    pipe = r_server.pipeline()
    for name, ip in records.items():
        if ip:
            pipe.sadd(ip, name)
        else:
            pipe.sadd('', name)
    if not pipe.execute():
        raise Exception

try:
    main()
except KeyboardInterrupt:
    if arguments.debug:
        from IPython import embed
        embed()
