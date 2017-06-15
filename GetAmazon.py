# -*- coding:utf-8 -*-
import bottlenose
import codecs
import types
import Amazon
import Mysql
import time
import os
import subprocess
import resource
import datetime
import sys
import tracemalloc
import gc

from bs4 import BeautifulSoup

# memo 0.2秒ぐらいだとHTTPエラーが多発する
sleepTime = 0.3

# black list
blackListTitle = " and not title:誕生日占い and not title:365誕生星占い"

# mode 
categoryUP = False

def main(node):
	global sleepTime
	# kindle読み放題のnode
	dic = {}
	amazon = Amazon.Amazon()
	dic = amazon.amazonBrowseNode(node)
	time.sleep(sleepTime)
	
	print (dic["parent_name"])
	for caegoryLine in dic["category"]:
		print ("getNodeItem start Node:" + caegoryLine["browsenode_id"] + " NodeName:" + caegoryLine["browsenode_name"])
		getNodeItem(caegoryLine["browsenode_id"])
		print ("getNodeItem end Node:" + caegoryLine["browsenode_id"] + " NodeName:" + caegoryLine["browsenode_name"])
		print ("============================================")
		
def mainSingleCategory(nodes):
	global sleepTime
	# kindle読み放題のnode
	dic = {}
	amazon = Amazon.Amazon()
	nodeAry = nodes.split(",")
	
	for node in nodeAry:
		dic = amazon.amazonBrowseNode(node)
		time.sleep(sleepTime)
		print ("getNodeItem start Node:" + node + " NodeName:" + dic["parent_name"])
		getNodeItem(node)
		print ("getNodeItem end Node:" + node + " NodeName:" + dic["parent_name"])

def moji_list(*args):
	moji = []
	for i in range(len(args)):
		moji.extend([chr(j) for j in range(args[i][0], args[i][1])])
	return moji


def getSortPricePageData(node, minPrice,maxPrice, powerIn, sortIn):
	global sleepTime
	pageCnt = 0
	amazon = Amazon.Amazon()
	totalPage = 10
	totalDic = {"item":[
		        ]}
	
	print ("min:" + str(minPrice) +  " max:" + str(maxPrice) + " page:" + str(pageCnt) + " power: " + powerIn + " sort:" + sortIn)
	while (totalPage > pageCnt):
		pageCnt += 1
		time.sleep(sleepTime)
		print ("page:" + str(pageCnt) + " totalPage:" + str(totalPage))
		dic,status = amazon.amazonItemSearch(pageCnt, node, "Books",minPrice,maxPrice,powerIn,sort=sortIn)
		totalDic["item"].extend(dic["item"])
	
	return totalDic["item"]
	

def getNullPubdatePageData(node, minPrice,maxPrice):
	global sleepTime
	pageCnt = 0
	amazon = Amazon.Amazon()
	totalPage = 10
	totalDic = {"item":[
		        ]}
	
	# 出版年月が入っていないコンテンツを取得。コミックが特に結構ある。
	power = "not pubdate:after 1000"
	print ("min:" + str(minPrice) +  " max:" + str(maxPrice) + " page:" + str(pageCnt) + "power: " + power)
	dic,status = amazon.amazonItemSearch(pageCnt, node, "Books", minPrice, maxPrice, power)
	totalDic["item"].extend(dic["item"])
	totalPage = int(dic["totalpages"])
	
	if (status == 1):
		print ("node is over flow by not after pubData:" + power + " min:" +str(minPrice) +  " max:" + str(maxPrice) + " totalPage:" + str(totalPage) + " totalresults:" + dic["totalresults"])
		totalDic["item"].extend(getYomiganaPageData(node , minPrice, maxPrice, power))
	else :
		while (totalPage > pageCnt):
			time.sleep(sleepTime)
			pageCnt += 1
			print ("page:" + str(pageCnt) + " totalPage:" + str(totalPage))
			dic,status = amazon.amazonItemSearch(pageCnt, node, "Books", minPrice, maxPrice, power)
			totalDic["item"].extend(dic["item"])
	
	return totalDic["item"]

