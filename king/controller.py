import redis, string
from utilities import distance, threaded_map
from plumbum import SshMachine
from rpyc.utils.factory import ssh_connect

all_dns = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=0))
open_resolvers = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=1))
geoip = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=2))
pl_hosts = [line.split(' ')[0:4] for line in map(string.strip,open('pl-host-list-geo').readlines())]

class PlanetLabNode(object):
    def __init__(self, id, host, ip, lat, lon):
        self.id = id
        self.host = host
        self.ip = ip
        self.lat = float(lat)
        self.lon = float(lon)
        try:
            self.connectPL()
        except AssertionError, e:
            try:
                self.restartPL()
                self.connectPL()
            except Exception, e:
                self = None
        except Exception, e:
            self = None
        print 'Done %s %i' % (host, id)

    def connectPL(self):
        print 'Connecting to %s %i' % (self.host, self.id)
        rem = SshMachine(self.host, user='ucb_268_measure', keyfile='~/.ssh/id_rsa',
                         ssh_opts=["-o StrictHostKeyChecking no",
                                   "-o UserKnownHostsFile=/dev/null"])
        conn = ssh_connect(rem, 18861)
        assert conn.root.test() == 1, "%s: RPC Failure" % host
        self.conn = conn

    def restartPL(self):
        subprocess.call(["ssh", "-t", "-i", "~/.ssh/id_rsa", "-o StrictHostKeyChecking no",
                         "-o UserKnownHostsFile=/dev/null", "ucb_268_measure@%s" % host,
                         "sudo tking-server stop; sudo tking-server start;"],
                         stdout=FNULL, stderr=subprocess.STDOUT)

    def get_latency(target1, ip1, target2, ip2):
        return self.conn.root.get_latency(target1, ip1, target2, ip2)

    def get_k(target, ip):
        return self.conn.get_k(target, ip)

    def get_distance(lat, lon):
        return distance((self.lat, self.lon), (lat, lon))

pl_nodes = threaded_map(lambda x: PlanetLabNode(x[0], *x[1]), list(enumerate(pl_hosts)), timeout=10.0)

