from compiler.ast import flatten
from multiprocessing import Pool
from DataPoint import DataPoint, Session

query_size = 25000
total = Session().query(DataPoint).count()
print total

def page_query(args):
    start, end = args

    from DataPoint import DataPoint, Session
    s = Session()
    q = s.query(DataPoint)

    offset = start
    results = []
    while offset < end:
        r = q.limit(min(query_size, end - offset + 1)).offset(offset).all()
        results.append(r)
        offset += query_size
    return results

slices = []
x = 0
while x < total:
    slices.append((x, min(x+query_size,total)))
    x += query_size

print slices

p = Pool(10)
results = flatten(p.map(page_query, slices))
print len(results)

#    print 'Date of Measurement', r.timestamp
#    print r.name1, r.name2
#    print r.target1
#    print r.target2
#    print r.test_point
#    print r.address
#    print r.start
#    print r.end
#    print r.pings
#    print '---------------------------------'
