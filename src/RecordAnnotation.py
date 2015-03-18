#coding=utf8
__author__ = 'luocheng'


import sqlite3
import math


# ljd = logarithm of the score assigned by judge j to document d
# J the total number of all judges( unique)
# sjd = 10^(ljd + u - uj)
# uj =  1/n*(sigma{d} ljd)
# u = all documents


cx = sqlite3.connect('../data/db.sqlite3')
cu = cx.cursor()

from collections import defaultdict

sid2tid2annotaion = defaultdict(lambda:defaultdict(lambda:dict()))
aid2sum = defaultdict(lambda:0.0)
cu.execute('select * from anno_recordannotation')
while True:
    one  = cu.fetchone()
    if one ==None:
        break
    else:
        id = int(one[0])
        annotator = int(one[1])
        studentid = int(one[2])
        taskid = int(one[3])
        score = int(one[4])
        if score ==0:
            print 'exception',studentid,annotator
            score =60

        sid2tid2annotaion[studentid][taskid][annotator] = math.log10(float(score))

for s in sid2tid2annotaion.keys():
    for t in sid2tid2annotaion[s].keys():
        for a in sid2tid2annotaion[s][t].keys():
            aid2sum[a]+= sid2tid2annotaion[s][t][a]


aid2mean = defaultdict(lambda:0.0)
for k in aid2sum.keys():
    aid2mean[k] = aid2sum[k]/(12.0*29.0)
    print 'aid2mean[k]',aid2mean[k]
gloablmean = sum(aid2sum[item] for item in aid2sum.keys())/(12.0*3.0*29.0)


fout = open('../data/recordannotation_processed.dat','w')

sid2tid2normanno = defaultdict(lambda:defaultdict(lambda:dict()))

for s in sid2tid2annotaion.keys():
    for t in sid2tid2annotaion[s].keys():
        if len(sid2tid2annotaion[s][t].keys())!=3:
            print s,t,sid2tid2annotaion[s][t]
        for a in sid2tid2annotaion[s][t].keys():
            fout.write(str(s)+'\t'+str(t)+'\t'+str(a)+'\t'+str(gloablmean)+'\t'+str(aid2mean[a])+'\t'+str(sid2tid2annotaion[s][t][a])+'\t'+str(10**(sid2tid2annotaion[s][t][a]+gloablmean-aid2mean[a]))+'\n')
            sid2tid2normanno[s][t][a] = 10**(sid2tid2annotaion[s][t][a]+gloablmean-aid2mean[a])
fout.close()

aid2annotations = defaultdict(lambda:list())
for s in sid2tid2annotaion.keys():
    for t in sid2tid2annotaion[s].keys():
        for a in sid2tid2annotaion[s][t].keys():
            aid2annotations[a].append(sid2tid2normanno[s][t][a])

from scipy.stats.stats import pearsonr
from scipy.stats.stats import kendalltau


annotators = list(aid2annotations.keys())
from  itertools import permutations
for i in permutations(annotators,2):
    print i[0],i[1],pearsonr(aid2annotations[i[0]],aid2annotations[i[1]])[0],kendalltau(aid2annotations[i[0]],aid2annotations[i[1]])[0]

# ----------------------------------------------------------
# 下面load 用户的主观打分，和标注人员的客观打分计算kappa correlation
#
#
# ----------------------------------------------------------

def loadValidUsers():
    u = set()
    for l in open('../data/validusers.txt').readlines():
        u.add(int(l.strip()))
    return u
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
querysatis = defaultdict(lambda:defaultdict(lambda:list()))

sessionsatis = defaultdict(lambda:defaultdict(lambda:1))
validUsers = loadValidUsers()

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
            querysatis[studentID][task_id].append(score)
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
            sessionsatis[studentID][task_id]=score
            print studentID,task_id,score
        else:
            print 'invalid studentID',studentID

def personSpecific(sid):
    queryseq = list()
    sessionseq = list()
    for tid in querysatis[sid]:
        for item in querysatis[sid][tid]:
            queryseq.append(item)
    for tid in sessionsatis[sid]:
        sessionseq.append(sessionsatis[sid][tid])
    return mean(queryseq),variance(queryseq),mean(sessionseq),variance(sessionseq)

user_parameters = dict()
for sid in validUsers:
    user_parameters[sid] =  personSpecific(sid)

mout = open('../data/recordscore.txt','w')
mout.write('studentid\ttaskid\traw_sessionsatis\tzscore_sessionsatis\tmeanannoscore\n')
zhuguan = list()
keguan = list()
for s in validUsers:
    for t in range(1,13,1):

        mout.write(str(s)+'\t'+str(t)+'\t'+str(sessionsatis[s][t])+'\t')
        mout.write(str((sessionsatis[s][t]-user_parameters[s][2])/user_parameters[s][3]))
        mout.write('\t')
        mout.write(str(mean([sid2tid2normanno[s][t][a] for a in annotators])))
        mout.write('\n')

        zhuguan.append((sessionsatis[s][t]-user_parameters[s][2])/user_parameters[s][3])
        keguan.append(mean([sid2tid2normanno[s][t][a] for a in annotators]))

print pearsonr(zhuguan,keguan)[0],pearsonr(zhuguan,keguan)[1]
print kendalltau(zhuguan,keguan)[0],kendalltau(zhuguan,keguan)[1]

for a in annotators:
    print a,pearsonr(aid2annotations[a],keguan),kendalltau(aid2annotations[a],keguan)

mout.close()


0.0865330183809 0.107077626977
0.05773893991   0.10792897429