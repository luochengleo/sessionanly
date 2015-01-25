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
            score =1
        print float(score)
        sid2tid2annotaion[studentid][taskid][annotator] = math.log10(float(score))
        aid2sum[annotator]+= math.log(float(score))


aid2mean = defaultdict(lambda:0.0)
for k in aid2sum.keys():
    aid2mean[k] = aid2sum[k]/(12.0*29.0)

gloablmean = sum(aid2sum[item] for item in aid2sum.keys())/(12.0*3.0*29.0)

fout = open('../data/recordannotation_processed.dat','w')

sid2tid2normanno = defaultdict(lambda:defaultdict(lambda:dict()))

for s in sid2tid2annotaion.keys():
    for t in sid2tid2annotaion[s].keys():
        if len(sid2tid2annotaion[s][t].keys())!=3:
            print s,t,sid2tid2annotaion[s][t]
        for a in sid2tid2annotaion[s][t].keys():
            # fout.write(str(s)+'\t'+str(t)+'\t'+str(a)+'\t'+str(gloablmean)+'\t'+str(aid2mean[a])+'\t'+str(sid2tid2annotaion[s][t][a])+'\t'+str((sid2tid2annotaion[s][t][a]+gloablmean-aid2mean[a]))+'\t'+str(10**(sid2tid2annotaion[s][t][a]+gloablmean-aid2mean[a]))+'\n')
            fout.write(str(s)+'\t'+str(t)+'\t'+str(a)+'\t'+str(10**(sid2tid2annotaion[s][t][a]+gloablmean-aid2mean[a]))+'\n')
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
    print i,pearsonr(aid2annotations[i[0]],aid2annotations[i[1]])[0],kendalltau(aid2annotations[i[0]],aid2annotations[i[1]])[0]








    

