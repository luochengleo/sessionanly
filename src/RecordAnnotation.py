#coding=utf8
__author__ = 'luocheng'


import sqlite3

cx = sqlite3.connect('../data/db.sqlite3')
cu = cx.cursor()

cu.execute('select * from anno_recordannotation')
while True:
    one  = cu.fetchone()
    id = int(one[0])
    annotator = int(one[1])
    studentid = int(one[2])
    taskid = int(one[4])
    

