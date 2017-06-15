# -*- coding:utf-8 -*-
import bottlenose
import codecs
import types
import time
import Furigana
import AmazonDataCheck
import re
from bs4 import BeautifulSoup

def error_handler(err):
  ex = err['exception']
  if isinstance(ex, HTTPError) and ex.code == 503:
    time.sleep(random.expovariate(0.1))
    return True

class Amazon(object):

	_instance = None

	# シングルトンにする
	def __new__(cls):
		if cls._instance is None:
			cls._instance = super().__new__(cls)
		return cls._instance

	def __init__(self):
		AWSAccessKeyId="ID"
		AWSSecretKey="PW"
		AssosiateId = "ID"
		amazon = bottlenose.Amazon(AWSAccessKeyId,
                           AWSSecretKey,
                           AssosiateId ,
                           Region='JP')
		self.amazon = amazon

	def amazonBrowseNode(self,node):

		dic = {"parent_name":"","parent_id":"","category":[
		        ]}

		response = self.amazon.BrowseNodeLookup(BrowseNodeId=node)
		soup = BeautifulSoup(response,"lxml")

		dic["parent_name"] = soup.findAll("name")[0].text
		dic["parent_id"] = node

		# 子ノードがない場合は、自分自身を返却
		if (len(soup.findAll("children")) == 0):
			print ("not found child node:", node)
			categoryLine = {}
			categoryLine["browsenode_id"] = node
			categoryLine["browsenode_name"] = "not found child"
			dic["category"].append(categoryLine)
			return dic

		for browsenode in soup.findAll("children")[0].findAll("browsenode"):
			categoryLine = {}
			#print (browsenode.browsenodeid.contents[0])
			#print (browsenode.findAll('name')[0].text)
			categoryLine["browsenode_id"] = browsenode.browsenodeid.contents[0]
			categoryLine["browsenode_name"] = browsenode.findAll('name')[0].text
			dic["category"].append(categoryLine)

		return dic

	def amazonItemSearch(self,item_page,node,category,*args, **kwargs):

		response = ""
		sort = ""
		if (item_page < 1):
			item_page = 1

		if (kwargs.get('sort') == "price") :
			sort="price"
		elif (kwargs.get('sort') == "-price") :
			sort="-price"
		else :
			sort="salesrank"
			
		try:
			if (len(args) ==2) :
				response = self.amazon.ItemSearch(
				SearchIndex=category,
				BrowseNode=node,
				ResponseGroup="ItemAttributes,Images,EditorialReview",
				Sort=sort,
				ItemPage = item_page,
				MinimumPrice = args[0],
				MaximumPrice = args[1],
				ErrorHandler=error_handler)
			elif (len(args) ==3) :
				response = self.amazon.ItemSearch(
				SearchIndex=category,
				BrowseNode=node,
				ResponseGroup="ItemAttributes,Images,EditorialReview",
				Sort=sort,
				ItemPage = item_page,
				MinimumPrice = args[0],
				MaximumPrice = args[1],
				Power =  args[2],
				ErrorHandler=error_handler)

			else :
				#結果ページ数取得
				response = self.amazon.ItemSearch(
				SearchIndex=category,
				BrowseNode=node,
				ResponseGroup="ItemAttributes,Images,EditorialReview",
				Sort=sort,
				ItemPage = item_page,
				ErrorHandler=error_handler)
		except Exception as e:
			retryCnt = 0;
			if (kwargs.get('retry') == None) :
				retryCnt = 1
			else :
				retryCnt = int(kwargs.get('retry'))

			if (retryCnt < 3):
				print ("HTTP ERROR RETRY:" + str(retryCnt))
				time.sleep(60)
				retryCnt += retryCnt
				return self.amazonItemSearch(item_page,node,category,*args,retry=retryCnt)
			else :
				raise e

		soup = BeautifulSoup(response,"lxml")

		dic = {"item":[
		        ]}
		dic["totalresults"] = soup.findAll("totalresults")[0].text
		dic["totalpages"] = soup.findAll("totalpages")[0].text

		#ソート指定がない場合は、10ページ以上存在する場合はエラーとする
		if (int(dic["totalpages"]) > 10 and kwargs.get('sort') == None) :
			return dic , 1;

		for itemData in soup.findAll("item"):
			itemLine = {}
			author=[]
			title=itemData.title.contents[0]

			#print ("!!" + str(itemData.editorialreviews.editorialreview.content.contents[0]))

			if itemData.publicationdate==None:
				publicationdate = "1900-01-01"
			else:
				publicationdate=itemData.publicationdate.contents[0]

			if itemData.releasedate==None:
				releasedate = "1900-01-01"
			else:
				releasedate=itemData.releasedate.contents[0]

			detailpageurl=itemData.detailpageurl.contents[0]

			if itemData.mediumimage==None:
				mediumimage = "NONE"
			else:
				mediumimage=itemData.mediumimage.contents[0].text

			if itemData.publisher==None:
				publisher = "NONE"
			else:
				publisher = itemData.publisher.contents[0]

			if itemData.author==None:
				author.append("NONE")
			else:
				for i in range(len(itemData.author)):
					author.append(itemData.author.contents[i])

			if itemData.editorialreviews ==None:
				editorialreview = "NONE"
			else:
				editorialreview = itemData.editorialreviews.editorialreview.content.contents[0]
				p = re.compile(r"<[^>]*?>")
				editorialreview = p.sub("", editorialreview)
				
			itemLine["asin"]=itemData.asin.contents[0]
			itemLine["node"]=node
			itemLine["title"] = title
			itemLine["title_kana"] = Furigana.getOnyomi(title)
			itemLine["kana_idx"] = Furigana.make_kana_idx(itemLine["title_kana"])
			itemLine["author"] = author[0]
			itemLine["adult_flg"] = AmazonDataCheck.chkAdultPublisher(publisher)
			itemLine["comment"] = editorialreview
			itemLine["publication_date"] = publicationdate
			itemLine["publisher"] = publisher
			itemLine["release_date"] = releasedate
			itemLine["detail_pageurl"] = detailpageurl
			itemLine["medium_image"] = mediumimage
			dic["item"].append(itemLine)

			#print ("asin:" + itemLine["asin"] + ",title:" + title + ",title_kana:" + itemLine["title_kana"] )
			print ("asin:" + itemLine["asin"] + ",title:" + title )
			#print ("publisher=" +publisher)
			#print ("author=" +author[0])
			#print ("publicationdate=" +publicationdate)
			#print ("releasedate=" + releasedate)
			#print ("detailpageurl=" + detailpageurl)
			#print ("mediumimage=" + mediumimage)

		return dic ,0
