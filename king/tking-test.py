import rpyc
c = rpyc.connect('pl2.planetlab.ics.tut.ac.jp', 18861)
c.root.test()
a = c.root.get_latency('google.com','8.8.8.8','ns1.google.com','216.239.32.10')
