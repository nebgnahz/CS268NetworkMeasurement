import time, urlparse, socket, threading, subprocess, argparse
from urlparse import urlparse
from time import gmtime, strftime

parser = argparse.ArgumentParser(description='Traceroute Logging; logFile is under logs, named by time')
parser.add_argument('-m', action='store', dest='message', default="", help='add comments to the log')

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
		if (self.process.returncode == 0):
			print "succeeded"
		elif (self.process.returncode == -15):
			print "timeout"
		else:
			print "check this traceroute manually:", self.cmd
			
		
arguments = parser.parse_args()

f = open('urllist.txt', 'r')
logFile = open(str(strftime("./logs/%Y-%m-%d %H:%M:%S")), 'w')
logFile.write( '# %s\n\n' % (arguments.message) )
count = 0

for line in f:
	if line[0] == '#' or line[0] == '\n' or len(line) == 0:
		continue

	count += 1
	url = urlparse(line.partition(" ")[0])
	print "[%i] traceroute to %s" % (count, url.netloc)
	command = Command(['traceroute', '-a', '-q 5', url.netloc], 30)
	command.run()

logFile.close()
