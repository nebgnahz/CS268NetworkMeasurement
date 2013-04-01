import time, urlparse, socket, threading, subprocess
from urlparse import urlparse
from time import gmtime, strftime

class Command(object):
	def __init__(self, cmd, timeout):
		self.cmd = cmd
		self.timeout = timeout
		self.process = None
		
	def run(self):
		ts = time.time()
		src = socket.gethostbyname(socket.gethostname())
		dst = self.cmd[-1]

		def target():
			self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, err = self.process.communicate()

			logFile.write(err)
			logFile.write(out)
			logFile.write('\n\n')


		thread = threading.Thread(target=target)
		thread.start()

		thread.join(self.timeout)
		if thread.is_alive():
			print "terminating process"
			self.process.terminate()
			thread.join()

		# timeout sees -15, normal sees 0x
		print self.process.returncode

f = open('urllist.txt', 'r')
logFile = open(str(strftime("%Y-%m-%d %H:%M:%S", gmtime())), 'w')

for line in f:
	if line[0] == '#' or line[0] == '\n' or len(line) == 0:
		continue
	url = urlparse(line.partition(" ")[0])
	command = Command(['traceroute', '-aS', '-q 5', url.netloc], 30)
	command.run()

logFile.close()
