import cPickle as pickle
from collections import defaultdict
from utilities import distance

input_file = open('results.pickle', 'r')

results = pickle.load(input_file)

seen = defaultdict(list)

for r in results:
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
    
    if latency > 0 \
    and dist > 0 \
    and target1[1] == address[0] \
    and latency > (dist/3.0/100000) \
    and len(filter(lambda x: x.total_seconds()/latency > 1.2, pings)) != 0 \
    and latency < 5:
        seen[(name1, name2)].append((dist, latency, test_point, timestamp))

for name1, name2 in seen.keys():
    if len(seen[(name1, name2)]) >= 2 and len(seen[name2, name1]) >= 2:
        for count, (dist, latency, test_point, timestamp) in enumerate(seen[(name1, name2)]):
            if count == 0:
                pass
            else:
                print name1, name2, dist, latency, test_point
