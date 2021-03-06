import logging, json, os, sys, platform, re, time, stat
from os.path import getsize
try:
	def replace(text):
		match = re.findall('\$\{.+?\}', text)
		if match != None:
			for varible in match:
				return text.replace(varible, os.environ[varible[2: -1]].replace("\\", "\\\\"))
		#match = re.findall('#\{HKCR}\{.+?,.+?\}', text)
		#if match != None:
		#	for varible in match:
		#		return text.replace(varible, os.environ[varible[2: -1]])
		#match = re.findall('#\{HKCU}\{.+?,.+?\}', text)
		#if match != None:
		#	for varible in match:
		#		return text.replace(varible, os.environ[varible[2: -1]])
		#match = re.findall('#\{HKLM}\{.+?,.+?\}', text)
		#if match != None:
		#	for varible in match:
		#		return text.replace(varible, os.environ[varible[2: -1]])
	def convert_size(size):
		try:
			if size >= 1000:
				if size >= 1000*1000:
					if size >= 1000*1000*1000:
						if size >= 1000*1000*1000*1000:
							total_size = str(format(size / (1000*1000*1000*1000), ".2f")) + "TB"
						else:
							total_size = str(format(size / (1000*1000*1000), ".2f")) + "GB"
					else:
						total_size = str(format(size / (1000*1000), ".2f")) + "MB"
				else:
					total_size = str(format(size / 1000, ".2f")) + "KB"
			else:
				total_size = str(format(size, ".2f")) + "B"
		except OSError:
			logging.error("索引失败!")
			input()
			sys.exit()
		return total_size
	logging.basicConfig(level = logging.INFO, format = '[%(asctime)s %(levelname)s] %(message)s', datefmt = '%H:%M:%S')
	logger = logging.getLogger(__name__)
	logging.info("")
	logging.info("	#==================================#")
	logging.info("	|   clean-toolx v1.2.3 By @延时qwq   |")
	logging.info("	#==================================#")
	logging.info("")
	if os.listdir("plugins"):
		clean_count, clean_size, total_size, total_count, plugin_count = 0, 0, 0, 0, 0
		for root,dirs,files in os.walk("plugins"):
			for file in files:
				if os.path.splitext(file)[-1]=='.json':
					plugin_count += 1
		if plugin_count == 0:
			logging.error("未检测到任何插件!")
			sys.exit()
		else:
			logging.info("检测到" + str(plugin_count) + "个插件.")
			print("\n")
		for root,dirs,files in os.walk("plugins"):
			for file in files:
				continue_signal = False
				if os.path.splitext(file)[-1] == ".json":
					try:
						plugin_data = open("plugins/" + file).read()
						plugin_data = plugin_data.replace("\\", "\\\\")
					except UnicodeDecodeError as e:
						logging.error("插件解析失败!请将插件编码设为GB2312(" + file + ").")
						logging.error("错误信息: " + str(e))
						print()
						continue
				else:
					continue
				try:
					plugin_config = json.loads(plugin_data)
				except json.decoder.JSONDecodeError as e:
					logging.error("插件解析失败!请检查插件完整性(" + file + ").")
					logging.error("错误信息: " + str(e))
					print()
					continue
				logging.info("插件名称: " + plugin_config["name"] + " (" + file + ")")
				logging.info("插件作者: " + plugin_config["author"])
				logging.info("插件版本: " + plugin_config["version_name"])
				if plugin_config["platform"].lower() != platform.system().lower():
					logging.error("此插件不适配此操作系统!")
					continue
				if "requires" in plugin_config:
					for path in plugin_config["requires"]:
						match = re.findall(r'\$\{.+?\}', path)
						if match != None:
							for varible in match:
								path = path.replace(varible, os.environ[varible[2: -1]])
						if os.path.exists(path) == False:
							logging.error("未安装此插件所需的软件!")
							continue_signal = True
				if continue_signal == True:
					continue
				for rule in plugin_config["rules"]:
					continue_signal = False
					rule_size = 0
					logging.info("")
					logging.info("正在索引 " + rule["name"] + " ...")
					path_list = []
					if "requires" in rule:
						for path in rule["requires"]:
							if os.path.exists(replace(path)) == False:
								logging.info("未检测到文件.")
								continue_signal = True
					if continue_signal == True:
						continue
					if "paths" in rule:
						for path in rule["paths"]:
							path = replace(path)
							logging.info("正在扫描 " + path + " ...")
							for path in os.popen("es /a-d -r \"" + path.replace("|", "^|") + "\"").readlines():
								path = path[: -1]
								try:
									total_size = total_size + getsize(path)
									rule_size = rule_size + getsize(path)
								except:
									continue
								path_list.append(path)
					else:
						logging.error("插件配置有误!请检查插件完整性(" + file + ").")
					file_count = len(path_list)
					if file_count == 0:
						logging.info("未检测到文件.")
						continue
					logging.info("")
					logging.info("检测到" + str(file_count) + "个文件(" + convert_size(rule_size) + "):")
					total_count = total_count + file_count
					count = 0
					for file_path in path_list:
						try:
							if os.path.isfile(file_path):
								filesize = convert_size(getsize(file_path))
							else:
								filesize = convert_size(0)
							logging.info("\t [" + filesize + "]\t" + file_path)
							count = count + 1
						except FileNotFoundError:
							path_list.remove(file_path)
						if count >= 10:
							logging.info("\t  ......\t ......")
							break
					logging.info("")
					if rule["warning_level"] == 0:
						pass
					elif rule["warning_level"] == 1:
						text = "[" + time.strftime("%H:%M:%S", time.localtime()) + " INFO] 按[Enter]开始清理..."
						if "descript" in rule:
							text = "[" + time.strftime("%H:%M:%S", time.localtime()) + " INFO] " + rule["descript"]
						input(text)
					elif rule["warning_level"] == 2:
						text = "[" + time.strftime("%H:%M:%S", time.localtime()) + " WARN] 这条规则可能会影响您的正常使用,确定继续吗?[Y/n]"
						if "descript" in rule:
							text = "[" + time.strftime("%H:%M:%S", time.localtime()) + " WARN] " + rule["descript"] + "[Y/n]"
						while True:
							answer = input(text)
							if answer.upper() == "N":
								break
							elif answer.upper() == "Y":
								logging.info("忽略警告.")
								break
							else:
								continue
						if answer.upper() == "N":
							continue
					elif rule["warning_level"] == 3:
						text = "[" + time.strftime("%H:%M:%S", time.localtime()) + " WARN] 这条规则会影响您的正常使用,确定继续吗?[y/N]"
						if "descript" in rule:
							text = "[" + time.strftime("%H:%M:%S", time.localtime()) + " WARN] " + rule["descript"] + "[y/N]"
						while True:
							answer = input(text)
							if answer.upper() == "N":
								break
							elif answer.upper() == "Y":
								logging.info("忽略警告.")
								break
							else:
								continue
						if answer.upper() == "N":
							continue
					elif rule["warning_level"] == 4:
						while True:
							text = "[" + time.strftime("%H:%M:%S", time.localtime()) + " WARN] 这条规则可能会损坏/删除您的数据,确定继续吗?[y/N]"
							if "descript" in rule:
								text = "[" + time.strftime("%H:%M:%S", time.localtime()) + " WARN] " + rule["descript"] + "[y/N]"
							answer = input(text)
							if answer.upper() == "N":
								break
							elif answer.upper() == "Y":
								logging.info("忽略警告.")
								break
							else:
								continue
						if answer.upper() == "N":
							continue
					elif rule["warning_level"] == 5:
						while True:
							text = "[" + time.strftime("%H:%M:%S", time.localtime()) + " WARN] 这条规则会损坏/删除您的重要数据,确定继续吗?[y/N]"
							if "descript" in rule:
								text = "[" + time.strftime("%H:%M:%S", time.localtime()) + " WARN] " + rule["descript"] + "[y/N]"
							answer = input(text)
							if answer.upper() == "N":
								break
							elif answer.upper() == "Y":
								logging.info("忽略警告.")
								break
							else:
								continue
						if answer.upper() == "N":
							continue
					logging.info("正在清理文件...")
					count = 1
					for file in path_list:
						try:
							filesize = getsize(file)
						except:
							filesize = convert_size(0)
						try:
							os.remove(file)
						except PermissionError as e:
							logging.info("\t [" + str(count) + "/" + str(file_count) + "] \t拒绝访问 - " + file)
						except FileNotFoundError as e:
							logging.info("\t [" + str(count) + "/" + str(file_count) + "] \t删除文件 - " + file)
						else:
							logging.info("\t [" + str(count) + "/" + str(file_count) + "] \t删除文件 - " + file)
							clean_size = clean_size + filesize
							clean_count = clean_count + 1
						count = count + 1
				print("")
			print("")
			logging.info("清理完毕!")
			try:
				logging.info("清理了" + str(clean_count) + "个文件(" + convert_size(clean_size) + ").")
				if total_count - clean_count > 0:
					logging.info("有" + str(total_count - clean_count) + "个文件(" + convert_size(total_size - clean_size) + ")未清理.")
			except NameError:
				logging.info("未清理文件.")
	else:
		logging.error("未检测到任何插件!")
		sys.exit()
except BaseException as e:
	logging.error(e.qwq)
	if isinstance(e, KeyboardInterrupt):
		logging.info("")
		logging.error("进程终止!")
except SystemExit as e:
	logging.error("退出程序!")