#coding=utf8
__author__ = 'luocheng'
import numpy as np
import pylab as pl
import sqlite3
import matplotlib.pyplot as plt
from collections import defaultdict
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

def loadValidUsers():
    u = set()
    for l in open('../data/validusers.txt').readlines():
        u.add(int(l.strip()))
    return u

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
def formalize(lt):
    return lt
    # return [(float(item)-mean(lt))/variance(lt) for item in lt]

user_parameters = dict()
for sid in validUsers:
    user_parameters[sid] =  personSpecific(sid)


# 按照task输出sCG  /  sCG/#queries随着query增多的变化
for sid in querysatis.keys():
    for tid in querysatis[sid]:
        formalized_query = list()
        for item in querysatis[sid][tid]:
            # formalized_query.append((float(item) - user_parameters[sid][0])/user_parameters[sid][1])
            formalized_query.append(float(item))

        xseq = range(1,len(formalized_query)+1,1)
        yseq = list()
        for item in xseq:
            yseq.append(mean(formalized_query[:item]))

        plt.xlim(0,12)
        plt.ylim(0,5)

        plt.subplot(3,4, tid)
        plt.plot(xseq,yseq)

for i in range(1,13,1):
    plt.subplot(3,4,i)
    plt.title("TASK "+str(i),loc='left')
plt.show()
plt.close()

# 按照user 输出sCG / sCG/#queries 随着query增多的变化
for sid in validUsers:
    for tid in querysatis[sid]:
        formalized_query = list()
        for item in querysatis[sid][tid]:
            # formalized_query.append((float(item) - user_parameters[sid][0])/user_parameters[sid][1])
            formalized_query.append(float(item))
        xseq = range(1,len(formalized_query)+1,1)
        yseq = list()
        for item in xseq:
            yseq.append(mean(formalized_query[:item]))

        plt.xlim(0,12)
        plt.ylim(0,5)
        plt.plot(xseq,yseq)

    plt.title("sID "+str(sid),loc='left')
    plt.savefig('../figure/sCG_nq_byUser/sCG_nq_vsQueryNumber_'+str(sid)+'.png')
    plt.close()


for sid in querysatis.keys():
    for tid in querysatis[sid]:
        formalized_query = list()
        for item in querysatis[sid][tid]:
            formalized_query.append(float(item))
            # formalized_query.append((float(item) - user_parameters[sid][0])/user_parameters[sid][1])

        xseq = range(1,len(formalized_query)+1,1)
        yseq = list()
        for item in xseq:
            yseq.append(sum(formalized_query[:item]))
        sSatisfaction = sessionsatis[sid][tid]
        plt.subplot(2,3,sSatisfaction)
        plt.xlim(0,12)
        plt.ylim(0,45)
        plt.title("Session Satisfaction="+str(sSatisfaction))
        plt.plot(xseq,yseq)

for i in range(1,6,1):
    plt.subplot(2,3,i)
    # plt.title('Session Satisfaction(original) = '+str(i))
plt.show()
# plt.savefig('../figure/bysession/sCGvsSessionSatisfaction.png')