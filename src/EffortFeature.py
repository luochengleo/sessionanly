#coding=utf8

__author__ = 'luocheng'

import sqlite3
from Utils import loadValidUsers

cx = sqlite3.connect('../data/db.sqlite3')
cu = cx.cursor()

class Log:
    def __init__(self,id,studentid,taskid,action,query,content):
        self.id = id
        self.studentid = studentid
        self.taskid = taskid
        self.action = action
        self.query = query
        self.content = content

LOGLIST =list()
validusers=loadValidUsers()


cu.execute('select * from anno_log')
while True:
    one = cu.fetchone()
    if one == None:
        break
    else:
        id = one[0]
        sid = int(one[1])
        taskid = int(one[2])
        action = one[3]
        query = one[4]
        content = one[5]
        if sid in validusers:
            LOGLIST.append(Log(id,sid,taskid,action,query,content))
import re
from collections import defaultdict
def extractTime(s):
    tp = re.compile('TIME=(\d*)')
    time  = int(tp.search(s).group(1))
    return time



def extractSessionDwellTime():
    # begintime ,endtime  __stdentid__taskid__
    betime = defaultdict(lambda:defaultdict(lambda:[-1,-1]))

    for l in LOGLIST:
        if l.action =='BEGIN_SEARCH':
            betime[l.studentid][l.taskid][0] = extractTime(l.content)
        if l.action =='SEARCH_END':
            betime[l.studentid][l.taskid][1] = extractTime(l.content)
    fout = open('../data/sessionDwellTime.feature','w')
    for sid in betime.keys():
        for tid in range(1,13,1):
            fout.write('\t'.join([ str(item) for item in [sid,tid, betime[sid][tid][0],betime[sid][tid][1],betime[sid][tid][1]-betime[sid][tid][0],'\n']]))
    fout.close()

def extractQueryDwellTime():
    #begin, end studentid, taskid ,query,
    betime = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:[2E12,-1])))
    for l in LOGLIST:
        t = extractTime(l.content)
        sid = l.studentid
        tid = l.taskid
        q = l.query
        if t <  betime[sid][tid][q][0]:
            betime[sid][tid][q][0] = t
        if t >  betime[sid][tid][q][1]:
            betime[sid][tid][q][1] = t
    fout = open('../data/queryDwellTime.feature','w')
    for sid in validusers:
        for tid in range(1,13,1):
            for q in betime[sid][tid].keys():
                fout.write('\t'.join([str(item) for item in [sid,tid,q.encode('utf8'),betime[sid][tid][q][0],betime[sid][tid][q][1],betime[sid][tid][q][1]-betime[sid][tid][q][0],'\n']]))
    fout.close()

def extractSessionClicks():
    # #clicks studentid, taskid ,counts
    clicks = defaultdict(lambda:defaultdict(lambda:0))
    for l in LOGLIST:
        if l.action =='CLICK':
            clicks[l.studentid][l.taskid] +=1
    fout = open('../data/sessionClicks.feature','w')
    for sid in validusers:
        for tid in range(1,13,1):
            fout.write(str(sid)+'\t'+str(tid)+'\t'+str(clicks[sid][tid])+'\n')
    fout.close()

def extractQueryClicks():
    # #clicks studentid, taskid, query,counts
    clicks = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:0)))
    for l in LOGLIST:
        if l.action =='CLICK':
            clicks[l.studentid][l.taskid][l.query] +=1
    fout = open('../data/queryClicks.feature','w')
    for sid in validusers:
        for tid in range(1,13,1):
            for q in clicks[sid][tid].keys():
                fout.write(str(sid)+'\t'+str(tid)+'\t'+q.encode('utf8')+'\t'+str(clicks[sid][tid][q])+'\n')
    fout.close()

