#coding=utf8
__author__ = 'luocheng'
import re

patterns = {key: re.compile('%s=(.*?)\\t' % key) for key in ['TIMESTAMP', 'USER', 'TASK', 'QUERY', 'ACTION']}
info_patterns = re.compile('INFO:\\t(.*?)$')
anno_info_patterns = {key: re.compile('%s=(.*?)\\t' % key) for key in ['id', 'src']}
anno_info_patterns['score'] = re.compile('score=(.*?)$')

def loadValidUsers():
    u = set()
    for l in open('../data/validusers.txt').readlines():
        u.add(int(l.strip()))
    return u

class Annotation:
    def __init__(self,studentID,task_id,query,result_id,result_url,score,content):
        self.studentID = studentID
        self.task_id = int(task_id)
        self.query = query
        self.result_id = result_id
        self.result_url = result_url
        self.score = int(score)
        self.content = content

def fromString(line):
    studentID = patterns['USER'].search(line).group(1)
    task_id = patterns['TASK'].search(line).group(1)
    query = patterns['QUERY'].search(line).group(1)
    info = info_patterns.search(line).group(1)
    result_id = anno_info_patterns['id'].search(info).group(1)
    result_url = anno_info_patterns['src'].search(info).group(1)
    score = int(anno_info_patterns['score'].search(info).group(1))
    anno_log_obj = Annotation(studentID=studentID,
                                task_id=task_id,
                                query=query,
                                result_id=result_id,
                                result_url=result_url,
                                score=score,
                                content=line)
    return anno_log_obj
