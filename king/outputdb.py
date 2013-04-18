import sys
from compiler.ast import flatten
from multiprocessing import Pool
from DataPoint import Session, DataPoint

s = Session()

def page_query(q):
    offset = 0
    while True:
        r = False
        for elem in q.limit(2000).offset(offset):
           r = True
           yield elem
        offset += 1000
        if not r:
            break

total = s.query(DataPoint).filter(DataPoint.success == True,).count()

print 'Total', total

for count, r in enumerate(page_query(s.query(DataPoint).filter(DataPoint.success == True,))):
    print '\r                      \r','{0:.0f}%'.format(float(count)/total * 100),
    sys.stdout.flush()
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
