#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import sys
import MeCab
import mojimoji
import KanaRoma

def getOnyomi(string):
	#【フルカラー】となっている場合、【】を削除する】
	string = re.sub(r'^【.*カラー.*】', "", string)
	
	#【】で始まる場合、【】を削除
	string = re.sub(r'【([^】]+)】', r'\1', string)
	
	# アルファベットと数値は全角の場合、読み仮名を振ることができるので全角にする（先頭のみ）
	# 英単語は全角にすると変換ができないので
	# 先頭がアルファベット一文字の場合
	matchObj = re.search(r'^([a-z])[^a-z]', string)
	if matchObj:
		#print ("HIT  "  + matchObj.group(1)) # マッチした文字列： abc
		zenkaku = mojimoji.han_to_zen(matchObj.group(1), kana=False)
		string  = zenkaku + string[1:len(string)]
		
	# 先頭が数値の場合
	matchObj = re.search(r'^([0-9]+)', string)
	if matchObj:
		#print ("HIT  "  + matchObj.group()) # マッチした文字列： abc
		zenkaku = mojimoji.han_to_zen(matchObj.group(1), kana=False)
		string  = zenkaku + string[matchObj.end():len(string)]
	
	# mecabで変換する
	m = MeCab.Tagger ("-Oyomi")
	onyomi = m.parse (string)
	
	#先頭がカタカナになっていないものは半角にしてローマ字変換でヒラガナにする
	matchObj = re.search(r'^[^ァ-ン]+', onyomi)
	if matchObj:
		# 半角変換
		#print ("HIT  "  + matchObj.group()) # マッチした文字列： abc
		zenkaku = mojimoji.zen_to_han(matchObj.group(0), kana=False)
		#print ("HIT  "  + zenkaku) # マッチした文字列： abc
		# アルファベットを含む場合はローマ字変換
		matchObjAlpha = re.search(r'^[a-z,A-Z]+', zenkaku)
		if matchObjAlpha:
			#print ("HIT  "  + matchObjAlpha.group()) # マッチした文字列： abc
			#print ("HIT  "  + KanaRoma.romaji2katakana(matchObjAlpha.group()))
			onyomi  = KanaRoma.romaji2katakana(matchObjAlpha.group()) + onyomi[matchObjAlpha.end():len(onyomi)]
		else:
			# アルファベット以外のカタカナがある場合は、カタカナの場所まで切り取りする
			onyomi  = onyomi[matchObj.end():len(onyomi)]
			
	return re.sub(r'[\n\r]', "", onyomi)


def make_kana_idx(string):
	"""カタカナのＩＤＸ作成（アカサタナ）"""
	
	# 先頭が数値の場合
	matchObj = re.search(r'^[ァ-ン]', string)
	idx = 99
	if matchObj:
		if (re.search(r'[アイウエオ]', matchObj.group())):
			idx = 0
		elif(re.search(r'[カキクケコ]', matchObj.group())):
			idx = 1
		elif(re.search(r'[サシスセソ]', matchObj.group())):
			idx = 2
		elif(re.search(r'[タチツテト]', matchObj.group())):
			idx = 3
		elif(re.search(r'[ナニヌネノ]', matchObj.group())):
			idx = 4
		elif(re.search(r'[ハヒフヘホ]', matchObj.group())):
			idx = 5
		elif(re.search(r'[マミムメモ]', matchObj.group())):
			idx = 6
		elif(re.search(r'[ヤユヨ]', matchObj.group())):
			idx = 7
		elif(re.search(r'[ラリルレロ]', matchObj.group())):
			idx = 8
		elif(re.search(r'[ワヲン]', matchObj.group())):
			idx = 9
		elif(re.search(r'[ガギグゲゴ]', matchObj.group())):
			idx = 10
		elif(re.search(r'[ザジズゼゾ]', matchObj.group())):
			idx = 11
		elif(re.search(r'[ダヂヅデド]', matchObj.group())):
			idx = 12
		elif(re.search(r'[バビブベボ]', matchObj.group())):
			idx = 13
		elif(re.search(r'[パピプペポ]', matchObj.group())):
			idx = 14
		else:
			idx = 99
	return idx