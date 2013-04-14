from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, PickleType
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///latency.db', echo=False)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)
s = Session()

class DataPoint(object):
    def __init__(self, start, end, pings, address, test_point):
        self.start = start
        self.end = end
        self.pings = pings
        self.address = address
        self.test_point = test_point

class Query(Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key=True)
    target1 = Column(PickleType)
    target2 = Column(PickleType)
    points = Column(PickleType)

    def __init__(self, target1, target2, points)
        self.target1 = target1
        self.target2 = target2
        self.points = points

q = s.query(Query)

for r in q.all():
    print r.target1
    print r.target2
    for p in r.points:
        print p.start
        print p.end
        print p.pings
        print p.address
        print p.test_point
    print '---------------------------------'
