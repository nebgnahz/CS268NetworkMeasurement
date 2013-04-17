from DataPoint import DataPoint, Session

s = Session()

num_items = s.query(DataPoint).all().count()

print num_items

for x in range(num_items):
    r = s.query(DataPoint).filter(DataPoint.id == x,).limit(1)
    print 'Date of Measurement', r.timestamp
    print r.name1, r.name2
    print r.target1
    print r.target2
    print r.test_point
    print r.address
    print r.start
    print r.end
    print r.pings
    print '---------------------------------'