def getYomiganaPageData(node, minPrice,maxPrice, powerIn):
	global sleepTime
	global blackListTitle
	
	pageCnt = 1
	totalDic = {"item":[
		        ]}
	
	amazon = Amazon.Amazon()

	#カタカナリストを取得
	moji = moji_list((12449, 12532+1))
	mojitwo = moji_list((12449, 12532+1))
	mojitwo.extend(moji_list((12532+8, 12532+9)))
	
	for chr in moji:
		power = powerIn + " and title-begins:" + chr
		print ("min:" + str(minPrice) +  " max:" + str(maxPrice) + " page:" + str(pageCnt) + "power: " + power)
		time.sleep(sleepTime)
		dic,status = amazon.amazonItemSearch(pageCnt, node, "Books", minPrice, maxPrice, power)
		
		totalDic["item"].extend(dic["item"])
		totalPage = int(dic["totalpages"])
		print ("totalPage: " + str(totalPage))
		
		if (status == 1):
			print ("node is over flow by power:" + power + " min:" +str(minPrice) +  " max:" + str(maxPrice) + " totalPage:" + str(totalPage) + " totalresults:" + dic["totalresults"])
			for chrtwo in mojitwo:
				pageCnt = 1
				powertwo = power + chrtwo + blackListTitle
				print ("min:" + str(minPrice) +  " max:" + str(maxPrice) + " page:" + str(pageCnt) + "powertwo: " + powertwo)
				time.sleep(sleepTime)
				dic,status = amazon.amazonItemSearch(pageCnt, node, "Books", minPrice, maxPrice, powertwo)
				totalDic["item"].extend(dic["item"])
				totalPage = int(dic["totalpages"])
				print ("totalPage: " + str(totalPage))
				if (status == 1):
					print ("can't node is over flow by powertwo:" + powertwo + " min:" +str(minPrice) +  " max:" + str(maxPrice) + " totalPage:" + str(totalPage) + " totalresults:" + dic["totalresults"])
					# ソートしてページ数を指定して取得
					# 昇順
					totalDic["item"].extend(getSortPricePageData(node, minPrice,maxPrice, powertwo, "-price"))
					# 降順
					totalDic["item"].extend(getSortPricePageData(node, minPrice,maxPrice, powertwo, "price"))
					
					pageCnt = 1
					continue
					
				while (totalPage > pageCnt):
					time.sleep(sleepTime)
					pageCnt += 1
					print ("page:" + str(pageCnt) + " totalPage:" + str(totalPage))
					dic,status = amazon.amazonItemSearch(pageCnt, node, "Books", minPrice, maxPrice, powertwo)
					totalDic["item"].extend(dic["item"])
	
				pageCnt = 1
				
		else :
			while (totalPage > pageCnt):
				time.sleep(sleepTime)
				pageCnt += 1
				print ("page:" + str(pageCnt) + " totalPage:" + str(totalPage))
				dic,status = amazon.amazonItemSearch(pageCnt, node, "Books", minPrice, maxPrice, power)
				totalDic["item"].extend(dic["item"])
		
		pageCnt = 1
	
	return totalDic["item"]

