import os
import re
import sys,  errno
import xml.sax.handler
from copy import deepcopy
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
from string import punctuation
import Stemmer
from write_file import write_file
from mergefiles import mergefiles

stop = set(stopwords.words('english'))
stop.update(list(x for x in punctuation))
stemmer = Stemmer.Stemmer('english')
text_punc = list(x for x in punctuation if x not in ['{','}','=','[',']'])
words_left = ['{','}','=','[',']']
text_punc.append('\n')
def processtitle(docid, title):
    """Create frequency of words in title."""
    freq = dict()
    title = re.sub('\\b[-\.]\\b' , '', title)
    title = re.sub('[^0-9a-zA-Z\{\}\[\]\=]+',' ',title)
    for word in wordpunct_tokenize(title):
    	word = word.lower()
    	if word not in stop:
			word = stemmer.stemWord(word)
			if word not in freq:
				freq[word]=0
			freq[word]+=1
    return freq

def processtext(docid, text):
    """Create Frequency of words in text."""
    freq = dict()
    numcurl = 0
    numsq = 0
    numeq = 0
    isinfobox = 0
    iscategory = 0
    islink = 0
    curtag = 'b'
    # text = text.lower()
    # text = re.sub('\\b[-\.]\\b' , '', text)
    text = re.sub('[^0-9a-zA-Z\{\}\[\]\=]+',' ',text)
    # info_reg = re.compile(r'\{\{infobox(.*)\}\}')
    """ Split on [[category]] to get the category string."""
    cat_reg = re.compile(r'\[\[Category(.*?)\]\]')
    text_new = cat_reg.split(text)
    if len(text_new)>1:
    	for te in text_new[1:]:
    		for t in words_left:
    			te = te.replace(t,' ')
	    	for word in wordpunct_tokenize(te):
	    		word = word.lower()
	    		if word not in freq:
	    			freq[word] = dict(t=0,b=0,i=0,c=0,l=0,r=0)
	    		freq[word]['c']+=1
    	text = text_new[0]

    """ Split on ==external links== to get the external links text."""
    text_new = text.split('==External links==')
    if len(text_new)>1:
    	for t in words_left:
    			text_new[1] = text_new[1].replace(t,' ')
    	for word in wordpunct_tokenize(text_new[1]):
    		word = word.lower()
    		if word not in freq:
    			freq[word] = dict(t=0,b=0,i=0,c=0,l=0,r=0)
    		freq[word]['l']+=1
    	text = text_new[0]

    """ Now to processing on the rest of the body."""
    text_new = text.split('{{Infobox')
    if len(text_new)>1:
    	for t in words_left:
    			text_new[0] = text_new[0].replace(t,' ')
    	for word in wordpunct_tokenize(text_new[0]):
    		word = word.lower()
    		if word not in freq:
    			freq[word] = dict(t=0,b=0,i=0,c=0,l=0,r=0)
    		freq[word]['b']+=1
    	numbra = 1
    	cat = 'i'
    	for word in wordpunct_tokenize(text_new[1]):
    		word = word.lower()
    		if '}}' in word:
    			numbra -= 1
    		if '{{' in word:
    			numbra += 1
    			continue
    		if numbra == 0:
    			cat = 'b'
    		for t in words_left:
    			word = word.replace(t,'')
    		if word not in freq:
    			freq[word] = dict(t=0,b=0,i=0,c=0,l=0,r=0)
    		freq[word][cat]+=1
    else:
    	for t in words_left:
    			text = text.replace(t,' ')
    	for word in wordpunct_tokenize(text):
    		word = word.lower()
    		if word not in freq:
    			freq[word] = dict(t=0,b=0,i=0,c=0,l=0,r=0)
    		freq[word]['b']+=1

    new_freq = dict()
    for word in freq:
    	w = stemmer.stemWord(word)
    	if w not in new_freq:
    		new_freq[w] = freq[word]
    	else:
    		for key in new_freq[w]:
    			new_freq[w][key] += freq[word][key]
    freq = dict()
    for word in new_freq:
   		if word not in stop and word != '':
   			freq[word] = new_freq[word]
    return freq


class IndexGenerator(xml.sax.ContentHandler):
	"""
	"""
	
	def __init__(self):
		"""Initialize."""
		self.istitle = 0
		self.istext = 0
		self.isfirstid = 0
		self.isid = 0
		self.titlebuf = ""
		self.textbuf = ""
		self.docid = ""
		self.tagmap = {'d':'docid', 't':'title', 'b':'text', 'i':'infobox', 'c':'categories', 'l':'links', 'r':'References'}
		self.tag_order = ['d','t','b','i','c','l','r']
		self.invindex = dict()
		self.count = 0
		self.filecount = 0
		self.first=0

	def startElement(self, tag, attributes):
		"""What to do if we get the start of a XML tag."""
		if tag == 'title':
			self.istitle = 1
			self.titlebuf = ""
		elif tag == 'text':
			self.istext = 1
			self.textbuf = ""
		elif tag == 'page':
			self.isfirstid = 1
			self.docid = ""
		elif tag == 'id' and self.isfirstid==1:
			self.isid = 1
			self.isfirstid=0

	def characters(self, content):
		"""What to do during travesal between XML tags."""
		if self.istitle:
			self.titlebuf += content
		elif self.istext:
			self.textbuf += content
		elif self.isid:
			self.docid += content

	def endElement(self, tag):
		if tag == 'title':
			self.istitle = 0
		elif tag == 'text':
			self.istext = 0
		elif tag == 'id':
			self.isfirstid = 0
			self.isid=0
		elif tag == 'page':
			self.count += 1
			text = deepcopy(self.textbuf)
			title = deepcopy(self.titlebuf)
			self.startprocessing(title, text)

	def startprocessing(self, title, text ):
		"""Starts Processing the title and text to create tf-idf for the current document"""
		docid = self.count
		freq = processtext(docid, text)
		titlefreq = processtitle(docid, title)
		f=open('titles.txt', 'a+')
		if self.first==1:
			f.write('\n')
			
		if self.first==0:
			self.first=1
		tr = str(docid)+' '+title
		f.write(tr.encode('utf-8'))
		f.close()
		for word in titlefreq:
			if word in freq:
				freq[word]['t'] += titlefreq[word]
			else:
				freq[word] = dict(d=docid,t=titlefreq[word],b=0,i=0,c=0,l=0,r=0)
		for word in freq:
			if len(word)<3 or word.startswith('0'):
				continue
			freq[word]['d'] = str(docid)
			if word not in self.invindex:
				self.invindex[word] = list()
			self.invindex[word].append(''.join(tag+str(freq[word][tag]) for tag in freq[word] if freq[word][tag]!=0))
		if self.count%1000 == 0:
			write_file(self.invindex, self.filecount, sys.argv[2])
			self.invindex = dict()
			self.filecount +=1

if __name__ ==  "__main__":
	try:
		os.remove('titles.txt')
	except OSError as e: 
		if e.errno != errno.ENOENT: 
			raise 
	if not os.path.exists('./tmp/'):
		try:
			os.makedirs('./tmp/')
		except OSError as exc:
			if exc.errno != errno.EEXIST:
				raise
	parser = xml.sax.make_parser()
	Handler = IndexGenerator()
	parser.setContentHandler(Handler)
	parser.parse(sys.argv[1])
	if Handler.count%1000 > 0:
		write_file(Handler.invindex, Handler.filecount, sys.argv[2])
		Handler.filecount += 1
	mergefiles(Handler.filecount, 'tmp')