import argparse

# this script only does limited parsing:
# it checks if the cellular network path is the specific one, and count how many follows
# there's got be a better way of using CouchDB MapReduce on this...

parser = argparse.ArgumentParser(description='Traceroute Log Parsing')
parser.add_argument('-f', action='store', dest='fName', default="", help='specify the file to be parsed')

arguments = parser.parse_args()
hops = []
for i in range(30):
	count = {}
	count[None] = 0
	hops.append(count)

count_to_five = 0
hop_num = 1

f = open(arguments.fName, 'r')
for line in f:
	if line[0] == '#' or line[0] == '\n' or len(line) == 0:
		continue

	elements = line.split(' ')
	if elements[0] == "traceroute" or elements[0] == "traceroute:":
		count_to_five = 0
		continue

	# remove space, remove 'ms'
	elements = filter (lambda a: a != '' and a != 'ms' and a != 'ms\n', elements)
	#print count_to_five, elements
	if count_to_five == 0:
		hop_num = int(elements.pop(0))
		# print hop_num, elements
		while elements and (elements[0] == '*' or elements[0] == '*\n'):
			# not a valid measurements
			elements.pop(0)
			hops[hop_num][None] += 1
			count_to_five += 1
			
	if len(elements) == 0:
  	# handle the case when timeout occurs, fill with "None"
		while count_to_five < 5:
			hops[hop_num][None] += 1
			count_to_five += 1

		count_to_five = 0
		continue

	# extract AS number first
	#print elements
	if elements[0][0:3] == "[AS":
		ASN = elements.pop(0)
		ASN = ASN[1:len(ASN)-1]
	
	routerName = elements.pop(0)
	routerIP = elements.pop(0)
	routerIP = routerIP[1:len(routerIP)-1]
	delay = elements.pop(0)
	#print ASN, routerName, routerIP, delay
	while delay[0] == "!":
		if elements:
			delay = elements.pop(0)
		else:
			delay = None
			break
	if delay is not None:
		try:
			delay = float(delay)
		except:
			delay = -1
	else:
		continue
	
	#print ASN, routerName, routerIP
		
	if routerIP in hops[hop_num]:
		hops[hop_num][routerIP].append(delay)
	else:
		hops[hop_num][routerIP] = [delay]
		
	count_to_five += 1
	#print delay, count_to_five
	
	while elements:
		if elements[0] == '*' or elements[0] == "*\n":
			elements.pop(0)
			hops[hop_num][None] += 1
			count_to_five += 1
		else:
			delay = elements.pop(0)
			while delay[0] == "!":
				if elements:
					delay = elements.pop(0)
				else:
					delay = None
					break
								
			if delay is not None:
				try:
					delay = float(delay)
				except:
					delay = -1	

				count_to_five += 1
				#print delay, count_to_five
				hops[hop_num][routerIP].append(delay)

	if count_to_five >= 5:
		count_to_five = 0

for i in range(10):
	print '\n\n %%', i, len(hops[i])-1
	if len(hops[i]) > 10:
		continue
	c = 0
	for key in hops[i]:
		if key is not None:
			print "%% %s" % key
			print "d%i%i = ..." %(i, c)
			c += 1
			print  hops[i][key]
		else:
			print "%% no response count: %i" % hops[i][key]


for key in hops[1]:
	if key is not None:
		print len(hops[1][key])


print '\n\n', hops[7]