def getPubdatePageData(node, minPrice,maxPrice, pubDate, month):
	global sleepTime
	pageCnt = 1
	totalDic = {"item":[
		        ]}
	
	# 仮で年も月も12回分集計するものとする
	getCount = 0
	amazon = Amazon.Amazon()
	power = ""
	month_flg = False
	
	countLimit = 5
	if (month != 0):
		month_flg = True
		countLimit = 12
	
	while(getCount < countLimit):
		if (month == 0) :
			power = "pubdate:during " + str(pubDate)
		else :
			power = "pubdate:during " + str(month) + "-" + str(pubDate)
			
		print ("min:" + str(minPrice) +  " max:" + str(maxPrice) + " page:" + str(pageCnt) + "power: " + power)
		time.sleep(sleepTime)
		dic,status = amazon.amazonItemSearch(pageCnt, node, "Books", minPrice, maxPrice, power)
		totalDic["item"].extend(dic["item"])
		totalPage = int(dic["totalpages"])
		print ("totalPage: " + str(totalPage))
		
		if (status == 1):
			print ("node is over flow by pubData:" + power + " min:" +str(minPrice) +  " max:" + str(maxPrice) + " totalPage:" + str(totalPage) + " totalresults:" + dic["totalresults"])
			# さらに月で分割する
			if (not month_flg):
				totalDic["item"].extend(getPubdatePageData(node , minPrice, maxPrice, pubDate, 12))
			else :
				print ("node is over flow by pubDataMonth:" +  power + " min:" +str(minPrice) +  " max:" + str(maxPrice) + " totalPage:" + str(totalPage) + " totalresults:" + dic["totalresults"])
				totalDic["item"].extend(getYomiganaPageData(node , minPrice, maxPrice, power))
		else :
			while (totalPage > pageCnt):
				time.sleep(sleepTime)
				pageCnt += 1
				print ("page:" + str(pageCnt) + " totalPage:" + str(totalPage))
				dic,status = amazon.amazonItemSearch(pageCnt, node, "Books", minPrice, maxPrice, power)
				totalDic["item"].extend(dic["item"])
		
		# １年引く
		if (month_flg is True):
			month -= 1
		else :
			pubDate -= 1
			
		getCount += 1
		pageCnt = 1
	
	if (not month_flg) :
		# 1900年より前のものをまとめて取得
		power = "pubdate:before " + str(pubDate)
		print ("min:" + str(minPrice) +  " max:" + str(maxPrice) + " page:" + str(pageCnt) + "power: " + power)
		dic,status = amazon.amazonItemSearch(pageCnt, node, "Books", minPrice, maxPrice, power)
		totalDic["item"].extend(dic["item"])
		totalPage = int(dic["totalpages"])
		
		if (status == 1):
			if (pubDate  < 1900):
				print ("node is over flow by pubDataMinmum:" + str(pubDate) + " min:" +str(minPrice) +  " max:" + str(maxPrice) + " totalPage:" + str(totalPage) + " totalresults:" + dic["totalresults"])
				totalDic["item"].extend(getYomiganaPageData(node , minPrice, maxPrice, power))
			else :
				print ("node is over flow by before pubData:" + str(pubDate) + " min:" +str(minPrice) +  " max:" + str(maxPrice) + " totalPage:" + str(totalPage) + " totalresults:" + dic["totalresults"])
				totalDic["item"].extend(getPubdatePageData(node , minPrice, maxPrice, pubDate, 0))
				
		else :
			while (totalPage > pageCnt):
				time.sleep(sleepTime)
				pageCnt += 1
				print ("page:" + str(pageCnt) + " totalPage:" + str(totalPage))
				dic,status = amazon.amazonItemSearch(pageCnt, node, "Books", minPrice, maxPrice, power)
				totalDic["item"].extend(dic["item"])
	
	return totalDic["item"]


