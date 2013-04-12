"""All sorts of geo utils for measurement project
"""
import math, sys, getopt

def distance(origin, destination, radius = 6371):
	"""Based on Haversine formula, default return result is kilometers"""
	# The Haversine formula is an equation that can be used to find great-circle distances between two points on a sphere from their longitudes and latitudes.
	#  When this formula is applied to the earth the results are an approximation because the Earth is not a perfect sphere. 
	# The currently accepted (WGS84) radius at the equator is 6378.137 km and 6356.752 km at the polar caps. For aviation purposes the FAI uses a radius of 6371.0 km
	lat1, lon1 = origin
	lat2, lon2 = destination
	
	dlat = math.radians(lat2 - lat1)
	dlon = math.radians(lon2 - lon1)
	a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
			* math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	d = radius * c
	return d
	
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


	seattle = [47.621800, -122.350326]
	olympia = [47.041917, -122.893766]
	print "distance:", distance(seattle, olympia)
