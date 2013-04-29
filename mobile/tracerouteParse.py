"""
Traceroute log parser

"""

import time, re, sys, argparse, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, PickleType, String
from sqlalchemy.ext.declarative import declarative_base
from multiprocessing import Pool
from os import listdir, getcwd
from os.path import isfile, join
from collections import defaultdict
import pickle

parser = argparse.ArgumentParser(description='Tracerout log parser')
parser.add_argument('--parse', action='store_true', default=False, help='Parse traceroute logs')
parser.add_argument('--output', action='store_true', default=False, help='Print data from the db')
parser.add_argument('--hop_stat', action='store_true', default=False, help='Output delay statistics, used for hop router counts')
parser.add_argument('--hop_delay', action='store_true', default=False, help='Output all delays')
parser.add_argument('--att_exit', action='store_true', default=False, help='Detect the exit point of ATT exit')
parser.add_argument('--dst_dump', action='store_true', default=False, help='Detect the exit point of ATT exit')
parser.add_argument('--route_flaps', action='store_true', default=False, help='Count the amount of routing flaps')
parser.add_argument('--ad_hoc', action='store_true', default=False, help='some add hoc implementation')


arguments = parser.parse_args()

db_name = 'traceroute.db'
engine = create_engine('sqlite:///' + db_name, echo=False)
Base = declarative_base(bind=engine)

class Trace(Base):

  __tablename__ = 'data'

  id = Column(Integer, primary_key=True)
  logTime = Column(PickleType)
  rssi = Column(PickleType)
  radio_type = Column(String)
  current_dst = Column(PickleType)
  hop_n = Column(Integer)
  hop_ASN = Column(Integer)
  hop_hostname = Column(String)
  hop_ip = Column(String)
  delay = Column(Integer)

  def __init__(self, logTime, rssi, radio_type, current_dst, hop_n, hop_ASN, hop_hostname, hop_ip, delay):
    self.logTime = logTime
    self.rssi = rssi
    self.radio_type = radio_type
    self.current_dst = current_dst
    self.hop_n = hop_n
    self.hop_ASN = hop_ASN
    self.hop_hostname = hop_hostname
    self.hop_ip = hop_ip
    self.delay = delay
    
Base.metadata.create_all()
Session = sessionmaker(bind=engine)
s = Session()

# I should have really parsed this into a database....
def parse_traceroute(filename):
  f = open(filename, 'r')
  logTime = time.strptime(filename, "logs/%Y_%m_%d_%H_%M_%S.txt")

  hostname_pattern = "(([a-zA-Z\d\-]+\.)+[a-zA-Z\d\-]+)"
  ip_pattern = "((\d+\.){3}\d+)"
  trace_pattern = "(\d*)  \[AS(\d+)\] (%s|%s) \(%s\)((  \d+\.\d+ ms)+)" % (hostname_pattern, ip_pattern, ip_pattern)

  # first line is comments include RSSI and signal type
  rssi, radio_type = trace_meta(f.readline())
  current_dst = None
  for line in f:
    # so everytime when there is traceroute found, then current_dst will be updated
    if (line.find('traceroute')) != -1:
      if ((line.find('Warning') != -1) or (line.find('unknown host') != -1)):
        # multiple address warning
        continue
      else:
        # extract the destination and warning
        pattern = "traceroute to ([a-z]+.[a-z]+) \(([0-9]+.[0-9]+.[0-9]+.[0-9]+.)\),"
        results = re.search(pattern, line)
        if results is not None:
          dst_name = results.group(1)
          dst_ip = results.group(2)
          current_dst = (dst_name, dst_ip)
        continue
    elif line[0] == '\n' or len(line) == 0:
      # bad lines
      pass
    else:
      # no traceroute, then have to be trace messages
      # remove * first, and other bad stuff
      bad_reply = line.count(" *")
      line.replace(" *", "")
      re.sub(" ![HNPZXFS]?", "", line)

      results = re.search(trace_pattern, line)
      if results is not None:
        hop_index = results.group(1)
        hop_ASN = results.group(2)
        hop_hostname = results.group(3)
        hop_ip = results.group(8)

        latencies = results.group(10)
        num_latencies = latencies.count('ms');
        delays = filter(lambda x: x != 'ms' and x != '', latencies.split(' '))
        delays = map(float, delays)

        # when you see new hop_index, update it
        if hop_index != '':
          hop_n = int(hop_index)

        for d in delays:
          data = Trace(logTime, rssi, radio_type, current_dst, hop_n, hop_ASN, hop_hostname, hop_ip, d)
          s.add(data)
          s.commit()
          # print logTime, rssi, radio_type, current_dst, hop_n, hop_ASN, hop_hostname, hop_ip, d
          
        for i in range(bad_reply):
          data = Trace(logTime, rssi, radio_type, current_dst, hop_n, None, None, None, None)
          s.add(data)
          s.commit()
  
          # print logTime, rssi, radio_type, current_dst, hop_n, None, None, None, None  

def trace_meta(line):
  rssi = None
  radio_type = None
  p = "-(\d+)dBm"
  r = re.search(p, line)
  if r is not None:
    rssi = r.group(1)
  else:
    print "No RSSI found"

  if line.find('LTE') != -1:
    radio_type = "LTE"
  elif line.find('4G') != -1:
    radio_type = "4G"
  else:
    print "No signal type found"

  return rssi, radio_type

