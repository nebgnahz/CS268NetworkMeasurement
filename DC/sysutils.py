#!/usr/bin/env python

"""
Ping wrapper for system ping (Unix machine)

"""
import sys, getopt, time, socket, re, os, signal
import threading, subprocess, logging
from datetime import timedelta

class Command(object):
	def __init__(self, cmd, timeout):
		self.cmd = cmd
		self.timeout = timeout
		self.process = None
		self.out = None
		self.err = None
		self.returncode = None
		
	def run(self):
		def target():
			self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			self.out, self.err = self.process.communicate()

		thread = threading.Thread(target=target)
		thread.start()

		thread.join(self.timeout)
		if thread.isAlive():
			logging.debug("terminating process")
			# python 2.5 doesn't have process.terminate
			os.kill(self.process.pid, signal.SIGTERM)
			thread.join()

		# timeout sees -15, normal sees 0x
		if (self.process.returncode == 0):
			logging.debug("succeeded")
		elif (self.process.returncode == -15):
			logging.debug("timeout")
		else:
			logging.debug("check this command manually: %s", self.cmd)
		self.returncode = self.process.returncode
			

def ping(dst, count = 10, timeout = 30):
	""" This is a wrapper function to the system ping.

	It opens a new subprocess, and passes the parameter.
	The implementation involves a threading solution, so that timeout value can be specified.
	"""	
	pingTimes = []
	logging.debug("ping %s (%i times)", dst, count)
	command = Command(['ping', '-n', '-c', str(count), dst], timeout)
	command.run()
	# when it's executing here, the results have been available
	if command.out is not None:
		pattern = "time=([0-9]+\.[0-9]+) ms"
		lines = command.out.split('\n')
		for line in lines:
			pingTime = re.search(pattern, line)
			try:
				pingTimes.append(float(pingTime.group(1)))
			except:
				pass

		return command.returncode, pingTimes

def tcpdump(timeout, q, interface):
	""" This is a wrapper function to the system tcpdump.

	It opens a new subprocess, and passes the parameter.
	The implementation involves a threading solution, so that timeout value can be specified.
	"""	
	logging.debug('tcpdump -s 1024 -lqnAt tcp port 80 -i eth0')
	# tcpdump -s 1024 -lqnAt tcp port 80
		
	command = Command(['/usr/sbin/tcpdump', '-s 1024', '-lnAq', '-i', interface], timeout)
	command.run()

	# when it's executing here, the results have been available
	# print command.out

	if command.out is not None:
		# pattern = "time=([0-9]+\.[0-9]+) ms"
		ip_pattern = "IP ([0-9]+.[0-9]+.[0-9]+.[0-9]+).[0-9]+ > [0-9]+.[0-9]+.[0-9]+.[0-9]+.[0-9]"
		google_pattern = "domain=.google.com"
		lines = command.out.split('\n')
		last_ip = None

		# first time scan for google's return ip
		for line in lines:
			ip_src = re.search(ip_pattern, line)
			if ip_src is not None:
				last_ip = ip_src.group(1)
			if re.search(google_pattern, line):
				print last_ip
				break

		gEntries = []
		if last_ip is not None:
			
			# second time scan parse tcpdump for query entries
			for line in lines:
				last_ip_pos = re.search(last_ip, line)
				if last_ip_pos is None:
					continue
			
				if line.index('>') > last_ip_pos.start():
					# from remote to this place
					traffic_type = 1			
				else:
					# out to remote
					traffic_type = 0
			
				time_pattern = "([0-9]+:[0-9]+:[0-9]+.[0-9]+) IP"
				timestamp = re.search(time_pattern, line)
				time_str = timestamp.group(1)
				h, m, s, ms = map(int, re.split(r'[.:]+', time_str))
				timestamp_delta = timedelta(hours=h, minutes=m, seconds=s, microseconds=ms)
				gEntries.append( (timestamp_delta, traffic_type) )
				# print line

		q.put((command.returncode, last_ip, gEntries))
		return
	
if __name__=='__main__':
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

	tcpdump()
	## process arguments
	# for arg in args:
	#	print ping(arg, 10)
		
