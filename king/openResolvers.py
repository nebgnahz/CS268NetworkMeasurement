# run redis-server redis-backup/redis.conf
# in redis.conf, it now specifies open.rdb as the database file
# redis now has two databases, in redis-cli, you can do select 0/1 to choose between them
# select 0 will come with the DB that is a copy of 236.db
# select 1 will come with the DB of open resolvers

# question: Do I need multi-threading?
# answer: tentatively, no!

# test the consistency of each time's query [Done]
# just run and print the results of keys, 'diff' gives no output

# HIGHLIGHT:
#   FIRST!!!
#   run python redisKeyDump.py > redis-backups/236keys.txt
# all keys are from [0:236733]


import argparse, time
import dns.query, dns.resolver, dns.rdatatype, redis, socket, struct
from sys import stderr

parser = argparse.ArgumentParser(description='Open DNS Resolvers')
parser.add_argument('range', metavar='octet', type=int, nargs='+',
                   help='Specify the range of keys in redis [0:236733]')
parser.add_argument('--debug', default=False, action='store_true', help='Print More Errors and Launch interactive console on exception or forced exit')
parser.add_argument('--concurrent', type=int, action='store', default=10)
parser.add_argument('--db', type=bool, action='store', default=False)
parser.add_argument('--timeout', type=float, action='store', default=3)

arguments = parser.parse_args()

timeout_count = 0
count_threshold = 2

filename = "./redis-backups/236keys.txt"

try:
	concurrent = arguments.concurrent
	debug = arguments.debug
	db = arguments.db
	if db:
		print "writing to redis db"		
	key_start, key_end = arguments.range
except Exception as e:
	print >> stderr, e
	exit(1)

try:
	dns_servers = redis.ConnectionPool(host='localhost', port=6379, db=0)
	db_dns = redis.Redis(connection_pool=dns_servers)
	if db:
		open_resolvers = redis.ConnectionPool(host='localhost', port=6379, db=1)
		db_open = redis.Redis(connection_pool=open_resolvers)
except:
	print >> stderr, 'Could not connect to Redis'

default = dns.resolver.get_default_resolver()
default.timeout = arguments.timeout
default_ns = default.nameservers[0]

def main(key_start, key_end):
	try:
		key_file = open(filename, 'r')
	except:
		print "[ERROR]: key file not found. \n  run python redisKeyDump.py > redis-backups/236keys.txt"
		return
	
	if key_start < 0:
		key_start = 0
	if key_end > 236733-1:
		key_end = 236733-1
	print "range:", key_start, key_end
	for i, line in enumerate(key_file):
		if i < key_start  or i > key_end:
			continue
		key = line.rstrip('\n')
		ip_set = db_dns.smembers(key)
		if ip_set == set():
			# empty set, we need to look it up
			# ip = socket.gethostbyname(key)
			# didn't handle those without ip for now
			print key
		else:
			for ip in ip_set:
				if ip is not '':
					print "[%i] %s, %s, %s" % (i, key, ip, ip2openResolvers(ip))
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
			if db:
				try:
					db_open.sadd(key, ip)
				except Exception as e:
					print "\tDB Error", e

		elif rcode == dns.rcode.NXDOMAIN:
			print "\tFalse"
			return False

	except dns.exception.Timeout:
		print "Timeout"
		global timeout_count, count_threshold
		timeout_count += 1
		if timeout_count > count_threshold:
			print "# sleep for 10 seconds", timeout_count
			timeout_count = 0
			time.sleep(10)
		if debug: print >> stderr, '\tTimeout, ip: %s' % (ip)
	except dns.query.BadResponse:
		print "Bad Response"
		if debug: print >> stderr, '\tBad Response, ip: %s' % (ip)
	except dns.query.UnexpectedSource:
		print "Unexpected Source"
		if debug: print >> stderr, '\tUnexpected Source, ip: %s' % (ip)
	except Exception:
		print "Unknown Error"
		print >> stderr, '\tUnknown Error, ip: %s' % (ip)

def ip2openResolvers(ip):
	ip = ip.split('.')
	ip.reverse()
	return '%s.dnsbl.openresolvers.org' % '.'.join(ip)


try:
	main(key_start, key_end)
	
except KeyboardInterrupt:
	if arguments.debug:
		from IPython import embed
		embed()