def output_fromdb():
  q = s.query(Trace)
  
  for r in q.all():
    print datetime.datetime(*r.logTime[:6]), r.rssi, r.radio_type, r.current_dst, r.hop_n, r.hop_ASN, r.hop_hostname, r.hop_ip, r.delay

  
if __name__=='__main__':
  # parse command line options
  if arguments.parse:
    mypath = "logs/"
    logFiles = [join(mypath, f) for f in listdir(mypath) if (isfile(join(mypath,f)) and f[-4:] == ".txt")]
    print logFiles
    p = Pool(10)
    p.map(parse_traceroute, logFiles)
    # parse_traceroute('logs/2013_04_22_20_07_27.txt')
  elif arguments.output:
    output_fromdb()
  elif arguments.hop_delay or arguments.hop_stat:
    hop_None = [0]*13
    hop_ipNum = [defaultdict(int) for i in range(13)];
    for i in range(1, 14):
      if arguments.hop_delay:
        print "d%d" % i, '= [',
      q = s.query(Trace.delay, Trace.hop_ip, Trace.hop_ASN).\
          filter(Trace.hop_n==i, Trace.radio_type=='LTE')
      # print q.count()
      for r in q.all():
        hop_ipNum[i-1][(r.hop_ASN, r.hop_ip)] += 13
        if r.delay is None:
          hop_None[i-1] += 1
        else:
          if arguments.hop_delay:
            print r.delay,
          pass
      if arguments.hop_delay:
        print '];'
      if arguments.hop_stat:
        for key in hop_ipNum[i-1]:
          ASN, ip = key
          if ASN is not None:
            print i, ',', ASN, ',', ip, ',', hop_ipNum[i-1][key]
          else:
            print i, ',', '-1', ',', '', ',', hop_ipNum[i-1][key]
            
  elif arguments.dst_dump:
    q = s.query(Trace.current_dst).\
        group_by(Trace.current_dst)
    print q.count()
    all_dst = defaultdict(list);
    for r in q.all():
      host_name, host_ip = r.current_dst
      all_dst[host_name].append(host_ip)
    for key in all_dst:
      if len(all_dst[key]) == 1:
        print key, ',', all_dst[key][0]
    pickle.dump(all_dst, open( "traceroutedst.p", "wb" ))

  elif arguments.route_flaps:
    # given a dst, and a specific hop, count the flaps in
    hop_flaps = defaultdict(set)
    q = s.query(Trace.current_dst, Trace.logTime, Trace.hop_n, Trace.hop_ip).\
          filter(Trace.radio_type=='LTE')
    print "%", q.count()
    for r in q.all():
      if r.hop_ip is not None:
        hop_flaps[(r.current_dst, r.logTime, r.hop_n)].add(r.hop_ip)

    flaps_count = defaultdict(list)
    for key in hop_flaps:
      dst, logT, n = key
      # print n, len(hop_flaps[key])
      flaps_count[n].append(len(hop_flaps[key]))
      # sys.exit(1)
    
    for key in flaps_count:
      print 'd%d=' % key, flaps_count[key], ';'
  
  elif arguments.att_exit:
    # python tracerouteParse.py --att_exit > dst_exit.csv
    # count the first hop that isn't belonging to ATT AS7018/AS0
    q = s.query(Trace.current_dst, Trace.logTime, Trace.hop_n, Trace.hop_ip, Trace.hop_ASN).\
          filter(Trace.radio_type=='LTE').\
          order_by(Trace.hop_n)
    exit_points = defaultdict(list)
    att_set = set([0, 7018])
    for r in q.all():
      name, ip = r.current_dst
      if r.hop_ASN not in att_set \
          and r.hop_n > 3 \
          and r.hop_ip is not None:
        if not exit_points[r.current_dst]:
          exit_points[r.current_dst].append((r.hop_n, r.hop_ASN, r.hop_ip))

    print "dst, exit"

    pickle.dump(exit_points, open("dst_exit.p", "wb"))
    
    for key in exit_points:
      name, dst_ip = key
      n, asn, ip = exit_points[key][0]
            
      # print '%d, ' % n,
      print "%s, %s" % (dst_ip, ip)
      
    # I have selected 
    # NY_set = set(["64.145.94.19", "208.64.111.142", "209.196.216.50", "69.60.7.199", "165.1.125.44", "207.241.148.80", "161.221.89.118", "129.228.25.181", "208.93.170.15", "107.6.107.204", "63.240.8.32", "67.214.157.20", "209.81.86.122", "206.220.43.92", "74.113.188.100", "206.220.43.92", "199.59.243.105", "173.231.134.18"])
    # for hop 9, it turns out that there are still 19 different IPs along the path

  elif arguments.ad_hoc:
    q = s.query(Trace).\
          filter(Trace.radio_type=='LTE')
    for r in q.all():
      name, ip = r.current_dst
      if ip == "70.42.185.10":
        print datetime.datetime(*r.logTime[:6]), r.rssi, r.radio_type, r.current_dst, r.hop_n, r.hop_ASN, r.hop_hostname, r.hop_ip, r.delay


    # an interesting path 70.42.185.10
