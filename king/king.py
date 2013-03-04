import dns.query, dns.message, random, time, ping, socket

def domain_latency(path):
	s = 0.0
	for i in xrange(0,100):
		start = time.time()
		q = dns.message.make_query("%i.%s" % (random.randint(0,10000), path), "A")
		# TODO: Break after bad domain queries
		response = dns.query.udp(q,"128.32.206.9")
		elapsed = time.time() - start
		s += elapsed

	delay = 0
	for i in xrange(0,100):
		try:
			delay += ping.do_one("128.32.206.9", 2,64)
		except socket.error, e:
			print "Ping Error", e

	print "Average: %f" %((s-delay)/100)

	delay = 0
	for i in xrange(0,100):
		try:
			delay += ping.do_one(path, 2,64)
		except socket.error, e:
			try:
				delay += ping.do_one("www.%s" % path, 2,64)
			except socket.error, e2:
				print "Bad Domain", e
				break

	print "Average: %f" %(delay/100.0)

domain_latency("berkeley.edu")
