"""Google Search Module

Search google for a url and estimate the time
"""
import urllib, urllib2, threading, httplib, Queue
import sys, getopt, re, time
import string, random, logging
from BeautifulSoup import BeautifulSoup, CData
from datetime import timedelta
from sysutils import tcpdump, ping

htmlFile = None
# logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


def random_string(size=6, chars=string.ascii_letters + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

def google_scrape(query, interface):
	address = "http://www.google.com/search?hl=en&output=search&q=%s" % (urllib.quote_plus(query))
	request = urllib2.Request(address, None, {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'})
	# use tcpdump
	# before this, I should probably obtain google's ip for this transaction

	q = Queue.Queue()
	thread = threading.Thread(target=tcpdump, args=(5, q, interface))
	thread.start()
	
	elapsed = -1
	try:
		# count time around this command
		start_time = time.time()
		page = urllib2.urlopen(request).read()
		end_time = time.time()
		print int(round(start_time * 1000)), int(round(end_time * 1000))
		elapsed = end_time - start_time
	except httplib.BadStatusLine:
		print request

	print len(page)
	logging.debug("time elapsed for google query: %f",  elapsed)

	thread.join(10)
	if thread.isAlive():
		logging.debug("terminating tcpdump process")
		thread.join()
	try:
		returncode, ip_src, tcpEntries = q.get(timeout = 1)
	except Queue.Empty:
		logging.debug("queue is empty for query: %s", query)
		
	# if write this to file for debugging
	if htmlFile:
		htmlFile.write(page)

	# parse the file
	soup = BeautifulSoup(page)
	googleTime = None
	try:
		resultStats = soup.find("div", {"id": "resultStats"})
		# u'(0.11 seconds)&nbsp;'
		pattern = '\(([0-9]+\.[0-9]+)'
		text = str(soup.nobr.text)
		webpage_time = re.search(pattern, soup.nobr.text)
		googleTime = timedelta( seconds = float(webpage_time.group(1)) )
		logging.debug("%s %f %f", query, elapsed, float(webpage_time.group(1)))
	except:
		logging.debug("exception caught when parsing, no google stats for query: %s", query)
		
	queryTime = timedelta(seconds=elapsed)
	
	if ip_src is not None:
		logging.debug("find ip source, now pinging")
		returncode, pingTime = ping(ip_src)
		pingTimeDelta = map(lambda t: timedelta(seconds=t), pingTime)
		return queryTime, googleTime, ip_src, pingTimeDelta, tcpEntries
	return queryTime, googleTime, ip_src, None, tcpEntries

def google_trends():
	address = "http://www.google.com/trends/hottrends/atom/hourly"
	request = urllib2.Request(address, None, {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'})
	page = urllib2.urlopen(request).read()
	if htmlFile:
		htmlFile.write(page)
		
	soup = BeautifulSoup(page)

	results = [];
	for cd in soup.findAll(text=True):
		if isinstance(cd, CData):
			s = BeautifulSoup(cd.encode())
			results.extend([i.string for i in s.findAll('a')])
	return results	
			
if __name__ == '__main__':
	"""'myfunc' documentation."""
	# parse command line options
	try:
		opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
	except getopt.error, msg:
		print msg
		print "for help use --help"
		sys.exit(2)

	# process options
	for o, a in opts:
		if o in ("-h", "--help"):
			print __doc__
			sys.exit(0)
	# process arguments
	for arg in args:
		print arg
		htmlFile = open(arg + '.html', 'w')
		qTime, gTime, ip, pingTime, tcpEntries = google_scrape(arg, 'eth0')
		print qTime, gTime, ip, pingTime

