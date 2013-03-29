import rpyc
conn = rpyc.connect('pl2.planetlab.ics.tut.ac.jp', 18861)
conn.root.test()
a = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')
b = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')
c = conn.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')

print a, b, c
