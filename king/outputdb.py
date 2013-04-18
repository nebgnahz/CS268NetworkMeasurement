from DataPoint import DataPoint, Session

s = Session()

query_size = 25000

def page_query(q):
    offset = 0
    while True:
        r = False
        for elem in q.limit(query_size).offset(offset):
           r = True
           yield elem
        offset += query_size
        if not r:
            break

for count, r in enumerate(page_query(s.query(DataPoint))):
    print count
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
