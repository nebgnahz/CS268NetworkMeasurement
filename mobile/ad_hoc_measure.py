from sysutils import tcpdump, ping
import string, os, time, urllib2, sys
from process_db import extract, process

file_download = False; 
extract_db = True;
ping_urllist = False;
parse_ping = False;

if extract_db:
  files = [f for f in os.listdir('./') if os.path.isfile('./'+ f) and f.endswith('.db')]
  print files[0]
  extract(files[0])

if parse_ping:
  # used to parse ping logs
  f = open('ping_log', 'r') 
  meta = f.readline()
  pings = map(lambda x: re.search('time=(\d+\.\d+) ms', x) and int(re.search('time=(\d+\.\d+) ms', x).group(1)) or -1, f.readlines())[:-4]


if ping_urllist:
  f = open('../mobile/urllist.txt', 'r')
  traceroute_dsts = [line.split(' ')[0] for line in filter(lambda x: x!='', map(string.strip, f.readlines()))]

  for dst in traceroute_dsts:
    print dst[7:]
    print ping(dst[7:])

if file_download:
  file_size = ['1KB', '10KB', '100KB', '1MB'];
  addresses = map(lambda x: "http://chuchufan.info/files/testfile_"+x, file_size)
  for address in addresses:
    request = urllib2.Request(address, None)
    start_time = time.time()
    urllib2.urlopen(request).read()
    elapsed = time.time() - start_time
    print elapsed
  
