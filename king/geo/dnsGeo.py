# run redis-server redis-backup/redis.conf
# in redis.conf, it now specifies open.rdb as the database file
# redis now has two databases, in redis-cli, you can do select 0/1 to choose between them
# select 0 will come with the DB that is a copy of 236.db
# select 1 will come with the DB of open resolvers
# select 2 will come with the GeoIP from MaxMind

# HIGHLIGHT:
#   FIRST!!!
#   run python redisKeyDump.py > redis-backups/236keys.txt
# all keys are from [0:236733]

import argparse, redis, socket, struct, sqlite3
from sys import stderr

parser = argparse.ArgumentParser(description='DNS GeoLocation')
parser.add_argument('range', metavar='octet', type=int, nargs='+', help='Specify the range of keys in redis [0:236733]')
parser.add_argument('--debug', default=False, action='store_true', help='Print More Errors and Launch interactive console on exception or forced exit')
parser.add_argument('--db', type=bool, action='store', default=False)

arguments = parser.parse_args()

filename = "./redis-backups/236keys.txt"

try:
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
	conn = sqlite3.connect('GeoIP.db')
	conn.text_factory = str
	c = conn.cursor()
	if db:
		dnsGeo = redis.ConnectionPool(host='localhost', port=6379, db=2)
		dbDNSGeo = redis.Redis(connection_pool=dnsGeo)
except:
	print >> stderr, 'Could not connect to Redis'

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
					query(key, ip, i)

def query(key, ip, i):
	ip_int = ip2int(ip)
	results = c.execute('''select city, latitude, longitude from GeoCityLocation where locId = (select locId from GeoCityBlocks where startIpNum <= %i and endIpNum >= %i);''' % (ip_int, ip_int))
	for row in results:
		city, latitude, longitude = row
		print "[%i] %s, %s\n  %s (%.2f, %.2f)" % (i, key, ip, city, latitude, longitude)
		if db:
			try:
				dbDNSGeo.sadd(key, (city, latitude, longitude))
			except Exception as e:
				print "\tRedis Error", e

def ip2int(ip):
	return int(socket.inet_aton(ip).encode('hex'),16)


try:
	main(key_start, key_end)
	
except KeyboardInterrupt:
	if arguments.debug:
		from IPython import embed
		embed()
