import subprocess, threading
from urlparse import urlparse
import json, time, socket, couchdb
from couch import Couch
from time import gmtime, strftime

class TracerouteLog:
	def __init__(self, src, dst, ts):
		self.src = src
		self.dst = dst
		self.ts = ts
		self.logEntries = []
		self.err = None
		
class TracerouteLogEntry:
	def __init__(self, index):
		self.index = index
		self.probes = []

class TraceProbeEntry:
	def __init__(self, ASN, rName, rIP, delay):
		self.ASNum = ASN
		self.routerName = rName
		self.routerIP = rIP
		self.delay = delay
		

class Command(object):
	def __init__(self, cmd, timeout):
		self.cmd = cmd
		self.timeout = timeout
		self.process = None
		
	def run(self):
		ts = time.time()
		src = socket.gethostbyname(socket.gethostname())
		dst = self.cmd[-1]
		log = TracerouteLog(src, dst, ts)

		def target():
			self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, err = self.process.communicate()

			logFile.write(err)
			logFile.write(out)
			logFile.write('\n\n')
			
			log.err = err
			counter = 0

			# the parsing process
			lines = out.split('\n')
			for line in lines:
				elements = line.split(' ')
				# remove space, remove 'ms'
				elements = filter (lambda a: a != '' and a != 'ms', elements)

				if len(elements) == 0:
					# not a valid line
					continue

				if counter == 0:
					# scan the index first, then create a TracerouteLogEntry
					print elements[0]
					newEntry = TracerouteLogEntry(elements.pop(0))
					while elements and elements[0] == '*':
						elements.pop(0)
						# time out for this probe
						print None, None, None, -1
						newEntry.probes.append(TraceProbeEntry(None, None, None, -1))
						counter += 1
					if counter == 5:
						log.logEntries.append(newEntry)
						counter = 0
						break

				if len(elements) == 0:
					# handle the case when timeout occurs, fill with "None"
					while counter < 5:
						print None, None, None, -1
						newEntry.probes.append(TraceProbeEntry(None, None, None, -1))
						counter += 1						
					continue

				# extract AS number first
				ASN = elements.pop(0)
				ASN = ASN[1:len(ASN)-1]
				routerName = elements.pop(0)
				routerIP = elements.pop(0)
				routerIP = routerIP[1:len(routerIP)-1]
				delay = elements.pop(0)
				print ASN, routerName, routerIP, delay
				newEntry.probes.append(TraceProbeEntry(ASN, routerName, routerIP, delay))
				counter += 1
				while elements:
					if counter == 5:
						break
					if elements[0] == '*':
						elements.pop(0)
						print None, None, None, -1
						newEntry.probes.append(TraceProbeEntry(None, None, None, -1))
						counter += 1
					else:
						delay =  elements.pop(0)
						print ASN, routerName, routerIP, delay
						newEntry.probes.append(TraceProbeEntry(ASN, routerName, routerIP, delay))
						counter += 1

				if counter >= 5:
					log.logEntries.append(newEntry)
					counter = 0

		thread = threading.Thread(target=target)
		thread.start()

		thread.join(self.timeout)
		if thread.is_alive():
			print "terminating process"
			self.process.terminate()
			thread.join()

		# timeout sees -15, normal sees 0x
		log.returnCode = self.process.returncode

		jsonString = json.dumps(log, default=lambda o: o.__dict__)
		print jsonString
		db.saveDoc('traceroute', jsonString)

		
f = open('urllist.txt', 'r')
db = Couch('localhost', '5984')
db.createDb('traceroute')

logFile = open(str(strftime("%Y-%m-%d %H:%M:%S", gmtime())), 'w')

for line in f:
	if line[0] == '#' or line[0] == '\n' or len(line) == 0:
		continue
	url = urlparse(line.partition(" ")[0])
	print "url     :", url.netloc
	print "comments:", line[line.index(' ') + 1:]
	command = Command(['traceroute', '-a', '-q 5', url.netloc], 20)
	command.run()

logFile.close()

