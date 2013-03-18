import dns.query, dns.resolver
from dns.exception import DNSException
from multiprocessing import Process
from multiprocessing import JoinableQueue as Queue

ip_range = 10
concurrent = 500

default = dns.resolver.get_default_resolver()
ns = default.nameservers[0]

def ip2reverse(ip):
    ip = ip.split('.')
    ip.reverse()
    return '%s.in-addr.arpa' % '.'.join(ip)

def lookup(ip):
    addr = ip2reverse(ip)
    query = dns.message.make_query(addr, dns.rdatatype.PTR)
    response = dns.query.udp(query, ns)

    rcode = response.rcode()
    if rcode == dns.rcode.NOERROR:
        return response.authority, response.additional
    else:
        return None, None

def doWork():
    while True:
        ip, level = q.get()
        auth, add = lookup(ip)
        if auth is None and add is None:
            pass
        else:
            print auth, add
            if level < 4:
                for octet in range(0,ip_range):
                    ip = "%s.%i" % (ip, octet)
                    q.put((ip, level+1))
        q.task_done()

q=Queue(concurrent*2)

for i in range(concurrent):
    t=Process(target=doWork)
    t.daemon=True
    t.start()


for octet in range(0,ip_range):
    q.put((str(octet), 1))
q.join()
