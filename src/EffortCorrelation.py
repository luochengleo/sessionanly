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
            print 'Load Query Satisfaction',studentID,task_id,score

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
            print 'Load Session Satisfaction',studentID,task_id,score
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

# correlatin calculation

result = open('../data/EffortCorrelation.csv','w')





# correlation between session dwell time and satisfaction
result.write('Correlation between Session Dwell time and Satisfaction\n')
result.write('kappa,sign,kendalltau,sign\n')


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

p =  pearsonr(sessionDwellTime,sessionSatisfaction)
k = kendalltau(sessionDwellTime,sessionSatisfaction)\

result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')

######################################################################
# correlation between (#clicks in a session )  and session satisfaction

result.write('Correlation between #Clicks in session and Satisfaction\n')
result.write('kappa,sign,kendalltau,sign\n')

sessionClicks = list()
sessionSatisfaction = list()

sid2tid2sessionClicks = defaultdict(lambda:defaultdict(lambda:0))
for l in open('../data/queryClicks.feature').readlines():
    segs = l.strip().split('\t')
    sid = int(segs[0])
    tid = int(segs[1])
    ck = int(segs[-1])
    sid2tid2sessionClicks[sid][tid] += ck

for s in validUsers:
    for t in range(1,13,1):
        sessionClicks.append(sid2tid2sessionClicks[s][t])
        _ssat = sid2tid2ssat[s][t]
        _ssat = (_ssat-personSpecific(s)[2])/personSpecific(s)[3]
        sessionSatisfaction.append(_ssat)

print 'Satisfaction(User) correlation with session clicks'

p =  pearsonr(sessionClicks,sessionSatisfaction)
k = kendalltau(sessionClicks,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')


######################################################################
# correlation between #queries  and session satisfaction
result.write('Correlation between #Queries in session and Satisfaction\n')
sessionQueryNum = list()
sessionSatisfaction = list()
sessionAvgQLength = list()
sid2tid2queries = defaultdict(lambda:defaultdict(lambda:set()))

cu.execute('select * from anno_log')
while True:
    one = cu.fetchone()
    if one ==None:
        break
    else:
        id = int(one[0])
        sid = int(one[1])
        tid = int(one[2])
        query = one[4]
        sid2tid2queries[sid][tid].add(query)

for s in validUsers:
    for t in range(1,13,1):
        if len(sid2tid2queries[s][t]) ==0:
            print s,t,len(sid2tid2queries[s][t])
        sessionQueryNum.append(len(sid2tid2queries[s][t]))
        sessionAvgQLength.append(mean([float(len(item)) for item in sid2tid2queries[s][t]]))

        _ssat = sid2tid2ssat[s][t]
        _ssat = (_ssat-personSpecific(s)[2])/personSpecific(s)[3]
        sessionSatisfaction.append(_ssat)

print 'Satisfaction(User) correlation with session query num'

p =  pearsonr(sessionQueryNum,sessionSatisfaction)
k = kendalltau(sessionQueryNum,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')

# correlation between avg query length  and session satisfaction

print 'Satisfaction(User) correlation with Average Query Length'

result.write('Correlation between Average Query Length in session and Satisfaction\n')
p =  pearsonr(sessionAvgQLength,sessionSatisfaction)
k = kendalltau(sessionAvgQLength,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')

# correlation between avg query and session satisfaction

print 'Satisfaction(User) correlation with Average Query Length'

result.write('Correlation between Average Query Length in session and Satisfaction\n')
p =  pearsonr(sessionAvgQLength,sessionSatisfaction)
k = kendalltau(sessionAvgQLength,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')

# correlation between Average Clicks per query and session Satisfaction
print 'Satisfaction(User) correlation with #clicks per query in session'

sessionAvgClickPerQuery = list()
for i in range(0,len(sessionClicks),1):
    sessionAvgClickPerQuery.append(float(sessionClicks[i])/float(sessionQueryNum[i]))

result.write('Correlation between Average #clicks per query in session and Satisfaction\n')
p =  pearsonr(sessionAvgClickPerQuery,sessionSatisfaction)
k = kendalltau(sessionAvgClickPerQuery,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')

#Correlation between click position(Average, Max, Min) and session Satisfaction

sid2tid2q2clickPosition = defaultdict(lambda:defaultdict(lambda:list()))

cu.execute()




result.close()