def extractFixation():
    # boundary query, page, list
    bond = defaultdict(lambda:defaultdict(lambda:list()))

    for l in open('../data/mouse_and_eye_new/result_pos.txt').readlines():
        d = dict()
        segs =l.strip().split('\t')
        if len(segs) >1:
            for s in segs:
                _k,_v = s.split('=')
                d[_k] = _v
            bond[d['query']][int(d['page'])].append([int(d['top']),int(d['bottom']),int(d['left']),int(d['right'])])
    # sid | tid |

    querieseq = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:dict())))
    for l in LOGLIST:
        _sid = l.studentid
        _tid = l.taskid
        _query = l.query
        if len(querieseq[_sid][_tid].keys()) == 0:
            querieseq[_sid][_tid][1] = _query
        else:
            if _query == querieseq[_sid][_tid][max(querieseq[_sid][_tid].keys())]:
                pass
            else:
                querieseq[_sid][_tid][max(querieseq[_sid][_tid].keys())+1] = _query
    fout = open('../data/fixitionOnResult.feature.temp','w')
    fout.write('studentid\ttaskid\tquery\tpageid\tqueryidx\ttype\tfixation_idx\tduration\tx_page\ty_page\tresult_idx\ttop\tbottom\tleft\tright\n')
    for sid in validusers:
        for l in open('../data/mouse_and_eye_new/processed_'+str(sid)).readlines()[1:]:
            segs = l.strip().split('\t')
            _sid = int(segs[0])
            _tid = int(segs[1])
            _query = segs[2]
            _pid = int(segs[3])
            _qidx = int(segs[4])
            _type = segs[5]
            _timestamp = int(segs[6])
            _content = segs[7:]

            if _type == 'eye':
                _contentdict = dict()
                for item in _content:
                    # print l
                    # print _content
                    k,v = item.strip().split('=')
                    _contentdict[k] = v
                x_page = int(_contentdict['x_on_page'])
                y_page = int(_contentdict['y_on_page'])
                duration = int(_contentdict['fixation_duration'])
                f_idx = int(_contentdict['fixation_idx'])
                count = 0
                # print len(bond[_query][_pid])
                # print bond[_query][_pid]
                for r in bond[_query][_pid][0:10]:
                    count +=1
                    if  r[2] <= x_page <= r[3] and r[0] <= y_page <= r[1]:

                        fout.write('\t'.join([str(item) for item in [_sid,_tid,_query,_pid,_qidx,_type,f_idx,duration,x_page,y_page,count,r[0],r[1],r[2],r[3]]]  )+'\n')

def content2dict(s):
    d = dict()
    for seg in s.split('\t'):
        kvs = seg.split('=')
        if len(kvs) ==2:
            d[kvs[0]] = kvs[1]
        else:
            d[kvs[0]] = ''

    return d


def extractResultDwellTime():

    fout = open('../data/resultDwellTime.feature','w')

    for idx in range(0,len(LOGLIST),1):
        l  = LOGLIST[idx]
        if l.action=='CLICK':
            d = content2dict(l.content)
            t0 = int(d['TIME'])
            sid = l.studentid
            tid = l.taskid
            q = l.query
            r  =d['result']
            p = d['page']
            rk = d['rank']
            src = d['src']


            for offset in range(1,5,1):
                if idx + offset >len(LOGLIST):
                    break
                else:
                    if LOGLIST[idx+offset].action != 'JUMP_OUT' or LOGLIST[idx+offset] =='JUMP_IN':
                        t1 = int(content2dict(LOGLIST[idx+offset].content)['TIME'])
                        fout.write('\t'.join([item for item in[str(sid),str(tid),q.encode('utf8'),r.encode('utf8'),p.encode('utf8'),rk.encode('utf8'),src.encode('utf8'),str(t1-t0)] ])+'\n')
                        break
    fout.close()


            #TIME=41906	USER=2014013436	TASK=1	QUERY=破冰游戏	ACTION=CLICK	INFO:	type=anchor	result=rb_0	page=1	rank=0	src=http://www.bdstar.org/Article/ShowArticle.asp?ArticleID=3927




def extractQueryDwellTime():
    fout = open('../data/queryDwellTime.feature','w')

    for idx in range(0,len(LOGLIST),1):
        l  = LOGLIST[idx]
        if l.action=='BEGIN_SEARCH':
            d = content2dict(l.content)
            t0 = int(d['TIME'])
            sid = l.studentid
            tid = l.taskid
            q = l.query
            offset = 1
            while True:
                if idx + offset >=len(LOGLIST):
                    t1 = int(content2dict(LOGLIST[idx+offset -1 ].content)['TIME'])
                    fout.write(str(sid) + '\t'+str(tid)+'\t'+q.encode('utf8')+'\t'+str(t1-t0)+'\n')
                    fout.close()
                    return
                else:
                    if LOGLIST[idx+offset].action == 'QUERY_REFORM' or LOGLIST[idx+offset].action == 'OVER':
                        t1 = int(content2dict(LOGLIST[idx+offset].content)['TIME'])
                        fout.write(str(sid) + '\t'+str(tid)+'\t'+q.encode('utf8')+'\t'+str(t1-t0)+'\n')
                        break
                    else:
                        pass

                offset +=1
    fout.close()



extractSessionDwellTime()
extractQueryDwellTime()
extractSessionClicks()
extractQueryClicks()


extractFixation()
extractResultDwellTime()
extractQueryDwellTime()
#