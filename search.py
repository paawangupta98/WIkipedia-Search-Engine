import re, os, sys
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
from string import punctuation
import Stemmer
import time
from rankdoc import finddoc

if __name__ ==  "__main__":
	stemmer = Stemmer.Stemmer('english')
	stop = set(stopwords.words('english'))
	offsets = list()
	titlepath = 'titles.txt'
	titles = dict()
	with open(titlepath, 'r') as f:
		for line in f.readlines():
			line = line.strip().split(' ',1)
			titles[int(line[0])] = line[1]
	num_docs = len(titles)
	# print titles
	with open('offsets.txt', 'r') as f:
		offsets = list(int(y.strip().split(' ')[1]) for y in f.readlines())
	while True:
		query = raw_input('->')
		ti = time.time()
		query = re.sub('[^0-9a-zA-Z: ]' , '', query)
		indexpath = sys.argv[1]
		field_list = ['t:', 'b:', 'i:', 'l:', 'c:', 'r:']
		query = query.strip() + ' '
		reg = re.compile(r'[a-z]:[A-Z0-9a-z ]+[ ]')
		query_list = dict()
		if any(1 for x in field_list if x in query):
			query = reg.findall(query)
			for x in query:
				x = x.strip().split(':')
				query_list[x[0]] = list(stemmer.stemWord(y.lower()) for y in x[1].split(' ') if y not in stop)
		else:
			qwords = query.strip().split(' ')
			query_list['a'] = list(stemmer.stemWord(w.lower()) for w in qwords if w not in stop)
			pass
		# print query_list
		results = finddoc(query_list, indexpath, num_docs, offsets)
		# print results
		print time.time() - ti
		if len(results)>0:
			if(len(results) > 10):
				results = results[:10]
			for k in results:
				print titles[k[0]]
				# print k
		else:
			print "query not found"


