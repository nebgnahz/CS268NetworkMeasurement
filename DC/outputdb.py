import socket
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, PickleType
from sqlalchemy.ext.declarative import declarative_base

# db_name = '../CS268Data/gQuery_lsirextpc01.epfl.ch.db'
db_name = '../CS268Data/gQuery_pl1.6test.edu.cn.db'
#gQuery_dhcp-44-12.eecs.berkeley.edu.db'

engine = create_engine('sqlite:///' + db_name, echo=False)

Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)
s = Session()

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

		
for r in s.query(Query).yield_per(100):
	print r.index
	print r.query
	print r.return_ip
	print r.queryTime
	print r.googleTime
	print r.pingTime
	for entry in r.tcpEntries:
		print entry

	print "\n------------------"
print "+++++++++++++++++++++++++++++++\n"
print "record #:", q.count()	
