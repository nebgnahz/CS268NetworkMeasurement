import logging, os, redis, rpyc, string, subprocess, sys
from apscheduler.scheduler import Scheduler
from datetime import datetime, timedelta
from multiprocessing import Process
from plumbum import SshMachine
from rpyc.utils.factory import ssh_connect
from utilities import distance

process_pool_size = 50

all_dns = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=0))
open_resolvers = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=1))
geoip = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=2))
pl_hosts = [line.split(' ')[0:4] for line in map(string.strip,open('pl-host-list-geo').readlines())]

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, PickleType
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///latency.db', echo=False)
Base = declarative_base(bind=engine)

class DataPoint(object):
    def __init__(self, start, end, pings, address, test_point):
        self.start = start
        self.end = end
        self.pings = pings
        self.address = address
        self.test_point = test_point

class Query(Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key=True)
    target1 = Column(PickleType)
    target2 = Column(PickleType)
    points = Column(PickleType)

    def __init__(self, target1, target2, points):
        self.target1 = target1
        self.target2 = target2
        self.points = points

Base.metadata.create_all()

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
            print e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            try:
                self.restartPL()
                self.connectPL()
            except Exception, e:
                print e
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)    
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
                    print e
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    self.connected = False
                    try:
                        self.connect()
                        return fn(self, *args, **kwargs)
                    except Exception, e:
                        print e
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        print(exc_type, fname, exc_tb.tb_lineno)
                        self.connected = False
                        return None
            else:
                return None
        return wrapped

    @handleConnExceptions
    def get_latency(self, target1, ip1, target2, ip2):
        timed_fn = rpyc.timed(self.conn.root.get_latency, 15)
        return timed_fn(target1, ip1, target2, ip2)

    @handleConnExceptions
    def get_k(self, target, ip):
        timed_fn = rpyc.timed(self.conn.get_k, 15)
        return timed_fn(target, ip)

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
    distances = distances[:5]

    results = map(lambda (dist, node): (node.host, node.get_latency(name1, ip1, name2, ip2)), distances)
    return results

def one_round():
    print 'Task'
    try:
        target1, target2 = select_random_points()
        results = query_latency(target1, target2)
        return target1, target2, results
    except Exception, e:
        print e
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return None

def doWork():
    Session = sessionmaker(bind=engine)
    s = Session()
    while True:
        try:
            target1, target2, result_set = one_round()
            points = []
            if result_set:
                for host, info in filter(None,result_set):
                    if info:
                        try:
                            # TODO: Store None Responses As Well
                            (end_time, start_time, ping_times, address) = info
                            point = DataPoint(start_time, end_time, ping_times, address, host)
                            points.append(point)
                        except Exception, e:
                            print e
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print(exc_type, fname, exc_tb.tb_lineno)
                            pass
                data_set = Query(target1, target2, points)
                s.add(data_set)
                s.commit()
        except Exception, e:
            print e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            pass

pl_nodes = map(lambda args: PlanetLabNode(*args), pl_hosts)

def main():
    processes = []
    for i in range(process_pool_size):
        p = Process(target=doWork)
        p.daemon = True
        p.start()
        processes.append(p)
    for p in processes:
        p.join()

main()
