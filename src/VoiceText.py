__author__ = 'cheng'
import json
fout = open('../data/voice2text.csv','w')
count = 0
wcount = 0
for l in open('../data/result.txt').readlines():
    count +=1
    segs = l.strip().split('\t')
    if len(segs) >=3:
        user,filename,jcontent = l.strip().split('\t')
    else:
        user,filename = l.strip().split('\t')
        jcontent=''
    filename = filename.replace('.wav','').replace('_','","')
    if jcontent=='':
        print 'empty'
        fout.write('"'+user+'","'+filename+'"\n')
        continue
    else:
        jobj = json.loads(jcontent)
        if 'result' in jobj.keys():
            wcount +=1
            print wcount,count
            fout.write('"'+user+'","'+filename+'","'+jobj['result'][0].encode('cp936')+'"\n')
            continue
        else:
            print 2
            fout.write('"'+user+'","'+filename+'"\n')
            continue