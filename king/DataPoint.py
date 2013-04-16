from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, PickleType, Boolean, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

engine = create_engine('mysql+pymysql://ucb_268_measure:ucb_268_measure@data.cnobwey0khau.us-west-2.rds.amazonaws.com:3306/mydb', echo=False)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)

class DataPoint(Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    name1 = Column(String)
    name2 = Column(String)
    target1 = Column(PickleType)
    target2 = Column(PickleType)
    start = Column(DateTime)
    end = Column(DateTime)
    pings = Column(PickleType)
    address = Column(PickleType)
    test_point = Column(String)
    success = Column(Boolean)

    def __init__(self, name1, name2, target1, target2, start, end,
                 pings, address, test_point, success):
        self.timestamp = datetime.now()
        self.name1 = name1
        self.name2 = name2
        self.target1 = target1
        self.target2 = target2
        self.start = start
        self.end = end
        self.pings = pings
        self.address = address
        self.test_point = test_point
        self.success = success

Base.metadata.create_all()
