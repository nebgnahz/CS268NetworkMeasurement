"""Google Search Module

Search google for a url and estimate the time
"""
from BeautifulSoup import BeautifulSoup, CData
import urllib, urllib2, threading, httplib
from Queue import Queue
import sys, getopt, re, time
from sysutils import tcpdump, ping
import string, random, logging

htmlFile = None
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def random_string(size=6, chars=string.ascii_letters + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

def google_scrape(query):
	address = "http://www.google.com/search?hl=en&output=search&q=%s" % (urllib.quote_plus(query))
	request = urllib2.Request(address, None, {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'})
	# use tcpdump
	# before this, I should probably obtain google's ip for this transaction

	q = Queue()
	thread = threading.Thread(target=tcpdump, args=(2, q))
	thread.start()
	
	elapsed = -1
	try:
		# count time around this command
		start_time = time.time()
		page = urllib2.urlopen(request).read()
		elapsed = time.time() - start_time
	except httplib.BadStatusLine:
		print request
				
	logging.debug("time elapsed for google query: %f",  elapsed)

	if htmlFile:
		htmlFile.write(page)

	
	soup = BeautifulSoup(page)
	googleTime = None
	try:
		resultStats = soup.find("div", {"id": "resultStats"})
		# u'(0.11 seconds)&nbsp;'
		pattern = '\(([0-9]+\.[0-9]+)'
		text = str(soup.nobr.text)
		webpage_time = re.search(pattern, soup.nobr.text)
		googleTime = float(webpage_time.group(1))
		logging.debug("%s %f %f", query, elapsed - googleTime, googleTime)
	except:
		logging.debug("exception caught when parsing, no google stats for query: %s", query)

	thread.join(3)
	if thread.isAlive():
		logging.debug("terminating tcpdump process")
		thread.join()
	returncode, ip_src = q.get()
	queryTime = elapsed
	if ip_src is not None:
		logging.debug("find ip source, now pinging")
		returncode, pingTime = ping(ip_src)
		return queryTime, googleTime, ip_src, pingTime
	return queryTime, googleTime, ip_src, None

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
			for a in s.findAll('a'):
				results.append(a.text)
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
		print google_scrape(arg)
		
