#!/usr/bin/python
import socket
import sqlite3

# GeoCityBlocks
#   startIpNum integer, endIpNum integer, locId integer
# GeoCityLocation 
#   locId integer, country text, region text, city text, postalCode text, latitude real, longitude real, metroCode text, areaCode text
def iptoint(ip):
	return int(socket.inet_aton(ip).encode('hex'),16)

def ip_db_lookup(ip):
	ip_int = iptoint(ip)
	conn = sqlite3.connect('GeoIP.db')
	c = conn.cursor()
	
	results = c.execute('''select city, latitude, longitude from GeoCityLocation where locId = (select locId from GeoCityBlocks where startIpNum <= %i and endIpNum >= %i);''' % (ip_int, ip_int))

	

	for row in results:
		city, latitude, longitude = row
		# a hacky design
		conn.close()
		return city, latitude, longitude



	
if __name__ == "__main__":
	ip_db_lookup('173.244.215.183')
