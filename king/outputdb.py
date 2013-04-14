from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, PickleType
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///latency.db', echo=False)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)
s = Session()

class DataPoint(Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key=True)
    target1 = Column(PickleType)
    target2 = Column(PickleType)
    start = Column(PickleType)
    end = Column(PickleType)
    pings = Column(PickleType)
    address = Column(PickleType)

    def __init__(self, target1, target2, start, end, pings, address):
        self.target1 = target1
        self.target2 = target2
        self.start = start
        self.end = end
        self.pings = pings
        self.address = address

q = s.query(DataPoint)

for r in q.all():
    print r
