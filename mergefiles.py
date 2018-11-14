import re, sys, os, errno
import heapq
from write_file import write_inv

def mergefiles(num_files, folder_path):
	file_pointer = list()
	file_end = list()
	wordlist = list()
	heap = list()

	for file_count in xrange(0,num_files):
		filepath = os.path.join(folder_path, str(file_count)+'.txt')
		file_pointer.append(open(filepath, 'r'))
		wordlist.append(file_pointer[file_count].readline().split(' ', 1))
		if wordlist[file_count][0] not in heap:
			heapq.heappush(heap, wordlist[file_count][0])
		file_end.append(0) 

	words = list()
	idf_dict = dict()
	filepath = 'inv_index.txt'
	offsetsfile = 'offsets.txt'
	try:
		os.remove(filepath)
		os.remove(offsetsfile)
	except OSError as e: 
		if e.errno != errno.ENOENT: 
			raise 
	flag = 0
	prev_offset = 0
	while len(heap)>0:
		top_word = heapq.heappop(heap)
		if top_word == '':
			continue
		words.append(top_word)
		if top_word not in idf_dict:
			idf_dict[top_word] = list()
		for x in xrange(0, num_files):
			if(file_end[x]==1):
				continue
			if wordlist[x][0] == top_word:
				idf_dict[top_word].append(wordlist[x][1].strip())
				wordlist[x] = file_pointer[x].readline().split(' ', 1)
				if wordlist[x] == '':
					file_end[x]=1
					file_pointer[x].close()
					continue
				if wordlist[x][0] not in heap:
					heapq.heappush(heap, wordlist[x][0])

		if len(words)%100000 == 0:
			prev_offset = write_inv(words, idf_dict, filepath, flag, offsetsfile, prev_offset)
			flag = 1
			words = list()
			idf_dict = dict()
	if len(words)>0:
		prev_offset = write_inv(words, idf_dict, filepath, flag, offsetsfile, prev_offset)