import re, os, sys, math
import operator 
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
from string import punctuation
import Stemmer

def rankdoc(result_doc, num_docs):
	doc = dict()
	factor = dict(
		t=0.3,b=0.3,c=0.1,l=0.1,i=0.2
		)
	for word in result_doc:
		for key in result_doc[word]:
			if len(result_doc[word][key])==0:
				continue
			x = math.log(num_docs/len(result_doc[word][key]))
			for dc in result_doc[word][key]:
				if dc[0] not in doc:
					doc[dc[0]] = 0.0
				doc[dc[0]] += factor[key] * x * (math.log(dc[1]+1))
	t = sorted(doc.items(), key=operator.itemgetter(1), reverse=True)
	return t[:10]

def findoffset(offsets, word, l, r, f):
	while l<=r:
		mid = (r+l)/2
		f.seek(offsets[mid])
		midword = f.readline().strip().split(' ')[0] 
		if midword == word:
			return offsets[mid]
		if midword < word:
			l = mid+1
		else:
			r = mid-1
	return -1

def get_postinglist(f, offset, key):
	f.seek(offset)
	l = f.readline().strip().split(' ')[1].split('|')
	if key=='a':
		return l
	w = list(x for x in l if key in x)
	return w

def finddoc(query_list, indexpath, num_docs, offsets):
	f_offset = open('offsets.txt', 'r')
	f_ind = open(indexpath, 'r')
	field_list = dict(
		t=re.compile('t[0-9]+'),
		c=re.compile('c[0-9]+'),
		b=re.compile('b[0-9]+'),
		i=re.compile('i[0-9]+'),
		l=re.compile('l[0-9]+'),
		r=re.compile('r[0-9]+')
		)
	result_doc = dict()
	for key in query_list:
		if key in ['a']:
			for word in query_list['a']:
				off = findoffset(offsets, word, 0, len(offsets), f_ind)
				if off==-1:
					continue
				r1 = get_postinglist(f_ind, off, 'a')
				result_doc[word] = {'t': list(), 'b': list(),'c': list(),'l': list(),'i': list(),'r': list()}
				for li in r1:
					yr = re.findall('d[0-9]+', li)
					if 't' in li:
						xr = re.findall('t[0-9]+', li)
						result_doc[word]['t'].append([int(yr[0][1:]), int(xr[0][1:])])
					if 'c' in li:
						xr = re.findall('c[0-9]+', li)
						result_doc[word]['c'].append([int(yr[0][1:]), int(xr[0][1:])])
					if 'i' in li:
						xr = re.findall('i[0-9]+', li)
						result_doc[word]['i'].append([int(yr[0][1:]), int(xr[0][1:])])
					if 'l' in li:
						xr = re.findall('l[0-9]+', li)
						result_doc[word]['l'].append([int(yr[0][1:]), int(xr[0][1:])])
					if 'r' in li:
						xr = re.findall('r[0-9]+', li)
						result_doc[word]['r'].append([int(yr[0][1:]), int(xr[0][1:])])
					if 'b' in li:
						xr = re.findall('b[0-9]+', li)
						result_doc[word]['b'].append([int(yr[0][1:]), int(xr[0][1:])])
		else:
			for word in query_list[key]:
				off = findoffset(offsets, word, 0, len(offsets), f_ind)
				if off == -1:
					continue
				r1 = get_postinglist(f_ind, off, key)
				# print r1
				if word not in result_doc:
					result_doc[word] = dict()
				result_doc[word][key] = list()
				for li in r1:
					if key in result_doc[word]:
						yr = re.findall('d[0-9]+', li)
						xr = field_list[key].findall(li)
						result_doc[word][key].append([int(yr[0][1:]), int(xr[0][1:])])

	rank_doc = rankdoc(result_doc, num_docs)
	return rank_doc

