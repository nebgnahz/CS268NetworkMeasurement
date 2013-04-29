import cPickle as pickle

input_file = open('results.pickle', 'r')
results = pickle.load(input_file)

forwarder_present = 0
seen = {}

for r in results:
    try:
        id, timestamp, name1, name2, target1, target2, start, end, pings, address, test_point, success = r
        timestamp =  pickle.loads(timestamp)
        target1 = pickle.loads(target1)
        target2 =  pickle.loads(target2)
        address = pickle.loads(address)
        start = pickle.loads(start)
        end = pickle.loads(end)
        pings = pickle.loads(pings)

        if target1[1] != address[0]:
            forwarder_present += 1
            seen[target1] = address
        if len(seen.keys()) == 10:
            break
    except Exception, e:
        print e

for key, value in seen.items():
    print key, value