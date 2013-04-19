import MySQLdb, MySQLdb.cursors
import sqlalchemy.ext.serializer
import cPickle as pickle
from datetime import timedelta
from utilities import distance

import argparse
parser = argparse.ArgumentParser(description='Output db')
parser.add_argument('--csv', action='store_true', default=False, help='Output CSV file of data')
arguments = parser.parse_args()

connection = MySQLdb.connect(host = "data.cnobwey0khau.us-west-2.rds.amazonaws.com",
                             user = 'ucb_268_measure',
                             passwd = 'ucb_268_measure',
                             db = 'mydb',
                             ssl = {},
                             cursorclass = MySQLdb.cursors.SSCursor)

cur = connection.cursor()
cur.execute("SELECT * from data where success;")
if arguments.csv:
    print 'distance, latency'
    for r in cur:
        id, timestamp, name1, name2, target1, target2, start, end, pings, address, test_point, success = r

        target1 = pickle.loads(target1)
        target2 = pickle.loads(target2)
        
        dist = distance(target1[2], target2[2])

        start = pickle.loads(start)
        end = pickle.loads(end)
        pings = pickle.loads(pings)
        latency = (end - start - sum(pings, timedelta())/len(pings)).total_seconds()

        address = pickle.loads(address)
        

        if latency >= 0 and target1[1] == address[0]:
            print dist, ',', latency
    cur.close()
else:
    for r in cur:
        id, timestamp, name1, name2, target1, target2, start, end, pings, address, test_point, success = r
        print 'Date of Measurement', pickle.loads(timestamp)
        print 'Target1:', name1, pickle.loads(target1)
        print 'Target2:', name2, pickle.loads(target2)
        print 'Test Point:', test_point
        print 'Response Address', pickle.loads(address)
        print 'Start:', pickle.loads(start)
        print 'End:', pickle.loads(end)
        print 'Pings:', pickle.loads(pings)
        print '---------------------------------'
    cur.close()
    cur = connection.cursor()
    cur.execute("""SELECT
    	               SUM(IF(success, 1, 0)),
    	               SUM(IF(not success, 1, 0))
                   FROM data;""")
    num_success, num_fail = cur.fetchone()
    percent = float(num_success)/float(num_fail+num_success)
    print 'Success %i, Fail %i, Success Rate %s' % (num_success, num_fail, "{0:.0f}%".format(percent * 100)) 
    cur.close()