# coding: utf-8

import MySQLdb

class Mysql(object):

	def __init__(self):
		# 接続する 
		self.con = MySQLdb.connect(
			user='user',
			passwd='PW',
			host='localhost',
			db='DB',
			charset="utf8")
		self.con.autocommit(False)
		
	
	def getCategoryProduct(self, node):
		# select なければinsert,あればupdate
		# カーソルを取得する
		cur= self.con.cursor()
		
		#sql = "select title,asin from m_product_info where node1 = %s and adult_flg = 0 order by title"
		sql = "select title,asin from m_product_info where node1 = %s order by title"
		cur.execute(sql, (node,))
		# 実行結果をすべて取得する
		rows = cur.fetchall()
		
		
		return rows
		
	def updateSeriesInfo(self, itemLine):
		# select なければinsert,あればupdate
		# カーソルを取得する
		cur= self.con.cursor()
		instCount = 0
		
		try: 
			# 対象ASINのシリーズを取得、シリーズ全体数も確認する
			sql = "select * from m_series_info where min_asin = %s and series_count = %s"
			cur.execute(sql, (itemLine["min_asin"],itemLine["series_count"],))
			# 実行結果をすべて取得する
			rows = cur.fetchall()
			
			# 存在する場合は更新日のみupdate
			if (len(rows) > 0):
				update_sql = "update `m_series_info` SET \
				`updt_ymd`= now() \
				where min_asin = %s ;"
				
				cur.execute(update_sql, 
				(itemLine["min_asin"]
				,))
				
			# 存在しない場合
			else:
				# 対象ASINのシリーズを取得
				sql = "select * from m_series_info where min_asin = %s"
				cur.execute(sql, (itemLine["min_asin"],))
				# 実行結果をすべて取得する
				rows = cur.fetchall()
			
				# 存在する場合はupdate
				if (len(rows) > 0):
					update_sql = "update `m_series_info` SET \
					`min_asin`=%s,\
					`series_title`=%s,\
					`series_min`=%s,\
					`series_max`=%s,\
					`series_count`=%s,\
					`series_updt_ymd`= now(),\
					`updt_ymd`= now() \
					where min_asin = %s ;"
					
					cur.execute(update_sql, 
					(
					itemLine["min_asin"],
					itemLine["series_title"],
					itemLine["series_min"],
					itemLine["series_max"],
					itemLine["series_count"],
					itemLine["min_asin"]
					, ))
					
				# 存在しない場合
				else :
					insert_sql = "insert into `m_series_info` ( \
					`min_asin`,\
					`series_title`,\
					`series_min`,\
					`series_max`,\
					`series_count`,\
					`series_updt_ymd`,\
					`inst_ymd`\
					) \
					VALUES (\
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					now(), \
					now() \
					);"
				
					cur.execute(insert_sql, 
					(
					itemLine["min_asin"],
					itemLine["series_title"],
					itemLine["series_min"],
					itemLine["series_max"],
					itemLine["series_count"]
					, ))
					
					instCount= 1
			
			self.con.commit()
			return instCount
			
		except Exception as e:
			self.con.rollback()
			raise e
		finally:
			cur.close()
			
	
	def updateProductInfo(self, itemLine, categoryUP):
		
		# select なければinsert,シリーズ数に変更なければ更新日のみ更新、シリーズ数に変更があればシリーズ数を更新
		# カーソルを取得する
		cur= self.con.cursor()
		instCount = 0
		
		try: 
			# 対象ASINの商品を取得
			sql = "select * from m_product_info where asin = %s"
			cur.execute(sql, (itemLine["asin"],))
			# 実行結果をすべて取得する
			rows = cur.fetchall()
			
			# 存在する場合はupdate
			if (len(rows) > 0):
				update_sql = ""
				if (categoryUP is True):
					update_sql = "update `m_product_info` SET \
					`title`=%s,\
					`title_kana`=%s,\
					`kana_idx`=%s,\
					`node2`=%s,\
					`author`=%s,\
					`publisher`=%s,\
					`adult_flg`=%s,\
					`comment`=%s,\
					`publication_date`=%s,\
					`release_date`=%s,\
					`detail_pageurl`=%s,\
					`medium_image`=%s,\
					`updt_ymd`= now() \
					where asin = %s ;"
				else :
					update_sql = "update `m_product_info` SET \
					`title`=%s,\
					`title_kana`=%s,\
					`kana_idx`=%s,\
					`node1`=%s,\
					`author`=%s,\
					`publisher`=%s,\
					`adult_flg`=%s,\
					`comment`=%s,\
					`publication_date`=%s,\
					`release_date`=%s,\
					`detail_pageurl`=%s,\
					`medium_image`=%s,\
					`updt_ymd`= now() \
					where asin = %s ;"
				
				cur.execute(update_sql, 
				(
				itemLine["title"],
				itemLine["title_kana"],
				itemLine["kana_idx"],
				itemLine["node"],
				itemLine["author"],
				itemLine["publisher"],
				itemLine["adult_flg"],
				itemLine["comment"],
				itemLine["publication_date"],
				itemLine["release_date"],
				itemLine["detail_pageurl"],
				itemLine["medium_image"],
				itemLine["asin"]
				, ))
			
			# 存在しない場合はinsert
			else:
				insert_sql = ""
				if (categoryUP is True):
					insert_sql = "insert into `m_product_info` ( \
					`asin`,\
					`node2`,\
					`title`,\
					`title_kana`,\
					`kana_idx`,\
					`author`,\
					`publisher`,\
					`adult_flg`,\
					`comment`,\
					`publication_date`,\
					`release_date`,\
					`detail_pageurl`,\
					`medium_image`,\
					`inst_ymd`\
					) \
					VALUES (\
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					now() \
					);"
				else :
					insert_sql = "insert into `m_product_info` ( \
					`asin`,\
					`node1`,\
					`title`,\
					`title_kana`,\
					`kana_idx`,\
					`author`,\
					`publisher`,\
					`adult_flg`,\
					`comment`,\
					`publication_date`,\
					`release_date`,\
					`detail_pageurl`,\
					`medium_image`,\
					`inst_ymd`\
					) \
					VALUES (\
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					%s, \
					now() \
					);"
				
				cur.execute(insert_sql, 
				(
				itemLine["asin"],
				itemLine["node"],
				itemLine["title"],
				itemLine["title_kana"],
				itemLine["kana_idx"],
				itemLine["author"],
				itemLine["publisher"],
				itemLine["adult_flg"],
				itemLine["comment"],
				itemLine["publication_date"],
				itemLine["release_date"],
				itemLine["detail_pageurl"],
				itemLine["medium_image"]
				, ))
				
				instCount= 1
			
			self.con.commit()
			return instCount
			
		except Exception as e:
			self.con.rollback()
			raise e
		finally:
			cur.close()
	
	
	def __del__( self ):
		self.con.close()
