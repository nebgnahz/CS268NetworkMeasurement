import dns.query, dns.resolver
from dns.exception import DNSException
from multiprocessing import Process, JoinableQueue

ip_range = 10
concurrent = 100

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

def processToDo():
    while True:
        ip, level = todo.get()
        auth, add = lookup(ip)
        if not auth and not add:
            pass
        else:
            print auth, add
            if level < 4:
                completed.put((ip, level))

def processComplete():
    while True:
        ip, level = completed.get()
        for octet in range(0,ip_range):
            ip = "%s.%i" % (ip, octet)
            todo.put((ip, level+1))
        completed.task_done()
        todo.task_done()

todo=JoinableQueue(concurrent*2)
completed=JoinableQueue()

for i in range(concurrent/2):
    t=Process(target=processToDo)
    t.daemon=True
    t.start()
    c=Process(target=processComplete)
    c.daemon=True
    c.start()

for octet in range(0,ip_range):
    todo.put((str(octet), 1))
todo.join()
completed.join()