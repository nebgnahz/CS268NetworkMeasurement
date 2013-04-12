import redis

all_dns_connection = redis.ConnectionPool(host='localhost', port=6379, db=0)
open_resolvers_connection = redis.ConnectionPool(host='localhost', port=6379, db=1)
geoip_connection = redis.ConnectionPool(host='localhost', port=6379, db=2)

all_dns = redis.Redis(connection_pool=all_dns_connection)
open_resolvers = redis.Redis(connection_pool=open_resolvers_connection)
geoip = redis.Redis(connection_pool=geoip_connection)
pl_hosts = map(string.strip,open('pl-host-list').readlines())

