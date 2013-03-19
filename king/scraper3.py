import dns.query, dns.resolver
from dns.exception import DNSException
from multiprocessing import Process, JoinableQueue, Array
from time import time

ip_range = 10
concurrent = 500
default = dns.resolver.get_default_resolver()
ns = default.nameservers[0]
q = JoinableQueue()

def main():
    start = time()
    arr = Array('d', concurrent, lock=False)
    for i in range(concurrent):
        t=Process(target=doWork, args=(arr, i))
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
            ips = ("%s.%i" % (prefix, octet) for octet in range(0,ip_range))
        else:
            ips = ("%i" % octet for octet in range(0,ip_range))
        
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
            print 'Timeout, Count: %i, Level: %i' % (i, level)
        except dns.query.BadResponse:
            print 'Bad Response, Count: %i, Level: %i' % (i, level)

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
    from IPython import embed
    embed()
