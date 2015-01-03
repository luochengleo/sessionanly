__author__ = 'cheng'

import sqlite3
cx = sqlite3.connect("../data/db.sqlite3")
cu = cx.cursor()

print 'looking up in database'
cu.execute('select * from anno_log where studentID=2012310575')
print 'executing...'
while True:
    logpiece =  cu.fetchone()
    if logpiece == None:
        break
    else:
        print logpiece


