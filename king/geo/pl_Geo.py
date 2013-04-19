"""run with python pl_Geo.py > file_to_save
"""

from GeoIP import ip_db_lookup
import socket, sys, getopt

pl_filename = "../pl-host-list"

def main():
	try:
		plfile = open(pl_filename, 'r')
	except:
		print "[ERROR]: planet lab list not found. \n"
		return
	for line in plfile:
		try:
			ip = socket.gethostbyname(line.rstrip())
			city, latitude, longtitude = ip_db_lookup(ip)
			print line.rstrip(), ip, latitude, longtitude, city
		except:
			pass
	

if __name__ == "__main__":
	#  parse command line options
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

	main()
