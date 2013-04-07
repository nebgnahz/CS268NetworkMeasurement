import redis

dns_servers = redis.ConnectionPool(host='localhost', port=6379, db=0)
db_dns = redis.Redis(connection_pool=dns_servers)

all_keys = db_dns.keys()
for keys in	all_keys:
	print keys

