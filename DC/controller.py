from gQuery import google_scrape, random_string, google_trends
import logging, sys, time, datetime, socket, os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, PickleType
from sqlalchemy.ext.declarative import declarative_base

db_name = os.getenv("HOME") + '/gQuery_' + socket.gethostname() + '.db'
engine = create_engine('sqlite:///' + db_name, echo=False)

Base = declarative_base(bind=engine)

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

Base.metadata.create_all()
Session = sessionmaker(bind=engine)
s = Session()
		
# I might have to rate limit this query
# from someone on stackoverflow, it seems safe to have automatic query with an interval larger than 1 second
# also diverse the search, rather than repeated search a single word

print "Starting", datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")

hot_items = google_trends()
random_list = []
for i in range(len(hot_items)):
	query = random_string(32)
	random_list.append(query)

merged_list =  [j for i in zip(hot_items, random_list) for j in i]
reduced_list = merged_list[0:20]

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
sleep_time = 5

# schedule every two hours running
repeated_times = 10

# usually the list size is 20, we search each 10 times. then its 200 times
# each time sleep for 5 sec, with additional time spent around 10 sec
# 15 sec * 200 -> 3000 sec -> < 1h
# not too bad
# let's test if this will be banned by google

for i in range(repeated_times):
	for item in reduced_list:
		# search hot item
		print "\n[%i] %s" % (i+1, item)
		qTime, gTime, ip, pingTime, tcpEntries = google_scrape(item, 'eth0')
		data = Query(i, item, ip, qTime, gTime, pingTime, tcpEntries)
		s.add(data)
		s.commit()
		
		time.sleep(sleep_time)

print "Ending", datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
