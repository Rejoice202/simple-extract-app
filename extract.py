#!/usr/bin/python3

import os
import time
import py7zr
import zipfile
import tarfile
import gzip

# folderPath = "F:\English Dubbed Anniation\测试py解压"
# _7z_password = "www.edatribe.com"
extract_file_type = ['jpg','mkv']
compressed_file_type = ['7z','zip','tar','gz']
'''
result['code']
0:解压完毕
1:文件夹路径无效
2:压缩类型不支持
'''
def extract_file(folderPath, fileType, password):

	result = {}
	result['code'] = 0
	result['success_times'] = 0
	result['failed_times'] = 0
	result['unknown_times'] = 0
	result['success_file_list'] = []
	result['failed_file_list'] = []
	result['unknown_file_list'] = []
	result['time_cost'] = 0

	begin = time.time()
	un_result = 2
	print("folderPath:", folderPath)
	print("password:", password)
	if not folderPath or folderPath == "":
		print("Invalid folderPath")
		result['code'] = 1
		return result

	if fileType == "All":
		result = extract_all(folderPath, fileType, password, result)
	# 待重构
	elif fileType == "7z":
		for root, dirs, files in os.walk(folderPath, topdown=False):
			for fileName in files:
				# print(fileName)
				filePath = root + "\\" + fileName
				if fileName.split(".")[-1] == "7z":
					un_result = un_7z(root, filePath, password)
					if un_result == 0:  # 解压成功
						result['success_file_list'].append(fileName)
						result['success_times'] += 1
					elif un_result == 1:  # 解压失败
						result['failed_file_list'].append(fileName)
						result['failed_times'] += 1
					else:  # 不支持解压的文件，或无需解压的文件
						result['unknown_file_list'].append(fileName)
						result['unknown_times'] += 1
		# print("one file,result = ",result)
	elif fileType == "zip":
		for root, dirs, files in os.walk(folderPath, topdown=False):
			for fileName in files:
				# print(fileName)
				filePath = root + "\\" + fileName
				if fileName.split(".")[-1] == "zip":
					un_result = un_zip(root, filePath, password)
					if un_result == 0:  # 解压成功
						result['success_file_list'].append(fileName)
						result['success_times'] += 1
					elif un_result == 1:  # 解压失败
						result['failed_file_list'].append(fileName)
						result['failed_times'] += 1
					else:  # 不支持解压的文件，或无需解压的文件
						result['unknown_file_list'].append(fileName)
						result['unknown_times'] += 1
		# print("one file,result = ",result)
	elif fileType == "tgz":
		for root, dirs, files in os.walk(folderPath, topdown=False):
			for fileName in files:
				# print(fileName)
				filePath = root + "\\" + fileName
				if fileName.split(".")[-1] == "gz" and fileName.split(".")[-2] == "tar":
					un_result = un_tgz(root, filePath, password)
					if un_result == 0:  # 解压成功
						result['success_file_list'].append(fileName)
						result['success_times'] += 1
					elif un_result == 1:  # 解压失败
						result['failed_file_list'].append(fileName)
						result['failed_times'] += 1
					else:  # 不支持解压的文件，或无需解压的文件
						result['unknown_file_list'].append(fileName)
						result['unknown_times'] += 1
		# print("one file,result = ",result)
	elif fileType == "gz":
		for root, dirs, files in os.walk(folderPath, topdown=False):
			for fileName in files:
				# print(fileName)
				filePath = root + "\\" + fileName
				if fileName.split(".")[-1] == "gz" and fileName.split(".")[-2] != "tar":
					un_result = un_gz(root, filePath, password)
					if un_result == 0:  # 解压成功
						result['success_file_list'].append(fileName)
						result['success_times'] += 1
					elif un_result == 1:  # 解压失败
						result['failed_file_list'].append(fileName)
						result['failed_times'] += 1
					else:  # 不支持解压的文件，或无需解压的文件
						result['unknown_file_list'].append(fileName)
						result['unknown_times'] += 1
		# print("one file,result = ",result)
	else:
		print("Invalid fileType")
		result['code'] = 2
	end = time.time()
	result['time_cost'] = end-begin
	return result


