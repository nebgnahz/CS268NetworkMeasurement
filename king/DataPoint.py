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
    timestamp = Column(DateTime) # Time measurement taken
    name1 = Column(String(length=200)) # First Test Point
    name2 = Column(String(length=200)) # 2nd Test point
    target1 = Column(PickleType) # Geo IP
    target2 = Column(PickleType) # Geo IP
    start = Column(DateTime) # Start Tking step 5
    end = Column(DateTime) # End Tking Step 8
    pings = Column(PickleType) # 5 ping times
    address = Column(PickleType) # DNS Server that responded (check for forwarder)
    test_point = Column(String(length=200)) # Planet Lab Node that did testing
    success = Column(Boolean) # True if we have all data

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
