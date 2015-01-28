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

def content2dict(s):
    d = dict()
    for seg in s.split('\t'):
        kvs = seg.split('=')
        if len(kvs) ==2:
            d[kvs[0]] = kvs[1]
        else:
            d[kvs[0]] = ''

    return d


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


print len(sessionAvgClickPerQuery),len(sessionSatisfaction)
debug = open('../data/debug.txt','w')
for idx in range(0,348,1):
    debug.write(str(sessionAvgClickPerQuery[idx])+','+str(sessionSatisfaction[idx])+'\n')
debug.close()

result.write('Correlation between Average #clicks per query in session and Satisfaction\n')
p =  pearsonr(sessionAvgClickPerQuery,sessionSatisfaction)
k = kendalltau(sessionAvgClickPerQuery,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')

#Correlation between click position(Average, Max, Min) and session Satisfaction
sid2tid2q2clickPosition = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:list())))

# TIME=5112	USER=2014013436	TASK=1	QUERY=破冰游戏	ACTION=CLICK	INFO:	type=anchor	result=rb_1	page=1	rank=1	src=http://www.tuozhanyouxi.com/pobing/
cu.execute('select * from anno_log')
while True:
    one = cu.fetchone()
    if one !=None:
        id = int(one[0])
        sid = int(one[1])
        tid = int(one[2])

        action = one[3]
        if action =='CLICK':
            query = one[4]
            content = one[5]
            d = content2dict(content)
            p = int(d[u'page'])
            r = int(d[u'rank'])
            sid2tid2q2clickPosition[sid][tid][query].append((p-1)*10+r)
    else:
        break


sessionMaxPosition = list()
sessionMinPosition = list()
sessionAvgPosition = list()
sessionSatisfaction = list()

for s in validUsers:
    for t in range(1,13,1):
        jlist = []
        for _q in sid2tid2q2clickPosition[s][t].keys():
            jlist.extend(sid2tid2q2clickPosition[s][t][_q])

        sessionMaxPosition.append(max(jlist))
        sessionAvgPosition.append(mean(jlist))
        sessionMinPosition.append(min(jlist))
        _ssat = sid2tid2ssat[s][t]
        _ssat = (_ssat-personSpecific(s)[2])/personSpecific(s)[3]
        sessionSatisfaction.append(_ssat)

result.write('Correlation between Max/Avg/Mean click position in session and Satisfaction\n')
p =  pearsonr(sessionMaxPosition,sessionSatisfaction)
k = kendalltau(sessionMaxPosition,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')


p =  pearsonr(sessionAvgPosition,sessionSatisfaction)
k = kendalltau(sessionAvgPosition,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')

p =  pearsonr(sessionMinPosition,sessionSatisfaction)
k = kendalltau(sessionMinPosition,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')


# Correlation between Fixation Time/#Fixations 

# Correlation between Fixation Distance(Max, Min, Average) with session Distance
sid2tid2qfixPosition = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:list())))
sid2tid2fixNum = defaultdict(lambda:defaultdict(lambda:0))
sid2tid2fixDurSum = defaultdict(lambda:defaultdict(lambda:0))
for l in open('../data/fixitionOnResult.feature.temp').readlines()[1:]:
    segs = l.strip().split('\t')
    sid = int(segs[0])
    tid = int(segs[1])
    q = segs[2]
    p = int(segs[3])
    d = int(segs[7])
    r = int(segs[10])
    sid2tid2qfixPosition[sid][tid][q].append((p-1)*10+r)
    sid2tid2fixNum[sid][tid]+=1
    sid2tid2fixDurSum[sid][tid]+=d

sessionFixNum = list()
sessionFixDurSum = list()
sessionAvgFixDist = list()
sessionMaxFixDist = list()
sessionMinFixDist = list()
for s in validUsers:
    for t in range(1,13,1):
        _flist = []
        for _q in sid2tid2qfixPosition[s][t].keys():
            _flist.extend(sid2tid2qfixPosition[s][t][_q])
        sessionFixNum.append(sid2tid2fixNum[s][t])
        sessionFixDurSum.append(sid2tid2fixDurSum[s][t])
        sessionAvgFixDist.append(mean(_flist))
        sessionMaxFixDist.append(max(_flist))
        sessionMinFixDist.append(min(_flist))

result.write('Correlation between Deepest Fixation and Satisfaction\n')
p =  pearsonr(sessionMaxFixDist,sessionSatisfaction)
k = kendalltau(sessionMaxFixDist,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')

result.write('Correlation between Average Fixation Depth and Satisfaction\n')
p =  pearsonr(sessionAvgFixDist,sessionSatisfaction)
k = kendalltau(sessionAvgFixDist,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')
print 'hello world 2'

print len(sessionMinFixDist),len(sessionSatisfaction)
for i in range(0,348,1):
    print sessionMinFixDist[i],sessionSatisfaction[i]
result.write('Correlation between Minimal Fixation Depth and Satisfaction\n')
p =  pearsonr(sessionMinFixDist,sessionSatisfaction)
k = kendalltau(sessionMinFixDist,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')

result.write('Correlation between Fixation Duration and Satisfaction\n')
p =  pearsonr(sessionFixDurSum,sessionSatisfaction)
k = kendalltau(sessionFixDurSum,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')

result.write('Correlation between #Fixations and Satisfaction\n')
p =  pearsonr(sessionFixNum,sessionSatisfaction)
k = kendalltau(sessionFixNum,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')

result.write('Correlation between Sum of Fixation Time and Satisfaction\n')
p =  pearsonr(sessionFixDurSum,sessionSatisfaction)
k = kendalltau(sessionFixDurSum,sessionSatisfaction)
result.write(','.join([str(p[0]),str(p[1]),str(k[0]),str(k[1])])+'\n')





result.close()

