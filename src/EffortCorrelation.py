#coding=utf8
import sqlite3
from scipy.stats.stats import pearsonr
from scipy.stats.stats import kendalltau
__author__ = 'Cheng'

from collections import defaultdict
import sqlite3

def mean(lt):
    sum = 0.0
    for item in lt:
        sum += float(item)
    return sum/ max(1.0,float(len(lt)))
def variance(lt):
    d = 0.0
    m = mean(lt)
    for item in lt:
        d += (float(item)-m)**2
    return (d/max(1.0,float(len(lt))))**0.5


sid2tid2satlist = defaultdict(lambda:defaultdict(lambda:list()))
sid2tid2ssat = defaultdict(lambda:defaultdict(lambda:1))
def loadValidUsers():
    u = set()
    for l in open('../data/validusers.txt').readlines():
        u.add(int(l.strip()))
    return u
validUsers = loadValidUsers()
for u in validUsers:
    print u
cx = sqlite3.connect("../data/db.sqlite3")
cu = cx.cursor()

cu.execute('select * from anno_querysatisfaction')

while True:
    logpiece =  cu.fetchone()
    if logpiece == None:
        break
    else:
        id = logpiece[0]
        studentID = int(logpiece[1])
        task_id = logpiece[2]
        query = logpiece[3]
        score = int(logpiece[4])
        if studentID in validUsers:
            sid2tid2satlist[studentID][task_id].append(score)
            print studentID,task_id,score

        else:
            print 'invalid studentID',studentID
cu.execute('select * from anno_sessionannotation')
while True:
    logpiece =  cu.fetchone()
    if logpiece == None:
        break
    else:
        id = logpiece[0]
        studentID = int(logpiece[1])
        task_id = logpiece[2]
        score = int(logpiece[3])
        if studentID in validUsers:
            sid2tid2ssat[studentID][task_id]=score
            print studentID,task_id,score
        else:
            print 'invalid studentID',studentID

def personSpecific(sid):
    queryseq = list()
    sessionseq = list()
    for tid in sid2tid2satlist[sid]:
        for item in sid2tid2satlist[sid][tid]:
            queryseq.append(item)
    for tid in sid2tid2ssat[sid]:
        sessionseq.append(sid2tid2ssat[sid][tid])
    return mean(queryseq),variance(queryseq),mean(sessionseq),variance(sessionseq)

# correlation between session dwell time and satisfaction
sessionDwellTime = list()
sessionSatisfaction = list()
sid2tid2sessionDwelltime= defaultdict(lambda:defaultdict(lambda:0.0))
for l in open('../data/sessionDwellTime.feature').readlines():
    segs = [int(item) for item in l.strip().split('\t')]
    sid2tid2sessionDwelltime[segs[0]][segs[1]] = segs[4]
for s in validUsers:
    for t in range(1,13,1):
        sessionDwellTime.append(sid2tid2sessionDwelltime[s][t])
        _ssat = sid2tid2ssat[s][t]
        _ssat = (_ssat-personSpecific(s)[2])/personSpecific(s)[3]
        sessionSatisfaction.append(_ssat)
print 'Satisfaction(User) correlation with session Dwell time'
print pearsonr(sessionDwellTime,sessionSatisfaction)
print kendalltau(sessionDwellTime,sessionSatisfaction)
