import string

lines = [
    ((51.0, 9.0), (52.5167, 13.4)),
    ((50.0833, 19.9167), (50.0833, 19.9167)),
    ((52.0, 20.0), (52.22977, 21.01178)),
    ((40.6224, -74.3124), (40.5516, -74.4637)),
    ((43.6667, -79.4167), (60.10867, -113.64258)),
    ((-10.0, -55.0), (-26.75, -53.5667)),
    ((62.0, 15.0), (62, 15)),
    ((-10.0, -55.0), (-23.5475, -46.63611)),
    ((52.5, 5.75), (52.37403, 4.88969)),
    ((40.4426, -79.977), (40.4426, -79.977))
]

print '<?xml version="1.0" encoding="UTF-8"?>'
print '<kml xmlns="http://earth.google.com/kml/2.2">'
print '    <Document>'
print '       <Folder>'

for (lat1, log1), (lat2, log2) in lines:
    print "<Placemark><LineString><coordinates>"
    print log1, ',', lat1, ', 0'
    print log2, ',', lat2, ', 0'
    print "</coordinates></LineString></Placemark>"
print '        </Folder>'
print '    </Document>'
print '</kml>'