def getCutPageData(node, minPrice, priceRange, limit):
	global sleepTime
	pageCnt = 1
	totalDic = {"item":[
		        ]}
	amazon = Amazon.Amazon()
	maxPrice = minPrice + priceRange
	
	ru = resource.getrusage(resource.RUSAGE_SELF)
	#print ("use memory:" + str(ru.ru_maxrss))
	
	tracemalloc.start()
	
	today = datetime.date.today()
	# YYYYで表示
	yyyy = int(today.strftime("%Y"))
	
	for i in range(10):
		time.sleep(sleepTime)
		if (i != 0):
			minPrice = maxPrice + 1
			maxPrice = maxPrice + priceRange
		
		print ("min:" + str(minPrice) +  " max:" + str(maxPrice) + " page:" + str(pageCnt))
		dic,status = amazon.amazonItemSearch(pageCnt, node, "Books", minPrice, maxPrice)
		totalDic["item"].extend(dic["item"])
		totalPage = int(dic["totalpages"])
		if (status == 1):
			print ("node is over flow by Price:" + node + " min:" +str(minPrice) +  " max:" + str(maxPrice) + " totalPage:" + str(totalPage) + " totalresults:" + dic["totalresults"])
			# ページ分割を繰り返す
			if (int((maxPrice - minPrice) /10) < 1):
				totalDic["item"].extend(getPubdatePageData(node , minPrice, maxPrice, yyyy, 0))
				totalDic["item"].extend(getNullPubdatePageData(node, minPrice,maxPrice))
			else :
				getCutPageData(node , minPrice, int((maxPrice - minPrice) /10), maxPrice)
		else :
			while (totalPage > pageCnt):
				time.sleep(sleepTime)
				pageCnt += 1
				print ("page:" + str(pageCnt) + " totalPage:" + str(totalPage))
				dic,status = amazon.amazonItemSearch(pageCnt, node, "Books",minPrice,maxPrice)
				totalDic["item"].extend(dic["item"])
			
		pageCnt = 1
	
	#ループを抜けてリミットまで達していない場合はリミットまでを再度取得する
	if (maxPrice < limit) :
		minPrice = maxPrice + 1
		maxPrice = limit
		print ("min:" + str(minPrice) +  " max:" + str(maxPrice) + " page:" + str(pageCnt))
		dic,status = amazon.amazonItemSearch(pageCnt, node, "Books",minPrice,maxPrice)
		totalDic["item"].extend(dic["item"])
		totalPage = int(dic["totalpages"])
		if (status == 1):
			print ("node is over flow by Price:" + node + " min:" +str(minPrice) +  " max:" + str(maxPrice) + " totalPage:" + str(totalPage) + " totalresults:" + dic["totalresults"])
			# ページ分割を繰り返す
			if (int((maxPrice - minPrice) /10) < 1):
				totalDic["item"].extend(getPubdatePageData(node , minPrice, maxPrice, yyyy, 0))
				totalDic["item"].extend(getNullPubdatePageData(node, minPrice,maxPrice))
			else :
				getCutPageData(node , minPrice, int((maxPrice - minPrice) /10), maxPrice)
			
		else :
			while (totalPage > pageCnt):
				time.sleep(sleepTime)
				pageCnt += 1
				print ("page:" + str(pageCnt) + " totalPage:" + str(totalPage))
				dic,status = amazon.amazonItemSearch(pageCnt, node, "Books",minPrice,maxPrice)
				totalDic["item"].extend(dic["item"])
	
	setOutputeDB(totalDic)
	del totalDic
	gc.collect()
	
	snapshot = tracemalloc.take_snapshot()
	top_stats = snapshot.statistics('lineno')
	print("[ Top 10 ]")
	for stat in top_stats[:10]:
		print(stat)
	
	return


def setOutputeDB(totalDic):
	global categoryUP
	
	# DB登録
	d = datetime.datetime.today()
	print('d:', d,'db update start')
	mysql = Mysql.Mysql()
	totalInstCount = 0
	totalUpdtCount = 0
	totalProcCount = 0
	for itemLine in totalDic["item"]:
		instCount = 0
		instCount = mysql.updateProductInfo(itemLine, categoryUP)
		totalProcCount += 1
		
		if ((totalProcCount % 100) == 0):
			time.sleep(10)
		
		time.sleep(0.01)
		if instCount == 1:
			totalInstCount += 1
		else :
			totalUpdtCount += 1
			
	print ("db update finish! total:" + str(totalInstCount + totalUpdtCount) + " new:" + str(totalInstCount) + " update:" + str(totalUpdtCount))
	
	del mysql
	gc.collect()
	
	return

