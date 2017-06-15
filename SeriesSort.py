# -*- coding:utf-8 -*-
import re
import sys
import MeCab
import mojimoji
import Mysql
import time

numbers =  [
'0','1','2','3','4','5','6','7','8','9',u'０',u'１',u'２',u'３',u'４',u'５',u'６',u'７',u'８',u'９',u'⓪',u'①',u'②',u'③',u'④',u'⑤',u'⑥',u'➆',u'⑧',u'➈']
	
def findNumber(string):

	global numbers
	
	# 文字列から数値の位置（最終）を見つける
	char_list = list(string)
	strlen = len(char_list)
	num = 1
	titleNum = strlen
	numstr = ""
	while num <= strlen:
		#print (char_list[strlen - num])
		if (char_list[strlen - num] in numbers) :
			if (num  == strlen):
				#タイトルの先頭は巻数ではないと判断
				numstr = ""
				break
			numVal = numbers.index(char_list[strlen - num])
			#  全角と半角を変換する
			if (numVal >= 20):
				numVal = numVal - 20
			elif (numVal >= 10):
				numVal = numVal - 10
				
			#4コマという文字の場合は、巻数ではないと判断する
			if (numVal  == 4 and num > 3):
				if (char_list[strlen - num + 1] == "コ" and char_list[strlen - num +2] == "マ"):
					num += 1
					continue
				
			numstr =  str(numVal) + numstr
		else:
			# 見つかっている数値が0の数値の場合は初期化しループを継続
			if (numstr == "0"):
				numstr = ""
				
			elif (len(numstr) != 0) :
				titleNum = strlen - num + 1
				break
		num += 1
	
	# 先頭のゼロを削除
	numstr = re.sub(r'^[0]{1,}', "", numstr)
	#print ("num:" + numstr +  " numLen:" + str(titleNum) + " title:"  + string[0:titleNum])
	# 0で終わっているタイトルは巻数とはみなさない
	if (numstr == 0) :
		titleNum = strlen
	
	# 数値がないもの、数値が年号のものは巻数とみなさない
	if (len(numstr) == 0 or int(numstr) >= 1900) :
		numstr = 0
		
	# タイトルと巻数を返却
	return re.sub(r'[(（]$',"",string[0:titleNum]), int(numstr)

def getSeries():
	
	mysql = Mysql.Mysql()
	# 3201084051 コミック
	lines = mysql.getCategoryProduct("3201084051")
	
	lineLen = len(lines)
	 
	title = ""
	titleNum = 0
	
	nextTitle = ""
	nextTitleNum = 0
	num = 0
	
	seriesTitle = ""
	seriesPublisher = ""
	seriesFlg = 0;
	seriesMinNum = 99999
	seriesMinAsin = ""
	seriesMaxNum = 0
	seriesCount = 1
	
	totalInstCount = 0
	totalUpdtCount = 0
	totalProcCount = 0
	
	#
	itemLine = {}
	
	while num < lineLen:
		line = lines[num][0]#title
		asin = lines[num][1]#asin
		
		#print (line)
		title , titleNum = findNumber(line)
		# 巻数が存在する場合
		if (titleNum != 0 and (num + 1) <  lineLen) :
			nextLine = lines[num + 1][0]
			nextAsin = lines[num + 1][1]
			
			nextTitle , nextTitleNum = findNumber(nextLine)
			#print (nextTitle , nextTitleNum)
			
			
			# 次のタイトルと一致するか確認 一致する場合
			if (title == nextTitle) :
				#print ("itti!!!!")
				seriesTitle =  title
				seriesFlg = 1
				# 最小最大巻数を工数（次の巻数分も更新する）
				if (seriesMinNum > titleNum) :
					seriesMinNum = titleNum
					seriesMinAsin  = asin
				if (seriesMinNum > nextTitleNum) : 
					seriesMinNum = nextTitleNum
					seriesMinAsin  = nextAsin
				if (seriesMaxNum < titleNum) :
					seriesMaxNum = titleNum
				if (seriesMaxNum < nextTitleNum) : 
					seriesMaxNum = nextTitleNum
				
				seriesCount += 1
				num += 1
				continue
		
		if (seriesFlg == 1):
			print (" タイトル:" + seriesTitle + " | "  + " 巻数" + str(seriesMinNum) + "～" + str(seriesMaxNum) + "計" + str(seriesCount)) 
		else :
			seriesTitle =  title
			seriesMinAsin = asin
			#print (" タイトル:" + seriesTitle + " | "  + " 巻数" + str(seriesMinNum) + "～" + str(seriesMaxNum) + "計" + str(seriesCount)) 
		
		itemLine["min_asin"] = seriesMinAsin
		itemLine["series_title"] = seriesTitle
		itemLine["series_min"] = seriesMinNum
		itemLine["series_max"] = seriesMaxNum
		itemLine["series_count"] = seriesCount
		
		instCount = mysql.updateSeriesInfo(itemLine)
		totalProcCount += 1
		
		if ((totalProcCount % 300) == 0):
			time.sleep(0.1)
		time.sleep(0.01)
		
		if instCount == 1:
			totalInstCount += 1
		else :
			totalUpdtCount += 1
		
		#変数初期化
		itemLine = {}
		seriesFlg = 0
		seriesCount = 1
		seriesTitle = ""
		seriesMinAsin = ""
		seriesMaxNum = 0
		seriesMinNum = 99999
		
		#次のレコードに遷移
		num += 1
	
	print ("db update finish! total:" + str(totalInstCount + totalUpdtCount) + " new:" + str(totalInstCount) + " update:" + str(totalUpdtCount))
	
if __name__ == '__main__':
	getSeries()
	