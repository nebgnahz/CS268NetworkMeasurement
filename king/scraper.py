from dns import name, resolver, reversename

ip = "206.190.36.45"

def flipIP(ip):
	ip = ip.split('.')
	ip.reverse()
	return '.'.join(ip)

addr = name.from_text("%s.in-addr.arpa" % flipIP(ip))
print addr
print str(resolver.query(addr,"PTR")[0])

'''
addr=reversename.from_address(ip)
print addr
str(resolver.query(addr,"PTR")[0])
''
