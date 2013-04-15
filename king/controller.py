import logging, os, redis, string
from apscheduler.scheduler import Scheduler
from datetime import datetime, timedelta
from multiprocessing import Process, Queue

from PlanetLabNode import PlanetLabNode
from utilities import outputException, distance

num_processes = 250
all_dns = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=0))
open_resolvers = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=1))
geoip = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=2))
pl_hosts = [line.split(' ')[0:4] for line in map(string.strip,open('pl-host-list-geo').readlines())]
pl_nodes = map(lambda args: PlanetLabNode(*args), pl_hosts)
q = Queue(num_processes)

def select_random_points():
    target1 = open_resolvers.randomkey()
    target2 = geoip.randomkey()
    while not geoip.exists(target1):
        target1 = open_resolvers.randomkey()

    ip1, coord1 = list(all_dns.smembers(target1))[0], eval(list(geoip.smembers(target1))[0])[1:]
    ip2, coord2 = list(all_dns.smembers(target2))[0], eval(list(geoip.smembers(target2))[0])[1:]

    return (target1, ip1, coord1), (target2, ip2, coord2)

def closestNodes(target1, target2):
    name1, ip1, coord1 = target1
    name2, ip2, coord2 = target2
    # Get closest 10 PL Nodes
    distances = map(lambda node: (distance(coord1, (node.lat, node.lon)), node), pl_nodes)
    distances.sort()
    distances = map(lambda x: x[1], distances)
    return distances[:10]

def query_latency(target1, target2, node):
    name1, ip1, coord1 = target1
    name2, ip2, coord2 = target2
    return node.get_latency(name1, ip1, name2, ip2)

# TODO: Store None Responses As Well
def doWork():
    from DataPoint import Session, DataPoint
    s = Session()
    while True:
        try:
            target1, target2, node = q.get()
            print target1, target2, node
            result = query_latency(target1, target2, node)
            if result:
                end_time, start_time, ping_times, address = result
            else:
                end_time = start_time = ping_times = address = None
            point = DataPoint(target1, target2, start_time, end_time, ping_times, address, node.host)
            s.add(point)
            s.commit()
        except Exception, e:
            outputException(e)

def main():
    processes = []
    for i in range(num_processes):
        p = Process(target=doWork)
        p.daemon = True
        p.start()
        processes.append(p)

    while True:
        t1, t2 = select_random_points()
        closest_nodes = closestNodes(t1, t2)
        for node in closest_nodes:
            q.put((t1, t2, node))

main()
