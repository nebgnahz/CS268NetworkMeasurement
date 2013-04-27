import string

pl_hosts = [line.split(' ')[2:4] for line in map(string.strip,open('../pl-host-list-geo').readlines())]

print '<?xml version="1.0" encoding="UTF-8"?>'
print '<kml xmlns="http://earth.google.com/kml/2.2">'
print '    <Document>'
print '       <Folder>'

for lat, log in pl_hosts:
    print "<Placemark><Point><coordinates>"
    print log, ',', lat, ', 0'
    print "</coordinates></Point></Placemark>"
print '        </Folder>'
print '    </Document>'
print '</kml>'
