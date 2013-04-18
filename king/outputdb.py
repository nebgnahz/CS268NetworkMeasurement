import MySQLdb, MySQLdb.cursors
import sqlalchemy.ext.serializer
import cPickle as pickle

connection = MySQLdb.connect(host = "data.cnobwey0khau.us-west-2.rds.amazonaws.com",
                             user = 'ucb_268_measure',
                             passwd = 'ucb_268_measure',
                             db = 'mydb',
                             ssl = {},
                             cursorclass = MySQLdb.cursors.SSCursor)

cur = connection.cursor()
cur.execute("SELECT count(*) from data;")
print 'Entries: %i' % cur.fetchone()
cur.close()

cur = connection.cursor()
cur.execute("SELECT * from data where success;")
for r in cur:
    id, timestamp, name1, name2, target1, target2, start, end, pings, address, test_point, success = r
    print 'Date of Measurement', timestamp
    print name1, name2
    print pickle.loads(target1)
    print pickle.loads(target2)
    print test_point
    print pickle.loads(address)
    print start
    print end
    print pickle.loads(pings)
    print '---------------------------------'
    break
cur.close()

#for r in s.query(DataPoint).filter(DataPoint.success == True,):

