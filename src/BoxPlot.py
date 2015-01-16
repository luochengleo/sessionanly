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

# querysatis [student id][task id] -> score list
# sessionsatis[ student id][task id] -> session satisfaction score
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



# 考察每一个satisfaction level 上的平均查询数量

sessionsatis2querynum = defaultdict(lambda:list())
for sid in sessionsatis.keys():
    for tid in sessionsatis[sid].keys():
        _sessionsatis = sessionsatis[sid][tid]
        _querynum = len(querysatis[sid][tid])
        sessionsatis2querynum[_sessionsatis].append(_querynum)

s_label = ('1','2','3','4','5')
y_pos = np.arange(len(s_label))

qnum = list()
for item in s_label:
    qnum.append(mean(sessionsatis2querynum[int(item)]))
error = list()
for item in s_label:
    if len(sessionsatis2querynum[int(item)])==1:
        error.append(0.0)
    else:
        error.append(variance(sessionsatis2querynum[int(item)])/len(sessionsatis2querynum[int(item)])**0.5)

plt.barh(y_pos, qnum, xerr=error, align='center', alpha=0.4)
plt.yticks(y_pos, s_label)
plt.xlabel('#queries')
plt.ylabel('Satisfaction Level')
plt.title('#queries on different session satisfaction levels')
plt.show()
plt.close()


# 考察每一个satisfaction level 上的平均session内点击结果数量
ResultAnnotation = defaultdict(lambda:defaultdict(lambda:list()))
cu.execute('select * from anno_annotation')
while True:
    logpiece =  cu.fetchone()
    if logpiece == None:
        break
    else:
        id = logpiece[0]
        studentID = int(logpiece[1])
        task_id = logpiece[2]
        query = logpiece[3]
        result_id = logpiece[4]
        score = int(logpiece[6])

        if studentID in validUsers:
            ResultAnnotation[studentID][task_id].append((query,result_id,score))
        else:
            print 'invalid studentID',studentID

sessionsatis2clickresultsnum = defaultdict(lambda:list())
for sid in ResultAnnotation.keys():
    for tid in ResultAnnotation[sid].keys():
        _sessionsatis = sessionsatis[sid][tid]
        _clickedResultNum = len(set(ResultAnnotation[sid][tid]))
        sessionsatis2clickresultsnum[_sessionsatis].append(_clickedResultNum)

s_label = ('1','2','3','4','5')
y_pos = np.arange(len(s_label))
rnum = list()
for item in s_label:
    rnum.append(mean(sessionsatis2clickresultsnum[int(item)]))
error = list()
for item in s_label:
    if len(sessionsatis2clickresultsnum[int(item)])==1:
        error.append(0.0)
    else:
        error.append(variance(sessionsatis2clickresultsnum[int(item)])/len(sessionsatis2clickresultsnum[int(item)])**0.5)

plt.barh(y_pos, rnum, xerr=error, align='center', alpha=0.4)
plt.yticks(y_pos, s_label)
plt.xlabel('#(clicked results)')
plt.ylabel('Satisfaction Level')
plt.title('#(clicked results) on different session satisfaction levels')
plt.show()
plt.close()


#考察不同的session Satisfaction level下，用户最深点击位置和满意度
sessionsatis2maxClickPosition = defaultdict(lambda:list())
for sid in ResultAnnotation.keys():
    for tid in ResultAnnotation[sid].keys():
        _sessionsatis = sessionsatis[sid][tid]
        _maxClickedPosition = max([int(item[1].split('_')[1])+1 for item in ResultAnnotation[sid][tid]])
        sessionsatis2maxClickPosition[_sessionsatis].append(_maxClickedPosition)

s_label = ('1','2','3','4','5')
y_pos = np.arange(len(s_label))
rnum = list()
for item in s_label:
    rnum.append(mean(sessionsatis2maxClickPosition[int(item)]))
error = list()
for item in s_label:
    if len(sessionsatis2maxClickPosition[int(item)])==1:
        error.append(0.0)
    else:
        error.append(variance(sessionsatis2maxClickPosition[int(item)])/len(sessionsatis2maxClickPosition[int(item)])**0.5)

plt.barh(y_pos, rnum, xerr=error, align='center', alpha=0.4)
plt.yticks(y_pos, s_label)
plt.xlabel('max click position')
plt.ylabel('Satisfaction Level')
plt.title('Max Click Position on different session satisfaction levels')
plt.show()
plt.close()

# 考察在不同的session Satisfaction下，top 5 query的satisfaction box graph

ssatis2position2satisfaction = defaultdict(lambda:defaultdict(lambda :list()))
for sid in querysatis.keys():
    for tid in querysatis[sid].keys():
        for i in range(1,len(querysatis[sid][tid])+1,1):
            _ssat = sessionsatis[sid][tid]
            ssatis2position2satisfaction[_ssat][i].append(querysatis[sid][tid][i-1])

def getMeanAndStddev(lt):
    if len(lt) ==0:
        return 0.0,0.0
    else:
        if len(lt) ==1:
            return lt[0],0.0
        else:
            return mean(lt),variance(lt)/len(lt)**0.5
for i in range(2,6,1):
    print 'Sesssion Satisfaction Level = ',i
    meanvalue = list()
    error = list()
    numOfSessions = len(ssatis2position2satisfaction[i][1])
    s_label = ('1','2','3','4','5')
    y_pos = np.arange(len(s_label))
    for item in s_label:
        m,d = getMeanAndStddev(ssatis2position2satisfaction[i][int(item)])
        meanvalue.append(m)
        error.append(d)
    plt.bar(y_pos,meanvalue,yerr=error,align='center',alpha=0.4)
    plt.yticks(y_pos,s_label)
    plt.ylabel('Satisfaction Level')
    plt.xlabel('Position')
    plt.title('Mean Query SAT when Satisfaction Level = '+str(i)+'(#session ='+str(numOfSessions)+')')
    plt.savefig('../figure/MeanQuerySatisfactionOnDifferentPosition/'+str(i)+'.png')
    plt.close()

colors = ['r','b','g','y']
recs = list()
for i in range(2,6,1):
    print 'Sesssion Satisfaction Level = ',i
    meanvalue = list()
    error = list()
    numOfSessions = len(ssatis2position2satisfaction[i][1])
    s_label = ('1','2','3','4','5')
    y_pos = np.arange(len(s_label))
    for item in s_label:
        m,d = getMeanAndStddev(ssatis2position2satisfaction[i][int(item)])
        meanvalue.append(m)
        error.append(d)
    r = plt.bar(y_pos+(i-2)*0.2,meanvalue,yerr=error,width=0.2,align='center',color=colors[i-2],alpha=0.4)
    recs.append(r)

    plt.yticks(y_pos,s_label)
plt.legend(recs,['2','3','4','5'],loc=2)
plt.ylabel('Satisfaction Level')
plt.xlabel('Position')

plt.savefig('../figure/MeanQuerySatisfactionOnDifferentPosition/all.png')
plt.close()
