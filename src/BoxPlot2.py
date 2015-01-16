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

def getMeanAndStddev(lt):
    if len(lt) ==0:
        return 0.0,0.0
    else:
        if len(lt) ==1:
            return lt[0],0.0
        else:
            return mean(lt),variance(lt)/len(lt)**0.5

# querysatis [student id][task id] -> score list
# sessionsatis[ student id][task id] -> session satisfaction score
querysatis  = defaultdict(lambda:defaultdict(lambda:list()))
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

#对session level的Satisfaction进行归一化，然后分析不同position上的满意

position2satisfaction = defaultdict(lambda :list())

for sid in querysatis.keys():
    for tid in querysatis[sid].keys():
        for i in range(1,len(querysatis[sid][tid])+1,1):
            position2satisfaction[i].append( (querysatis[sid][tid][i-1] - user_parameters[sid][0])/user_parameters[sid][1])

def getMeanAndStddev(lt):
    if len(lt) ==0:
        return 0.0,0.0
    else:
        if len(lt) ==1:
            return lt[0],0.0
        else:
            return mean(lt),variance(lt)/len(lt)**0.5
meanlist = list()
varlist = list()
lenlist = list()

for i in range(1,10,1):
    m,v = getMeanAndStddev(position2satisfaction[i])
    l = len(position2satisfaction[i])
    meanlist.append(m)
    varlist.append(v)
    lenlist.append(l)
x_label = ('1','2','3','4','5','6','7','8','9')
y_pos = np.arange(len(x_label))
rects = plt.bar(y_pos,meanlist,yerr=varlist,align='center')
plt.xticks(y_pos,x_label)
plt.ylabel('Satisfaction Level')
plt.xlabel('Position')
plt.title('Mean Query SAT on Different Positions')
i = 0
for rect in rects:
    height = rect.get_height()
    l = lenlist[i]
    i+=1
    plt.text(rect.get_x()+rect.get_width()/2., -0.5, '%d'%int(l),
                ha='center', va='bottom')
# plt.savefig('../figure/MeanQuerySatisfactionOnDifferentPosition/'+str(i)+'.png')
plt.show()
plt.close()
