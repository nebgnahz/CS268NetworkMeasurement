import os, operator

from StringIO import StringIO
from multiprocessing import Pool, Value
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, PickleType
from sqlalchemy.ext.declarative import declarative_base


files = [f for f in os.listdir('.') if os.path.isfile(f)]
files = filter(lambda f: f.endswith('.db'),files)

counter = Value('i', 0)

def extract(db_name):
    try:
        counter.value += 1
        print counter.value, db_name
        results = []
        engine = create_engine('sqlite:///' + db_name, echo=False)
        Base = declarative_base(bind=engine)
        output_file = open(db_name+'.csv', 'w')

        class Query(Base):
            __tablename__ = 'data'

            id = Column(Integer, primary_key=True)
            index = Column(PickleType)
            query = Column(PickleType)
            return_ip = Column(PickleType)
            queryTime = Column(PickleType)
            googleTime = Column(PickleType)
            pingTime = Column(PickleType)
            tcpEntries = Column(PickleType)

            def __init__(self, index, query, return_ip, queryTime, googleTime, pingTime, tcpEntries):
                self.index = index
                self.query = query
                self.return_ip = return_ip
                self.queryTime = queryTime
                self.googleTime = googleTime
                self.pingTime = pingTime
                self.tcpEntries = tcpEntries

        Session = sessionmaker(bind=engine)
        s = Session()
        for r in s.query(Query).yield_per(1000):
            out = process(r)
            print >> output_file, out
        output_file.close()
        print db_name, 'Done'
    except Exception, e:
        print db_name, e

def process(r):
    output = StringIO()
    print >> output, r.query, ',',
    print >> output, r.index, ',',
    print >> output, r.return_ip, ',',
    print >> output, r.queryTime.total_seconds(), ',',
    if not r.googleTime:
        print >> output, '-1', ',',
    else:
        print >> output, r.googleTime.total_seconds(), ',',

    if not r.pingTime:
        print >> output, '-1', ',',
    else:
        print >> output, min(r.pingTime).total_seconds(),

    return output.getvalue()

p = Pool(20)
p.map(extract, files)
