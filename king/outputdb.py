import MySQLdb, MySQLdb.cursors
import sqlalchemy.ext.serializer

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
    for att in r:
        print '--------'
        print att
    break
cur.close()

#for r in s.query(DataPoint).filter(DataPoint.success == True,):
#    print r.id
#    print 'Date of Measurement', self.r.timestamp
#    print r.name1, self.r.name2
#    print r.target1
#    print r.target2
#    print r.test_point
#    print r.address
#    print r.start
#    print r.end
#    print r.pings
#    print '---------------------------------'
