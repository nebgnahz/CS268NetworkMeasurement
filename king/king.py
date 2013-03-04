import dns.query, dns.message, random, time, ping, socket

s = 0.0

for i in xrange(0,100):
	start = time.time()
	q = dns.message.make_query("%i.berkely.edu" % random.randint(0,10000), "MX")
	response = dns.query.udp(q,"128.32.206.9")
	elapsed = time.time() - start
	s += elapsed

print "Average: %f" %(s/100.0)

delay = 0
for i in xrange(0,100):
	try:
		delay += ping.do_one("www.berkeley.edu", 2,64)
	except socket.error, e:
		print "Ping Error", e

print "Average: %f" %(delay/100.0)

