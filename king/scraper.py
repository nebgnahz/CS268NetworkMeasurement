import dns.resolver, dns.name, dns.rdatatype

google_ips = ["74.125.224.52", "74.125.224"]
yahoo_ips = ["98.139.183.24", "98.139.183"]
berkeley_ips = ["169.229.216.200", "169.229.216"]

ips = google_ips + yahoo_ips + berkeley_ips

def getAddr(ip):
	ip = ip.split('.')
	ip.reverse()
	addr = dns.name.from_text("%s.in-addr.arpa" % '.'.join(ip))
	return addr


for ip in ips:
	addr = getAddr(ip)
	print addr
	authority = dns.resolver.query(addr, rdtype="PTR", rdclass="IN", raise_on_no_answer=False).response.authority
	for rr in authority:
		print rr
	print '\n'
