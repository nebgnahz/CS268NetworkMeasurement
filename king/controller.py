import logging, os, redis, string
from apscheduler.scheduler import Scheduler
from datetime import datetime, timedelta
from multiprocessing import Process

from PlanetLabNode import PlanetLabNode
from DataPoint import Session, DataPoint, Query
from utilities import outputException, threaded_map, distance

process_pool_size = 1
all_dns = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=0))
open_resolvers = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=1))
geoip = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=2))
pl_hosts = [line.split(' ')[0:4] for line in map(string.strip,open('pl-host-list-geo').readlines())]
pl_nodes = map(lambda args: PlanetLabNode(*args), pl_hosts)

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

    results = threaded_map(lambda (dist, node): (node.host, node.get_latency(name1, ip1, name2, ip2)), distances)
    return results

def one_round():
    print 'Task'
    try:
        target1, target2 = select_random_points()
        results = query_latency(target1, target2)
        return target1, target2, results
    except Exception, e:
        outputException(e)
        return None

def doWork():
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
                            outputException(e)
                            pass
                data_set = Query(target1, target2, points)
                s.add(data_set)
                s.commit()
        except Exception, e:
            outputException(e)
            pass

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
