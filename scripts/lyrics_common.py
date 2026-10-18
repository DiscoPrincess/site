"""Sanitize source timestamps without inventing word timings."""
import math,re

def clean_lines(raw,duration):
    lines=[]
    if not isinstance(raw,list):return lines
    for row in raw:
        if not isinstance(row,dict):continue
        text=row.get('text','').strip()
        if not text or re.fullmatch(r'\[[^\]]+\]',text):continue
        start,end=row.get('start'),row.get('end')
        if not all(isinstance(t,(float,int)) and math.isfinite(t) for t in (start,end)):continue
        if not 0<=start<end<=duration+.5:continue
        if end-start>35:continue
        lines.append({'text':text,'start':round(start,3),'end':round(end,3),'words':[]})
    return sorted(lines,key=lambda l:l['start'])

def accepted_words(words,line):
    if len(words)!=len(line['text'].split()):return []
    previous=line['start']-.05
    for w in words:
        if not line['start']-.05<=w['start']<w['end']<=line['end']+.05:return []
        if w['start']<previous or w['score']<.15:return []
        previous=w['end']
    return words
