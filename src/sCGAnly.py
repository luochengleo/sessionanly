__author__ = 'luocheng'
from collections import defaultdict
import sqlite3
from operator import div
import math
from scipy.stats.stats import pearsonr
from scipy.stats.stats import kendalltau

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
def formalize(lt):
    return [(float(item)-mean(lt))/variance(lt) for item in lt]

# userid - taskid - querysatislist
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


sCGseq = list()
sDCGseq = list()
nsDCGseq = list()
sSatisseq = list()
numOfQueryseq = list()

def sCG(lt ):
    return sum(lt)

def DCG(lt):
    sum = 0.0
    for i in range(0,len(lt),1):
        sum += (2**lt[i]-1)/(math.log(i+2)/math.log(2))
    return sum

def sDCG(lt,bq):
    #sDCG(q) = (1 + logbq q)-1 * DCG
    sum = 0.0
    for i in range(0,len(lt),1):
        sum += (1+math.log(i+1)/math.log(bq))**(-1)*DCG(lt[0:i+1])
    return sum
def dcg( r ):
    from math import log
    return reduce(lambda dcgs, dg: dcgs + [dg+dcgs[-1]],map(lambda (rank, g): (2**g-1) / log( rank+2, 2), enumerate( r ) ), [0])[1:]
def ndcg( r ):
  return map(div, dcg(r), dcg(sorted(r, reverse=True)))


for sid in querysatis.keys():
    for tid in querysatis[sid].keys():
        #formalize
        formalized_query = list()
        for item in querysatis[sid][tid]:
            formalized_query.append((float(item) - user_parameters[sid][0])/user_parameters[sid][1])
        formalized_session = (sessionsatis[sid][tid] - user_parameters[sid][2])/user_parameters[sid][3]

        numOfQueryseq.append(len(querysatis[sid][tid]))


        sCGseq.append(sCG(formalized_query))
        nsDCGseq.append(dcg(formalized_query)[-1])
        sDCGseq.append(sDCG(formalized_query,4))
        sSatisseq.append(formalized_session)


sCGchuNumOfQueriesseq = list()
for i in range(0,len(sCGseq),1):
    sCGchuNumOfQueriesseq.append(sCGseq[i]/numOfQueryseq[i])



print '\n\n'
print 'correlation between sCG and session Satisfaction'
print pearsonr(sCGseq,sSatisseq)
print kendalltau(sCGseq,sSatisseq)

print 'correlation between #queries and session Satisfaction'

print pearsonr(numOfQueryseq,sSatisseq)
print kendalltau(numOfQueryseq,sSatisseq)

print 'correlation between sCG/#queries and session Satisfaction'
print pearsonr(sCGchuNumOfQueriesseq,sSatisseq)
print kendalltau(sCGchuNumOfQueriesseq,sSatisseq)


print 'correlation between sDCG and session Satisfaction'
print pearsonr(sDCGseq,sSatisseq)
print kendalltau(sDCGseq,sSatisseq)


print ndcg([1,2,3,4,5,6])[-1]

print 'correlation between nsDCG and session Satisfaction'
print nsDCGseq
print pearsonr(nsDCGseq,sSatisseq)
print kendalltau(nsDCGseq,sSatisseq)

