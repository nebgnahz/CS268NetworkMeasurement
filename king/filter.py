import cPickle as pickle
from collections import defaultdict
from utilities import distance

input_file = open('results.pickle', 'r')

results = pickle.load(input_file)

seen = defaultdict(list)

total = 0
negative_latency = 0
zero_dist = 0
forwarder_present = 0
faster_than_light = 0
greater_than_5 = 0

for r in results:
    try:
        total += 1
        id, timestamp, name1, name2, target1, target2, start, end, pings, address, test_point, success = r
        timestamp =  pickle.loads(timestamp)
        target1 = pickle.loads(target1)
        target2 =  pickle.loads(target2)
        address = pickle.loads(address)
        start = pickle.loads(start)
        end = pickle.loads(end)
        pings = pickle.loads(pings)

        dist = distance(target1[2], target2[2])

        latency = (end - start - min(pings)).total_seconds()

        if latency < 0:
            negative_latency += 1
        if dist <= 0:
            zero_dist += 1
        if target[1] != address[0]:
            forwarder_present += 1
        if latency > (dist/2.0/100000):
            faster_than_light += 1
        if latency >= 5:
            greater_than_5 += 1

        if latency > 0 \
        and dist > 0 \
        and target1[1] == address[0] \
        and latency > (dist/2.0/100000):
            seen[(name1, name2)].append((dist, latency, test_point, timestamp))
    except:
        continue

for name1, name2 in seen.keys():
    if len(seen[(name1, name2)]) >= 2 and len(seen[name2, name1]) >= 2:
        for count, (dist, latency, test_point, timestamp) in enumerate(seen[(name1, name2)]):
            if count == 0:
                pass
            else:
                print name1, name2, dist, latency, test_point

print "total", total
print "negative_latency", negative_latency
print "zero_dist", zero_dist
print "forwarder_present", forwarder_present
print "faster_than_light", faster_than_light
print "greater_than_5", greater_than_5
