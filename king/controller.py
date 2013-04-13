import apscheduler, redis, string
from multiprocessing import Pool
from plumbum import SshMachine
from rpyc.utils.factory import ssh_connect
from utilities import distance, threaded_map

process_pool_size = 60

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
        self.connected = False

    def connect(self):
        try:
            self.connectPL()
        except AssertionError, e:
            try:
                self.restartPL()
                self.connectPL()
            except Exception, e:
                self.connected = False
        except Exception, e:
            self.connected = False

    def connectPL(self):
        #print 'Connecting to %s %i' % (self.host, self.id)
        rem = SshMachine(self.host, user='ucb_268_measure', keyfile='~/.ssh/id_rsa',
                         ssh_opts=["-o StrictHostKeyChecking no",
                                   "-o UserKnownHostsFile=/dev/null"])
        conn = ssh_connect(rem, 18861)
        assert conn.root.test() == 1, "%s: RPC Failure" % host
        self.conn = conn
        self.connected = True

    def restartPL(self):
        subprocess.call(["ssh", "-t", "-i", "~/.ssh/id_rsa", "-o StrictHostKeyChecking no",
                         "-o UserKnownHostsFile=/dev/null", "ucb_268_measure@%s" % host,
                         "sudo tking-server stop; sudo tking-server start;"],
                         stdout=FNULL, stderr=subprocess.STDOUT)

    def handleConnExceptions(fn):
        def wrapped(self, *args, **kwargs):
            if not self.connected:
                self.connect()

            if self.connected:
                try:
                    return fn(self, *args, **kwargs)
                except Exception, e:
                    self.connected = False
                    try:
                        self.connect()
                        return fn(self, *args, **kwargs)
                    except Exception, e:
                        self.connected = False
                        return None
            else:
                return None
        return wrapped

    @handleConnExceptions
    def get_latency(self, target1, ip1, target2, ip2):
        return self.conn.root.get_latency(target1, ip1, target2, ip2)

    @handleConnExceptions
    def get_k(self, target, ip):
        return self.conn.get_k(target, ip)

    @handleConnExceptions
    def get_distance(self, lat, lon):
        return distance((self.lat, self.lon), (lat, lon))

def random_latency():
    target1 = open_resolvers.randomkey()
    target2 = geoip.randomkey()
    while not geoip.exists(target1):
        target1 = open_resolvers.randomkey()

    ip1, (lat1, long1) = list(all_dns.smembers(target1))[0], eval(list(geoip.smembers(target1))[0])[1:]
    ip2, (lat2, long2) = list(all_dns.smembers(target2))[0], eval(list(geoip.smembers(target2))[0])[1:]

    #print ip1, lat1, long1, ip2, lat2, long2

    return target1, ip1, target2, ip2

def test(node):
    node.get_latency(*random_latency())

pl_nodes = map(lambda x: PlanetLabNode(x[0], *x[1]), list(enumerate(pl_hosts)))

p = Pool(process_pool_size)
results = p.map(test, pl_nodes)

print len(results)
for r in results:
    print r
