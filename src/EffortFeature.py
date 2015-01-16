#coding=utf8

__author__ = 'luocheng'

import sqlite3
from Utils import loadValidUsers

cx = sqlite3.connect('../data/db.sqlite3')
cu = cx.cursor()

class Log:
    def __init__(self,id,studentid,taskid,action,query,content):
        self.id = id
        self.studentid = studentid
        self.taskid = taskid
        self.action = action
        self.query = query
        self.content = content

LOGLIST =list()
validusers=loadValidUsers()


cu.execute('select * from anno_log')
while True:
    one = cu.fetchone()
    if one == None:
        break
    else:
        id = one[0]
        sid = int(one[1])
        taskid = int(one[2])
        action = one[3]
        query = one[4]
        content = one[5]
        if sid in validusers:
            LOGLIST.append(Log(id,sid,taskid,action,query,content))
import re
from collections import defaultdict
def extractTime(s):
    tp = re.compile('TIME=(\d*)')
    time  = int(tp.search(s).group(1))
    return time



def extractSessionDwellTime():
    # begintime ,endtime  __stdentid__taskid__
    betime = defaultdict(lambda:defaultdict(lambda:[-1,-1]))

    for l in LOGLIST:
        if l.action =='BEGIN_SEARCH':
            betime[l.studentid][l.taskid][0] = extractTime(l.content)
        if l.action =='SEARCH_END':
            betime[l.studentid][l.taskid][1] = extractTime(l.content)
    fout = open('../data/sessionDwellTime.feature','w')
    for sid in betime.keys():
        for tid in range(1,13,1):
            fout.write('\t'.join([ str(item) for item in [sid,tid, betime[sid][tid][0],betime[sid][tid][1],betime[sid][tid][1]-betime[sid][tid][0],'\n']]))
    fout.close()

def extractQueryDwellTime():
    #begin, end studentid, taskid ,query,
    betime = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:[2E12,-1])))
    for l in LOGLIST:
        t = extractTime(l.content)
        sid = l.studentid
        tid = l.taskid
        q = l.query
        if t <  betime[sid][tid][q][0]:
            betime[sid][tid][q][0] = t
        if t >  betime[sid][tid][q][1]:
            betime[sid][tid][q][1] = t
    fout = open('../data/queryDwellTime.feature','w')
    for sid in validusers:
        for tid in range(1,13,1):
            for q in betime[sid][tid].keys():
                fout.write('\t'.join([str(item) for item in [sid,tid,q.encode('utf8'),betime[sid][tid][q][0],betime[sid][tid][q][1],betime[sid][tid][q][1]-betime[sid][tid][q][0],'\n']]))
    fout.close()

def extractSessionClicks():
    # #clicks studentid, taskid ,counts
    clicks = defaultdict(lambda:defaultdict(lambda:0))
    for l in LOGLIST:
        if l.action =='CLICK':
            clicks[l.studentid][l.taskid] +=1
    fout = open('../data/sessionClicks.feature','w')
    for sid in validusers:
        for tid in range(1,13,1):
            fout.write(str(sid)+'\t'+str(tid)+'\t'+str(clicks[sid][tid])+'\n')
    fout.close()

def extractQueryClicks():
    # #clicks studentid, taskid, query,counts
    clicks = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:0)))
    for l in LOGLIST:
        if l.action =='CLICK':
            clicks[l.studentid][l.taskid][l.query] +=1
    fout = open('../data/queryClicks.feature','w')
    for sid in validusers:
        for tid in range(1,13,1):
            for q in clicks[sid][tid].keys():
                fout.write(str(sid)+'\t'+str(tid)+'\t'+q.encode('utf8')+'\t'+str(clicks[sid][tid][q])+'\n')
    fout.close()

def extractFixation():
    # boundary
    bond = defaultdict(lambda:defaultdict(lambda:[0.0,0.0,0.0,0.0]))

    for l in open('../data/mouse_and_eye_new/result_pos.txt').readlines():
        d = dict()
        segs =l.strip().split('\t')
        if len(segs) >1:
            for s in segs:
                k,v = k.split('=')
                d[k] = v
            bond[d['query']][int(d['page'])] = [int(d['top']),int(d['bottom']),int(d['left']),int(d['right'])]
    # sid | tid |
    querieseq = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:dict())))
    
extractSessionDwellTime()
extractQueryDwellTime()
extractSessionClicks()
extractQueryClicks()
extractFixation()