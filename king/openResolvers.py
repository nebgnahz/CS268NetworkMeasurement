# run redis-server redis-backup/redis.conf
# in redis.conf, it now specifies open.rdb as the database file
# redis now has two databases, in redis-cli, you can do select 0/1 to choose between them
# select 0 will come with the DB that is a copy of 236.db
# select 1 will come with the DB of open resolvers



# question: Do I need multi-threading?
# answer: tentatively, no!


import argparse
from sys import stderr
import argparse, dns.query, dns.resolver, dns.rdatatype, redis, socket, struct

# print 'Using Threading'
from threading import Thread as Split
from Queue import Queue
from array import array as Array

parser = argparse.ArgumentParser(description='Open DNS Resolvers')
parser.add_argument('--debug', default=False, action='store_true', help='Print More Errors and Launch interactive console on exception or forced exit')
parser.add_argument('--concurrent', type=int, action='store', default=500)
parser.add_argument('--timeout', type=float, action='store', default=1)

arguments = parser.parse_args()
concurrent = arguments.concurrent
debug = arguments.debug

try:
	dns_servers = redis.ConnectionPool(host='localhost', port=6379, db=0)
	open_resolvers = redis.ConnectionPool(host='localhost', port=6379, db=1)
	db_dns = redis.Redis(connection_pool=dns_servers)
	db_open = redis.Redis(connection_pool=open_resolvers)
except:
	print >> stderr, 'Could not connect to Redis'

q = Queue()

default = dns.resolver.get_default_resolver()
default.timeout = arguments.timeout
default_ns = default.nameservers[0]

def main():
	count = 0
	all_keys = db_dns.keys()
	for key in all_keys:
		ip_set = db_dns.smembers(key)
		if ip_set == set():
			# empty set, we need to look it up
			# ip = socket.gethostbyname(key)
			print key
			
		if len(ip_set) > 1:
			# print "multiple IPs", key, ip_set
			for ip in ip_set:
				if ip is not '':
					count += 1
					print "[%i] %s, %s, %s" % (count, key, ip, ip2openResolvers(ip))
					query(key, ip)


def query(key, ip):
	addr = ip2openResolvers(ip)
	query = dns.message.make_query(addr, dns.rdatatype.A)
	try:
		response = dns.query.udp(query, default_ns, timeout=arguments.timeout)
		rcode = response.rcode()

		if rcode == dns.rcode.NOERROR:
			# insert into another database
			print "\tTrue"
			try:
				db_open.sadd(key, ip)
			except Exception as e:
				print "\tDB Error", e

		elif rcode == dns.rcode.NXDOMAIN:
			print "\tFalse"
			return False

	except dns.exception.Timeout:
		if debug: print >> stderr, '\tTimeout, ip: %s' % (ip)
	except dns.query.BadResponse:
		if debug: print >> stderr, '\tBad Response, ip: %s' % (ip)
	except dns.query.UnexpectedSource:
		if debug: print >> stderr, '\tUnexpected Source, ip: %s' % (ip)
	except Exception:
		print >> stderr, '\tUnknown Error, ip: %s' % (ip)

def ip2openResolvers(ip):
	ip = ip.split('.')
	ip.reverse()
	return '%s.dnsbl.openresolvers.org' % '.'.join(ip)


try:
	main()
	count = 0
	
except KeyboardInterrupt:
	if arguments.debug:
		from IPython import embed
		embed()
