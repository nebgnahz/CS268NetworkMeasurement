import dns.resolver, dns.name, dns.rdatatype

ips = ["74.125.224.52", "74.125.224"]

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
