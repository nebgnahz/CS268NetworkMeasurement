# example usage: python mobile-geo.py > mobile.csv

from GeoIP import ip_db_lookup
import pickle

exit_points = pickle.load( open( "../../mobile/dst_exit.p", "r" ))


print '<?xml version="1.0" encoding="UTF-8"?>'
print '<kml xmlns="http://earth.google.com/kml/2.2">'
print '    <Document>'
print '       <Folder>'

for key in exit_points:
  name, dst_ip = key
  n, asn, ip = exit_points[key][0]
  # print '%d, ' % n,

  print "<Placemark>",
  print "<name>%s</name>" % name

  city1, lat1, lon1 = ip_db_lookup(dst_ip)
  # print '%s, %s, %s, %s, ' % (dst_ip, city1, lat1, lon1),

  city2, lat2, lon2 = ip_db_lookup(ip)
  # print '%s, %s, %s, %s' % (ip, city2, lat2, lon2)

  print '<LineString><coordinates>'
  print lon1, ',', lat1, ', 0'
  print lon2, ',', lat2, ', 0'
  print "</coordinates></LineString>"
  print "</Placemark>" 

print '        </Folder>'
print '    </Document>'
print '</kml>'
 # 70.42.185.10	 San Francisco	37.7697	-122.3933	  208.175.172.10	 Chesterfield	38.65	-90.5334



#  % traceroute -a reference.com 
# traceroute to reference.com (66.235.120.211), 64 hops max, 52 byte packets
#  1  [AS0] 172.20.10.1 (172.20.10.1)  0.927 ms  0.642 ms  0.477 ms
#  2  [AS16509] 172.26.242.133 (172.26.242.133)  36.689 ms  30.317 ms  35.074 ms
#  3  [AS16509] 172.26.236.2 (172.26.236.2)  25.838 ms  29.971 ms  31.606 ms
#  4  [AS0] 172.26.96.2 (172.26.96.2)  28.391 ms  27.886 ms  29.280 ms
#  5  [AS0] 172.26.96.193 (172.26.96.193)  30.280 ms  49.540 ms  28.846 ms
#  6  [AS0] 172.16.120.50 (172.16.120.50)  35.119 ms  31.004 ms  32.317 ms
#  7  [AS7018] 12.249.2.53 (12.249.2.53)  26.373 ms  34.862 ms  32.519 ms
#  8  [AS7018] 12.83.180.94 (12.83.180.94)  103.892 ms  107.387 ms  113.005 ms
#  9  [AS7018] cr1.sffca.ip.att.net (12.122.3.69)  106.870 ms  95.033 ms  104.060 ms
# 10  [AS7018] cr1.cgcil.ip.att.net (12.122.4.122)  109.386 ms  106.220 ms  108.469 ms
# 11  [AS7018] cr2.wswdc.ip.att.net (12.122.18.22)  100.918 ms  102.278 ms  103.591 ms
# 12  [AS7018] 12.123.10.137 (12.123.10.137)  97.787 ms  104.401 ms  102.540 ms
# 13  * * *
# 14  [AS10913] border10.pc1-bbnet1.wdc002.pnap.net (216.52.127.9)  197.034 ms
#     [AS10913] border10.pc2-bbnet2.wdc002.pnap.net (216.52.127.73)  106.194 ms  105.049 ms
# 15  * * *
# ...
