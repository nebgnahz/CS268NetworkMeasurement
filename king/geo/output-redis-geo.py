from redis import ConnectionPool, Redis
import sys
from ast import literal_eval

try:
  db_dns = Redis(connection_pool=ConnectionPool(host='localhost', port=6379, db=1))
  db_geo = Redis(connection_pool=ConnectionPool(host='localhost', port=6379, db=2))
except:
  sys.exit(1)    

dns_keys = db_dns.keys()

print '<?xml version="1.0" encoding="UTF-8"?>'
print '<kml xmlns="http://earth.google.com/kml/2.2">'
print '    <Document>'
print '       <Folder>'

for key in dns_keys:
  geo_info = db_geo.smembers(key)
  for g in geo_info:
    city, lat, log = literal_eval(g)
    print "<Placemark><Point><coordinates>"
    print log, ',', lat, ', 0'
    print "</coordinates></Point></Placemark>"
print '        </Folder>'
print '    </Document>'
print '</kml>'

  



  