def extract_all(folderPath, fileType, password, result):
	for root, dirs, files in os.walk(folderPath, topdown=False):
		print("root",root)
		# print("dirs",dirs)
		# print("files",files)
		for fileName in files:
			# print(fileName)
			filePath = root + "\\" + fileName
			if fileName.split(".")[-1] == "7z":
				un_result = un_7z(root, filePath, password)
			elif fileName.split(".")[-1] == "zip":
				un_result = un_zip(root, filePath, password)
			elif fileName.split(".")[-1] == "gz":
				if fileName.split(".")[-2] == "tar":
					un_result = un_tgz(root, filePath, password)
				else:
					un_result = un_gz(root, filePath, password)
			else:
				un_result = 2
			if un_result == 0:	#解压成功
				result['success_file_list'].append(fileName)
				result['success_times'] += 1
			elif un_result == 1:	#解压失败
				result['failed_file_list'].append(fileName)
				result['failed_times'] += 1
			else:	#不支持解压的文件，或无需解压的文件
				result['unknown_file_list'].append(fileName)
				result['unknown_times'] += 1
			# print("one file,result = ",result)
	return result

# 解压后若有同名文件则自动覆盖
def un_7z(folderPath,filePath,_7z_password):
	try:
		if py7zr.is_7zfile(filePath):
			with py7zr.SevenZipFile(filePath, password=_7z_password, mode='r') as sevenZ_f:
				sevenZ_f.extractall(folderPath)
		return 0
	except:
		return 1

# 解压后若有同名文件则自动覆盖
def un_zip(folderPath,filePath,password):
	try:
		if zipfile.is_zipfile(filePath):
			zip_file = zipfile.ZipFile(filePath)
			for file in zip_file.namelist():
				try:
					zip_file.extract(file, folderPath, password) # 一个压缩包内可能有多个文件，解压所有文件到同一路径
				except:
					zip_file.extract(file, folderPath) # 无需密码的文件，带上密码就出错
		return 0
	except:
		return 1

def un_tgz(folderPath,filePath,password):
	try:
		tar = tarfile.open(filePath,'r')
		tar.extractall(path=folderPath)
		tar.close()
		return 0
	except:
		return 1

def un_gz(folderPath,filePath,password):
	try:
		g_file = gzip.GzipFile(filePath)
		open(folderPath, "w+").write(g_file.read())
		g_file.close()
		return 0
	except:
		return 1

def get_compressed_filesize(folderPath,fileType):
	all_file_zise = 0
	for root, dirs, files in os.walk(folderPath, topdown=False):
		# print("root", root)
		# print("dirs", dirs)
		# print("files", files)
		for fileName in files:
			# print(fileName)
			filePath = root + "\\" + fileName
			if fileName.split(".")[-1] in compressed_file_type:
				if fileType == "All":all_file_zise += os.path.getsize(filePath)
				elif fileType == "zip":
					if fileName.split(".")[-1] == "zip":
						all_file_zise += os.path.getsize(filePath)
				elif fileType == "7z":
					if fileName.split(".")[-1] == "7z":
						all_file_zise += os.path.getsize(filePath)
				elif fileType == "tgz":
					if fileName.split(".")[-1] == "gz" and fileName.split(".")[-2] == "tar":
						all_file_zise += os.path.getsize(filePath)
				elif fileType == "gz":
					if fileName.split(".")[-1] == "gz" and fileName.split(".")[-2] != "tar":
						all_file_zise += os.path.getsize(filePath)
	return all_file_zise

def remove_compressed_file(folderPath):
	try:
		for root, dirs, files in os.walk(folderPath, topdown=False):
			print("root", root)
			print("dirs", dirs)
			print("files", files)
			for fileName in files:
				# print(fileName)
				filePath = root + "\\" + fileName
				if fileName.split(".")[-1] in compressed_file_type:
					os.remove(filePath)
		return True
	except:
		return False