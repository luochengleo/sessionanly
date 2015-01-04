__author__ = 'luocheng'
from collections import defaultdict
import sqlite3
import math
def loadValidUsers():
    u = set()
    for l in open('../data/validusers.txt'):
        u.add(l.strip())
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
        studentID = logpiece[1]
        task_id = logpiece[2]
        query = logpiece[3]
        score = logpiece[4]
        querysatis[studentID][task_id].append(score)

cu.execute('select * from anno_sessionannotation')
while True:
    logpiece =  cu.fetchone()
    if logpiece == None:
        break
    else:
        id = logpiece[0]
        studentID = logpiece[1]
        task_id = logpiece[2]
        score = logpiece[3]
        querysatis[studentID][task_id]=score
def sCG(lt):
    return sum(formalize(lt))

def sDCG(lt,bq):
    #sDCG(q) = (1 + logbq q)-1 * DCG
    sum = 0.0








