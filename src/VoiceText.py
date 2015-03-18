__author__ = 'cheng'
import json
fout = open('../data/voice2text.csv','w')
for l in open('../data/voice2text.txt').readlines():
    count = 0
    user,filename,jcontent = l.strip().split('\t')
    if '_' in filename:
        if jcontent=='':
            print 'empty'
            fout.write('"'+user+'","'+filename+'"\n')
            continue
        else:
            jobj = json.loads(jcontent)
            if 'result' in jobj.keys():
                print 1
                fout.write('"'+user+'","'+filename+'","'+jobj['result'][0].encode('cp936')+'"\n')
                continue
            else:
                print 2
                fout.write('"'+user+'","'+filename+'"\n')
                continue