def getNodeItem(node):
	amazon = Amazon.Amazon()
	totalDic = {"item":[
		        ]}
	dic = {}
	status = 0
	
	# 3200207051のブラウズノードを取得
	## ノードごとにアイテム取得のループをする
	
	### 取得がなくなるまでループ
	pageCnt = 1
	nextFlg = 0
	minPrice = 0
	maxPrice =  2000
	priceRange = (maxPrice - minPrice) /10
	cutPage = 0
	
	print ("node:" + node + " start")
	
	dic,status = amazon.amazonItemSearch(pageCnt, node, "Books")
	totalDic["item"].extend(dic["item"])
	totalPage = int(dic["totalpages"])
	print ("page:" + str(pageCnt) + " totalPage:" + str(totalPage))
	
	# 戻ってきた件数が多すぎる。
	## 価格のレンジ指定でデータを取得
	if (status == 1):
		print ("node is 10page over:" + node )
		getCutPageData(node , minPrice, priceRange , 99999)
		
	else :
		while (totalPage > pageCnt):
			time.sleep(sleepTime)
			pageCnt += 1
			print ("page:" + str(pageCnt) + " totalPage:" + str(totalPage))
			dic,status = amazon.amazonItemSearch(pageCnt, node, "Books")
			totalDic["item"].extend(dic["item"])
			
	print ("total:" + str(len(totalDic["item"])))
	setOutputeDB(totalDic)
	
	print ("node:" + node + " end")

if __name__ == '__main__':
	node = "3197885051"
	d = datetime.datetime.today()
	print('d:', d,'start')

	# OOM Killer対象外にする
	pid = os.getpid()
	cmd = "sudo echo -1000 > /proc/" + str(pid) + "/oom_score_adj"
	print ("cmd:" + cmd)
	subprocess.call( cmd, shell=True  ) 
	
	# soft は初期メモリ量と、追加時のメモリ量。
	softmem = 64 * 1024 * 1024  # 64MB
	# hard は上限値。
	hardmem = 512 * 1024 * 1024 # 512MB
	# メモリの上限を設定する。単位はバイト。
	resource.setrlimit(resource.RLIMIT_DATA, (softmem, hardmem))
	
	# 再度上限値を取得して値を確認する。
	value = resource.getrlimit(resource.RLIMIT_DATA)
	print ("set limit memory:" + str(value)) # (67108864, 536870912)

	# カテゴリ巡回モードかを確認
	args = sys.argv
	if (len(args) > 1 and args[1] == 'cate'): 
		categoryUP = True
		
	if (categoryUP is True) :
		print ("カテゴリ巡回モードです")
		# main処理開始、kindle読みの登録コンテンツを対象とする
		
		#ノード指定がある場合は、そのノードから調べる
		if (len(args) > 2 and len(args[2]) > 0):
			node = args[2]
		
		# kindle読み放題のnode
		dic = {}
		amazon = Amazon.Amazon()
		dic = amazon.amazonBrowseNode(node)
		for caegoryLine in dic["category"]:
			print ("getNodeItem start Node:" + caegoryLine["browsenode_id"] + " NodeName:" + caegoryLine["browsenode_name"])
			main(caegoryLine["browsenode_id"])
			#main("3198378051")
			print ("getNodeItem end Node:" + caegoryLine["browsenode_id"] + " NodeName:" + caegoryLine["browsenode_name"])
			print ("============================================")
			
	else :
		print ("全件取得モードです")
		# カテゴリコードの指定がある場合は、該当カテゴリ内の全件取得とする
		if (len(args) > 2 and len(args[2]) > 0):
			mainSingleCategory(args[2])
		else :
			# main処理開始、kindle読み放題全体を対象とする
			main(node)
	
	d = datetime.datetime.today()
	print('d:', d,'end')
	
	#getPubdatePageData("3200207051" , 324, 1000, 1901, 0)
	#getPubdatePageData("3197885051" , 108, 108, 1901, 0)
	#getSortPricePageData("3197885051", 108,108, "pubdate:before 1896 and title-begins:ナン and not title:誕生日占い and not title:365誕生星占い\
	# and not asin:B00NGEW9QA" \
	# , "price")
	#itemLine = {}
	#itemLine["asin"]='B010L0C710'
	#itemLine["title"]='タイトルテスト'
	#itemLine["author"] = 'テストAさん'
	#itemLine["publication_date"] = '2016-11-23'
	#itemLine["publisher"] = '出版社A'
	#itemLine["release_date"] = '2016-11-23'
	#itemLine["detail_pageurl"] = 'http://yahoo.co.jp'
	#itemLine["medium_image"] = 'http://yahoo.co.jp/image/image.jpg'
	#
	#mysql = Mysql.Mysql()
	#mysql.updateProductInfo(itemLine)
