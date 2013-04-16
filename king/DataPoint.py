from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, PickleType, Boolean, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///latency.db', echo=False)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)

class DataPoint(Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key=True)
    target1 = Column(String)
    target2 = Column(String)
    start = Column(PickleType)
    end = Column(PickleType)
    pings = Column(PickleType)
    address = Column(PickleType)
    test_point = Column(String)
    success = Column(Boolean)

    def __init__(self, target1, target2, start, end, pings, address, test_point, success):
        self.target1 = target1
        self.target2 = target2
        self.start = start
        self.end = end
        self.pings = pings
        self.address = address
        self.test_point = test_point
        self.success = success

Base.metadata.create_all()
