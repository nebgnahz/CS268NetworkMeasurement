import redis

all_dns_connection = redis.ConnectionPool(host='localhost', port=6379, db=0)
open_resolvers_connection = redis.ConnectionPool(host='localhost', port=6379, db=1)
geoip_connection = redis.ConnectionPool(host='localhost', port=6379, db=2)

all_dns = redis.Redis(connection_pool=all_dns_connection)
open_resolvers = redis.Redis(connection_pool=open_resolvers_connection)
geoip = redis.Redis(connection_pool=geoip_connection)
pl_hosts = map(string.strip,open('pl-host-list').readlines())


class PlanetLabNode(object):
    def __init__(self, host):
        self.host = host
        try:
            self.conn = self.connectPL()
        except AssertionError, e:
            self.restartPL()
            self.conn = self.connectPL()

    def connectPL(self):
        rem = SshMachine(host, user='ucb_268_measure', keyfile='~/.ssh/id_rsa',
                         ssh_opts=["-o StrictHostKeyChecking no",
                                   "-o UserKnownHostsFile=/dev/null"])
        conn = ssh_connect(rem, 18861)
        assert conn.root.test() == 1, "%s: RPC Failure" % host
        return conn

    def restartPL(self):
        subprocess.call(["ssh", "-t", "-i", "~/.ssh/id_rsa", "-o StrictHostKeyChecking no",
                         "-o UserKnownHostsFile=/dev/null", "ucb_268_measure@%s" % host,
                         "sudo tking-server stop; sudo tking-server start;"],
                         stdout=FNULL, stderr=subprocess.STDOUT)

    def get_latency(target1, ip1, target2, ip2):
        return self.conn.root.exposed_get_latency(target1, ip1, target2, ip2)

    def get_k(target, ip):
        return self.conn.exposed_get_k(target, ip)

