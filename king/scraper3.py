import argparse, dns.query, dns.resolver
from dns.exception import DNSException
from time import time
from sys import stderr

parser = argparse.ArgumentParser(description='Reverse DNS Scraper')
parser.add_argument('range', metavar='octet', type=int, nargs='+',
                   help='Specify first octet range')
parser.add_argument('--threading', action='store_true', help='Use threads instead of processes')
parser.add_argument('--debug', action='store_true', help='Launch interactive console on exception or forced exit')
arguments = parser.parse_args()

try:
    ip_start, ip_end = arguments.range
    print "IP Range: %i - %i" % (ip_start, ip_end)
    ip_end += 1
except:
    print >> stderr, 'Invalid Range'
    exit(1)

default = dns.resolver.get_default_resolver()
ns = default.nameservers[0]

concurrent = 500

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
    q.put((None, 1))
    q.join()
    end = max(arr)
    print "Total Time: %f seconds" % (end - start)

def doWork(arr, id):
    while True:
        try:
            prefix, level = q.get(timeout=1)
        except:
            continue

        if prefix:
            prefix = int2ip(prefix)
            ips = ("%s.%i" % (prefix, octet) for octet in range(0,256))
        else:
            ips = ("%i" % octet for octet in range(ip_start,ip_end))
        
        for ip in ips:
            auth, add = lookup(ip, level, arr, id)
            if auth is None and add is None:
                pass
            else:
                # print ip, auth, add
                if level < 4:
                    q.put((ip2int(ip), level+1))
        q.task_done()

def lookup(ip, level, arr, id):
    addr = ip2reverse(ip)
    query = dns.message.make_query(addr, dns.rdatatype.PTR)

    for i in range(5-level):
        try:
            response = dns.query.udp(query, ns, timeout=1)
            arr[id] = time()
            rcode = response.rcode()
            if rcode == dns.rcode.NOERROR:
                return response.authority, response.additional
            else:
                return None, None
        except dns.exception.Timeout:
            print >> stderr, 'Timeout, Count: %i, Level: %i' % (i, level)
        except dns.query.BadResponse:
            print >> stderr, 'Bad Response, Count: %i, Level: %i' % (i, level)

    return None, None

#############
# Utilities #
#############
def ip2int(addr):
    return tuple(addr.split('.'))

def int2ip(addr):
    return '.'.join(addr)

def ip2reverse(ip):
    ip = ip.split('.')
    ip.reverse()
    return '%s.in-addr.arpa' % '.'.join(ip)

try:
    main()
except KeyboardInterrupt:
    if arguments.debug:
        from IPython import embed
        embed()
