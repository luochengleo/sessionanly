__author__ = 'cheng'

from collections import defaultdict

sid2tid2satis = defaultdict(lambda:defaultdict(lambda:0.0))
sid2tid2util = defaultdict(lambda:defaultdict(lambda:0.0))

for l in open('../data/recordscore.txt').readlines()[1:]:
    segs = l.strip().split('\t')
    s = int(segs[0])
    t = int(segs[1])
    zscore = float(segs[3])
    rscore = float(segs[4])
    sid2tid2satis[s][t]=zscore
    sid2tid2util[s][t]=rscore
sid2tid2sdwelltime = defaultdict(lambda:defaultdict(lambda:0.0))

for l in open('../data/sessionDwellTime.feature').readlines():
    segs = l.strip().split('\t')
    s = int(segs[0])
    t = int(segs[1])
    d = int(segs[4])
    sid2tid2sdwelltime[s][t] = d

hzhuguan = list()
lzhuguan = list()
hkeguan = list()
lkeguan = list()

for s in sid2tid2sdwelltime.keys():
    for t in sid2tid2sdwelltime[s].keys():
        if sid2tid2sdwelltime[s][t]>10000:
            hzhuguan.append(sid2tid2satis[s][t])
            hkeguan.append(sid2tid2util[s][t])

        else:
            lzhuguan.append(sid2tid2satis[s][t])
            lkeguan.append(sid2tid2util[s][t])
print 'High Effort ',len(hzhuguan),' Samples'
print 'Low Effort ',len(lzhuguan),' Samples'

from scipy.stats.stats import pearsonr
from scipy.stats.stats import kendalltau
print 'High'
print pearsonr(hzhuguan,hkeguan),kendalltau(hzhuguan,hkeguan)
print 'Low'
print pearsonr(lzhuguan,lkeguan),kendalltau(lzhuguan,lkeguan)