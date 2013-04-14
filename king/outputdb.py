from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, PickleType
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from DataPoint import DataPoint, Query, session

q = session.query(Query)

for r in q.all():
    print r.target1
    print r.target2
    for p in r.points:
        print p.start
        print p.end
        print p.pings
        print p.address
        print p.test_point
        print '***********'
    print '---------------------------------'
