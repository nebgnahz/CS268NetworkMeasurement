import argparse, dns.query, dns.resolver, psycopg2
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

conn = psycopg2.connect('dbname=dns password=test')
c = conn.cursor()
c.execute('''DROP TABLE dns;''')
c.execute('''CREATE TABLE dns (name TEXT, ip BIGINT);''')
conn.commit()

default = dns.resolver.get_default_resolver()
ns = default.nameservers[0]

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
            ips = ("%s.%i" % (prefix, octet) for octet in range(0,octet_range))
        else:
            ips = ("%i" % octet for octet in range(ip_start,ip_end))
        
        for ip in ips:
            auth, add = lookup(ip, level, arr, id)
            if auth is None and add is None:
                pass
            else:
                # print ip, auth, add
                processRecords(auth, add)
                if level < 4:
                    q.put((ip2int(ip), level+1))
        q.task_done()

def lookup(ip, level, arr, id):
    addr = ip2reverse(ip)
    query = dns.message.make_query(addr, dns.rdatatype.PTR)

    for i in range(5-level):
        try:
            response = dns.query.udp(query, ns, timeout=.5)
            arr[id] = time()
            rcode = response.rcode()
            if rcode == dns.rcode.NOERROR:
                return response.authority, response.additional
            else:
                return None, None
        except dns.exception.Timeout:
            pass
            #print >> stderr, 'Timeout, Count: %i, Level: %i' % (i, level)
        except dns.query.BadResponse:
            pass
            #print >> stderr, 'Bad Response, Count: %i, Level: %i' % (i, level)

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

def processRecords(auth, add):
    if auth == add == []:
        return
    else:
        pass
        #print addr, level, auth, add
    records = {}
    for A in add:
        if A.type is dns.A:
            records[A.name.name] = A.payload.dottedQuad()
    for NS in auth:
        if NS.type is dns.NS:
            if NS.payload.name.name not in records:
                records[NS.payload.name.name] = None
    try:
        insertDB(records)
    except e:
        print "DB Error", e

def insertDB(records):
    for name, ip in records.items():
        if ip:
            query = '''INSERT INTO dns (name, ip) SELECT '%s', %i WHERE NOT EXISTS (SELECT 1 FROM dns WHERE name = '%s' and ip IS NOT NULL);''' % (name, ip2int(ip), name)
        else:
            query = '''INSERT INTO dns (name, ip) SELECT '%s', NULL WHERE NOT EXISTS (SELECT 1 FROM dns WHERE name = '%s');''' % (name, name)
        #print name, ip
        c.execute(query)
    conn.commit()
