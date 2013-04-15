from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, PickleType
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from DataPoint import DataPoint, Session

q = Session().query(DataPoint)

for r in q.all():
    print r.target1
    print r.target2
    print r.test_point
    print r.address
    print r.start
    print r.end
    print r.pings
    print '---------------------------------'
