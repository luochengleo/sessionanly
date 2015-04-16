#coding=utf8

from bs4 import BeautifulSoup
import sqlite3
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

cx = sqlite3.connect('../data/db.sqlite3')
cu = cx.cursor()

fout = open('../data/clickedContent.txt','w')
count = 0
for l in open('../data/resultDwellTime.feature'):
    segs = l.strip().split('\t')
    task = int(segs[1])
    rid = segs[3]
    query = segs[2]
    count +=1
    print count
    cu.execute('select * from anno_searchresult where query="'+segs[2]+'" and result_id="'+rid+'"')
    while True:
        one = cu.fetchone()
        if one==None:
            break
        else:
            content=one[4]
            soup = BeautifulSoup(content)
            title = soup.find('h3').get_text()
            snippet = soup.find('div',class_='ft').get_text()
            print title,snippet
            fout.write(str(task)+'\t'+(title +' '+snippet).replace('\n',' ')+'\n')
fout.close()
