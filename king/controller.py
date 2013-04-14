import os, redis, string, subprocess
from apscheduler.scheduler import Scheduler
from datetime import datetime, timedelta
from multiprocessing import Pool
from plumbum import SshMachine
from rpyc.utils.factory import ssh_connect
from utilities import distance, threaded_map

process_pool_size = 100
sched = Scheduler(standalone=True)

all_dns = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=0))
open_resolvers = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=1))
geoip = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=2))
pl_hosts = [line.split(' ')[0:4] for line in map(string.strip,open('pl-host-list-geo').readlines())]

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, PickleType
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///latency.db', echo=True)
Base = declarative_base(bind=engine)

class DataPoint(Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key=True)
    target1 = Column(PickleType)
    target2 = Column(PickleType)
    start = Column(PickleType)
    end = Column(PickleType)
    pings = Column(PickleType)
    address = Column(PickleType)

    def __init__(self, target1, target2, start, end, pings, address):
        self.target1 = target1
        self.target2 = target2
        self.start = start
        self.end = end
        self.pings = pings
        self.address = address

Base.metadata.create_all()
Session = sessionmaker(bind=engine)
s = Session()

class PlanetLabNode(object):
    def __init__(self, host, ip, lat, lon):
        self.host = host
        self.ip = ip
        self.lat = float(lat)
        self.lon = float(lon)
        self.connected = False

    def connect(self):
        try:
            self.connectPL()
        except Exception, e:
            try:
                self.restartPL()
                self.connectPL()
            except Exception, e:
                self.connected = False

    def connectPL(self):
        rem = SshMachine(self.host, user='ucb_268_measure', keyfile='~/.ssh/id_rsa',
                         ssh_opts=["-o StrictHostKeyChecking no",
                                   "-o UserKnownHostsFile=/dev/null"])
        conn = ssh_connect(rem, 18861, config={'allow_pickle' : True})
        assert conn.root.test() == 1, "%s: RPC Failure" % self.host
        self.conn = conn
        self.connected = True

    def restartPL(self):
        FNULL = open(os.devnull, 'w')
        subprocess.call(["ssh", "-t", "-i", "~/.ssh/id_rsa", "-o StrictHostKeyChecking no",
                         "-o UserKnownHostsFile=/dev/null", "ucb_268_measure@%s" % self.host,
                         "sudo tking-server stop; sudo tking-server start;"],
                         stdout=FNULL, stderr=FNULL)

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

def select_random_points():
    target1 = open_resolvers.randomkey()
    target2 = geoip.randomkey()
    while not geoip.exists(target1):
        target1 = open_resolvers.randomkey()

    ip1, coord1 = list(all_dns.smembers(target1))[0], eval(list(geoip.smembers(target1))[0])[1:]
    ip2, coord2 = list(all_dns.smembers(target2))[0], eval(list(geoip.smembers(target2))[0])[1:]

    return (target1, ip1, coord1), (target2, ip2, coord2)

def query_latency(target1, target2):
    name1, ip1, coord1 = target1
    name2, ip2, coord2 = target2

    # Get closest 4 PL Nodes
    distances = map(lambda node: (distance(coord1, (node.lat, node.lon)), node), pl_nodes)
    distances.sort()
    distances = distances[:4]

    results = threaded_map(lambda (dist, node): (node.host, node.get_latency(name1, ip1, name2, ip2)), distances, timeout=10.0)
    return results

def one_round(x):
    target1, target2 = select_random_points()
    results = query_latency(target1, target2)
    return target1, target2, results

pl_nodes = map(lambda args: PlanetLabNode(*args), pl_hosts)
p = Pool(process_pool_size)

def task():
    print 'Task'
    results = p.map(one_round, range(process_pool_size))
    for target1, target2, result_set in filter(None,results):
        for host, info in filter(None,result_set):
            if info:
                (end_time, start_time, ping_times, address) = info
                point = DataPoint(target1, target2, start_time, end_time, ping_times, address)
                s.add(point)
    s.commit()

sched.add_interval_job(task, minutes=1)
sched.start()
