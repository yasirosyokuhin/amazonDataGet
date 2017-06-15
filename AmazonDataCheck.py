#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
	
adultList = ""
	
def chkAdultPublisher(str):
	global adultList
	
	if (len(adultList) <= 0) :
		print ("file open")
		f = open('PATH')
		adultList = f.readlines() # 1行毎にファイル終端まで全て読む(改行文字も含まれる)
		f.close()
	
	lineLen = len(adultList)
	num = 0
	
	while num < lineLen:
		line = re.sub(r'[\n\r]', "", adultList[num])
		#lineArray = line.split("\t")
		
		#print (line)
		if (str == line):
			#print ("adult publisher;" + line)
			return 1
		num += 1
	
	return 0
	
if __name__ == "__main__":
    chkAdultPublisher("A-KAGURA")
    
    
    