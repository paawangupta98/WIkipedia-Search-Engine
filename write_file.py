import re, sys, os

def write_file(idf_dict, file_count, folder_path):
	list_to_write = list()
	filepath = os.path.join(folder_path, str(file_count)+'.txt')
	f = open(filepath, 'w+')
	for key in sorted(idf_dict):
		str_write = key + ' '
		str_write += '|'.join(list(post for post in idf_dict[key]))
		list_to_write.append(str_write)
	if len(list_to_write)>0:
		f.write('\n'.join(list_to_write).encode('utf-8'))
	f.close()

def write_inv(words, idf_dict, filepath, first_write, offsetsfile, prev_offset):
	list_to_write = list()
	offset = list()
	try: 
		f = open(filepath, 'a+')
		f1 = open(offsetsfile, 'a+')
		if first_write == 1:
			list_to_write.append('')
			offset.append('')
		for key in words:
			offset.append(key + ' ' + str(prev_offset))
			str_write = key + ' '
			str_write += '|'.join(list(post for post in idf_dict[key]))
			list_to_write.append(str_write)
			prev_offset += len(str_write) + 1
		if len(list_to_write)>0:
			f.write('\n'.join(list_to_write).encode('utf-8'))
		if len(offset) > 0:
			f1.write('\n'.join(offset).encode('utf-8'))
		f.close()
		f1.close()
	except Exception as e:
		print "Exception occured", e
	finally:
		f.close()
		f1.close()
	return prev_offset