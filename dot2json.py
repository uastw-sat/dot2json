#!/usr/bin/env python

########################################################################
### dot2json.py
### F. Gerstmayer 2016
### UAS Technikum Wien, Embsys, SAT
########################################################################



""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""" IMPORT	 														 """
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import argparse
import json
import sys
import os
import re



""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""" DEFINES	 														 """
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
### Keywords for elements which shall be ignored by the parser
dot_ignore = 	[
					"graph",
					"node",
					"subgraph",
				]
				
### Keywords for *.dot parsing (trigger)
dot_keywords = 	[
					"bgcolor",
					"height",
					"width",
					"label",
					"pos",
					"shape",
					"style",
					"lp",
				]

### Keywords for *.json output (init)
sigma_keywords = [
					"id",		# x
					"label",	# x
					"Detail",	# x
					"bb",		# x
					"et",		# x
					"st",		# x
					"wet",		# x
					"wst",		# x
					"pos",		# x
					"x",		# x
					"y",		# x
					"color",	# x
					"source",	# x
					"target",	# x
					"type", 	# x
					"width",	# x
					"height",	# x
					"size",		# []
					"suc",		# x
					"pre",		# x
					"line", 	# x
					"done",		# x
					"code",		# x
					"src",		# x
				]

### Map for simplified dot2json conversion
dot_sigma_key_map = {
					"label" 	: "label",
					"bgcolor" 	: "color",
					"pos" 		: "pos",
					"width" 	: "width",
					"height" 	: "height",
					"style" 	: "type",
				}

### Global variables / settings
verbosity 		= 0
gen_json 		= False
path_in_dot 	= ""
path_in_dep 	= ""
path_in_src 	= ""
path_out_html 	= ""
path_out_json 	= ""
src_list = []


### "constant" settings not modifyable by commandline
colBlue 	= { "r" : 50	, "g" : 150	, "b" : 255	} #dodgerblue
colRed  	= { "r" : 255	, "g" : 30	, "b" : 30	}
colGreen 	= { "r" : 60	, "g" : 179	, "b" : 113	}
colYellow	= { "r" : 207	, "g" : 181	, "b" : 59	}

constYMult	= 1 # 1.5
constXMult	= 2 # 5
constYDiff 	= 100
constXMove 	= 100
constRange 	=  20
constOut	= "./out/default.cfg.html"
constDep	= "./dep/"



""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""" IMPORT	 														 """
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
### Get positional information of a Node
def getPosNode(node):
	x = node["x"]
	y = node["y"]
	return x,y

### Set positional information of a node
def setPosNode(node, x, y):
	node["x"] = x
	node["y"] = y

### Calculate absolute difference between two numbers
def calcAbsDiff(numA, numB):
	return max(numA,numB)-min(numA,numB)

### Calculate differnce between two numbers (position dependent)
def calcRelDiff(numA, numB):
	return numA - numB
	
### Rearrange children to align critical path correctly
def sortChilds(nodes, ends):
	result = []
	for i in ends:
		child = nodes[i]
		if child["wet"]== True:
			result.insert(0,i)
		else:
			result.insert(1,i)
	
	return result


def align4(cur, nodes):
	if nodes[cur]["done"] == True:
		return nodes
	
	suc = nodes[cur]["suc"].split(',')	# Get Successors
	pre = nodes[cur]["pre"].split(',')	# Get Predecssors
	bro = ['']
	
	
	if pre:
		print pre
		for i in pre:
			bro = nodes[i]["suc"].split(',')
	
	print "Cur: " + str(cur) + " (" + str(nodes[cur]["bb"]) + ")"
	print "Suc: " + str(suc)
	print "Pre: " + str(pre)
	print "Bro: " + str(bro)
	
	px_cur,py_cur = getPosNode(nodes[cur])
	
	# Orientate on Predecessors
	# Which one is closer in X, ignore Y
	
	px_pre = []
	py_pre = []
	
	if len(pre) > 1:
		for i in pre:
			pritn("Hello")
			px_pre[i],py_pre[i] = getPosNode(nodes[i])
			
			dx_pre[i] 			= calcAbsDiff(px_cur,px_pre[i])  
	
	if len(suc) > 1:
		print suc
		for i in suc:
			print i
			nodes = align(i,nodes)
			
	return nodes
	
def align3(parent, nodes):
	nodes[parent]["done"] = True
	
	for me in nodes[parent]["suc"].split(','):
		if not me or nodes[me]["done"] == True:
			continue
		
		others = nodes[parent]["suc"].split(',')
		
		xpos1,ypos1 = getPosNode(nodes[parent])
		xpos2,ypos2 = getPosNode(nodes[me])
		
		diff_rel_x = calcRelDiff(xpos1,xpos2)
		diff_rel_y = calcRelDiff(ypos1,ypos2)
		
		#print (("Name:  " + str(nodes[parent]["bb"])))
		#print (("pre_X: " + str(nodes[parent]["x"])))
		#print (("pre_Y: " + str(nodes[parent]["y"]) +"\n"))
		#print (("Name:  " + str(nodes[me]["bb"])))
		#print (("suc_X: " + str(nodes[me]["x"])))
		#print (("suc_Y: " + str(nodes[me]["y"])))
		print (("\n"+ str(nodes[parent]["bb"]) + " --> " +str(nodes[me]["bb"])))
		print (("Old:"))
		print str(diff_rel_x)
		print str(diff_rel_y)
		
		x_move = 0
		
		if diff_rel_x > 0 and diff_rel_x < constXMove:
			x_move = xpos1 - diff_rel_x
			xpos2 -= x_move
		elif diff_rel_x < 0 and diff_rel_x < -constXMove:
			x_move = xpos1 + diff_rel_x
			xpos2 -= x_move
		#elif diff_rel_x < -constXMove:
		#	x_move = posx1 + diff_rel_x
		#	xpos2 -= x_move
		#elif diff_rel_x > constXMove:
			
		
		move_y = constYDiff - diff_rel_y
		ypos2 -= move_y
		
		
		setPosNode(nodes[me],xpos2, ypos2)
		
		
		xpos1,ypos1 = getPosNode(nodes[parent])
		xpos2,ypos2 = getPosNode(nodes[me])
		
		diff_rel_x = calcRelDiff(xpos1,xpos2)
		diff_rel_y = calcRelDiff(ypos1,ypos2)
		
		print (("\nNew:"))
		print str(diff_rel_x)
		print str(diff_rel_y)
		
		for oth in others:
			if oth <> me:
				xpos3,ypos3 = getPosNode(nodes[oth])
				setPosNode(nodes[oth],xpos3-x_move,ypos3 - move_y)
				
		nodes = align(me, nodes);
		
	return nodes



### Recursive Function for forward aligment(x/y) of nodes
def align(start, ends, nodes, yoff):
	
	#print (("" + nodes[start]["width"]  + "\n"))
	# Set actual node to done to prevent infinite recursion
	nodes[start]["done"] = True
	ends = sortChilds(nodes,ends)
	for i in ends:
		
		# Get positional information for start and target node
		xpos1,ypos1 = getPosNode(nodes[start])
		xpos2,ypos2 = getPosNode(nodes[i])
		
		# Max diff relevant as adjustment is only done if diff greater than a certain value
		diff_abs_x = calcAbsDiff(xpos1,xpos2)  
		
		# Rel diff relevant as it defines whether the graph is stretched or compressed
		diff_rel_y = calcRelDiff(ypos1,ypos2)

		#print (("\nOld:"))
		#print (("\t" + start + "\t(" 	+ '% 6d' % xpos1 + "," 	+ '% 6d' % ypos1 			+ ")"))
		#print (("\t" + i + "\t(" 		+ '% 6d' % xpos2 + "," 	+ '% 6d' % ypos2 			+ ")"))
		#print (("\tDiff:\t(" 			+ '% 6d' % diff_abs_x 	+ "," + '% 6d' % diff_rel_y + ")"))
		#print (("Name:  " + str(nodes[start]["bb"])))
		#print (("pre_X: " + str(nodes[start]["x"])))
		#print (("pre_Y: " + str(nodes[start]["y"])))
		#print (("pre_H: " + str(nodes[start]["height"])))
		#print (("pre_W: " + str(nodes[start]["width"] +"\n")))
		#print (("Name:  " + str(nodes[i]["bb"])))
		#print (("suc_X: " + str(nodes[i]["x"])))
		#print (("suc_Y: " + str(nodes[i]["y"])))
		#print (("suc_H: " + str(nodes[i]["height"])))
		#print (("suc_W: " + str(nodes[i]["width"])))
		#print ("\n")
		#print ("\n")
		# Adapt x position if diff between nodes to short
		if diff_abs_x < constXMove:
			xpos2 = xpos1

		# Apply general offset and recalc
		ypos2 -= yoff
		diff_rel_y = calcRelDiff(ypos1,ypos2)

	


		if diff_rel_y > constYDiff:
			num1 = 0
			num2 = 0
			if nodes[i]["pre"] != "":
				num1 = len(nodes[i]["pre"].split(","))
			if nodes[i]["suc"] != "":
				num2 = len(nodes[i]["suc"].split(","))
			
			if len(ends) <= 2 and num1 <=2 and num2 <= 2:
				yoff -= diff_rel_y
				diff_rel_y = 0
			
		
		if diff_rel_y < constYDiff:
			ypos2 = ypos1 - constYDiff 		# Set Diff to 500 if diff < 500
			yoff += constYDiff - diff_rel_y	# How far has the graph moved due to stretching
		
		
		
		diff_rel_y = calcRelDiff(ypos1,ypos2)
		#print (("New:"))
		#print (("\t" + start + "\t(" 	+ '% 6d' % xpos1 + "," 	+ '% 6d' % ypos1 			+ ")"))
		#print (("\t" + i + "\t(" 		+ '% 6d' % xpos2 + "," 	+ '% 6d' % ypos2 			+ ")"))
		#print (("\tDiff:\t(" 			+ '% 6d' % diff_abs_x 	+ "," + '% 6d' % diff_rel_y + ")"))
		#print ( "\n-------------------------------"
		
		
		if nodes[i]["done"] == True:
			continue
		
		setPosNode(nodes[i],xpos2,ypos2)
		
		tempA = i
		if nodes[tempA]["suc"] != "":
			tempB = nodes[tempA]["suc"].split(",")
			nodes=align(tempA, tempB, nodes,yoff)
		
		
	return nodes
	
	
	
	
def dot2json(path_in_dot):
	nodes = {}
	edges = {}
	
	# Open & Load Input Dot File 
	p_inp = open(path_in_dot,"r")
	content = p_inp.read()
	
	# Parse Dot-File
	data = content.split("];")
	
	# Ignore first and last Element (General Graph Information & "}")
	for comp in data[1:-1]:
		# Strip leadign and trailing whitespaces and linefeeds
		comp = comp.strip()
		
		# In case the first character is a '}', remove and strip again
		if comp[0:1]=="}":
			comp = comp[1:]
			comp = comp.strip()
			
		ret = False
		for x in dot_ignore:
			ret |= comp.startswith(x) 
		if ret:
			continue
			
		# Find Start of Node/Edge
		ret = comp.find("[")
		if ret == -1:
			print ( "Oho! Node passt nicht: \n" + comp + "\n exiting...!")
			continue
		
		# Get Name (ID) of Node/Edge & Strip Info
		name = comp[:ret].strip()
		comp = comp[ret +1:]
		
		
		#Declare & Initialize Dictionary for Data
		nodedata = {}
		for i in sigma_keywords:
			nodedata[i] = ""
			
		# Traverse through elements
		for bef in comp.split(",\n"):
			
			# Find Separator
			ret = bef.find("=")
			if ret == -1:
				print ( "Oho! Component passt nicht: \n" + bef + "\n exiting...!")
				continue
			
			# Get Source & Target Information
			src = bef[:ret].strip()
			tar = bef[ret+1:].strip()
			
			# Strip Target of unnecessary characters
			if tar[0] == "\"":
				tar = tar[1:-1]
			if tar[0] == "{":
				tar = tar[1:-1]
				
			# Replace Dot characters with control sequences
			tar = tar.replace("\\\n","")
			tar = tar.replace("\n","")
			tar = tar.replace("\\l","\n")
			tar = tar.replace("\\","")
			tar = tar.strip()
			
			#print(src)
			#print(tar)
			
			if src in dot_keywords:
				if src in dot_sigma_key_map.keys():
					nodedata[dot_sigma_key_map[src]] = tar
				#else:
					#print ( "Omitting: " + src + "=" + tar)
			
		# Nodedata contains main Information from Dot
		# Process data for json (sigma) required information
		
		# Differ Edge & Node
		ret = name.find("->")
		
		# Edge
		if ret != -1: 	
			nodedata["source"]=name[:ret].strip()
			nodedata["target"]=name[ret+2:].strip()
			
			# Add Egde to Edge-Dictionary
			edges[name] = nodedata
		
		# Node
		else: 			
			nodedata["id"] = name
			ret = nodedata["pos"].find(",")
			if ret > -1:
				nodedata["x"] = float(nodedata["pos"][:ret]) 	* constXMult
				nodedata["y"] = float(nodedata["pos"][ret+1:]) 	* constYMult
			else:
				nodedata["x"] = 0
				nodedata["y"] = 0
			
			nodedata["wet"] = False
			nodedata["wst"] = False
			nodedata["done"] = False
			
			temp = nodedata["label"]
			
			
			# Find first end of header |
			ret  = temp.find("|")
			
			# If none found, set to end of string
			if ret == -1:
				ret = len(temp)
			
			head = temp[:ret]
			body = temp[ret+1:]
			
			ret  = head.find("\n")
			if ret == -1:
				nodedata["bb"] = head
			else:
				prev = 0
				cnt  = 0
				
				head += "\n"
				for ret in re.finditer("\n",head):
					lab = head[prev:ret.start()]
					
					prev = ret.end()
					cnt += 1
					if cnt == 1:
						nodedata["bb"] = lab
					elif cnt == 2:
						nodedata["et"] = lab[4:]
						if lab[-1:] == " ":
							nodedata["wet"] = True
					elif cnt == 3:
						nodedata["st"] = lab[4:]
						if lab[-1:] == " ":
							nodedata["wst"] = True
					elif cnt == 4:
						nodedata["code"] = lab
						retColon1 = lab.find(":")
						retColon2 = lab.rfind(":")
						if retColon1 != -1 and retColon2 != -1:
							src_path = lab[:retColon1]
							src_func = lab[retColon1+1:retColon2]
							src_line = lab[retColon2+1:].split(',')
							src_line = [int(x) for x in src_line]
							matching = [s for s in src_list if src_path in s]
							if len(matching) == 1:
								f_temp 	= open(matching[0],"r")
								lines	= f_temp.readlines()
								for num in range(min(src_line),max(src_line)+1):
									temp = lines[num-1]
									retComment = temp.find('//')
									if retComment != -1:
										temp = temp[:retComment] + "\n"
									retComment = temp.find('/*')
									if retComment != -1:
										temp = temp[:retComment] + "\n"
									
									nodedata["src"] += str(num) + ":" + temp
								
								nodedata["src"] = nodedata["src"].replace('"','\\"')
								nodedata["src"] = nodedata["src"].replace("&","&gt;")
								nodedata["src"] = nodedata["src"].replace("<","&lt;")
								nodedata["src"] = nodedata["src"].replace(">","&gt;")
								nodedata["src"] = nodedata["src"].replace("\t","&emsp;")
								nodedata["src"] = nodedata["src"].replace("\n","<br>")
								nodedata["src"] = nodedata["src"].replace("\r","")
								nodedata["src"] = "<small>" + nodedata["src"] + "</small>"
								nodedata["code"] = "<a href=\\\"" + os.path.relpath(matching[0],os.path.dirname(path_out_html)) + "\\\">"+ src_path + str(src_line) +"</a><br>"
								#print (nodedata["src"])
							elif len(matching) == 0:
								pass
							else:
								print ("More than one match:" + matching)
					#else:
					#	print ( "More information in header than parsed")
				
				temp = ""
				prev = 0
				for rep in re.finditer(r"0x[0-9a-z]*:", body):
					temp += body[prev:rep.start()] + "<i>" + body[rep.start():rep.end()] + "</i>"
					prev = rep.end()
				
				if temp == "":
					temp = body
				else:
					temp += body[prev:]
				
				temp = temp.replace("\n", "<br>")
				nodedata["Detail"] = temp
			#else:
			#	nodedata["bb"] = nodedata["label"] 
				
			if nodedata["wet"] and nodedata["wst"]:
				nodedata["color"] = colRed
			elif nodedata["wet"]:
				nodedata["color"] = colYellow
			elif nodedata["wst"]:
				nodedata["color"] = colBlue
			else:
				nodedata["color"] = colGreen
			# Add Node to Node-Dictionary
			nodes[name] = nodedata
			
			
	# Add Dependencies (Edges) to Nodes
	for i in edges:
		src = edges[i]["source"]
		tar = edges[i]["target"]
		
		if nodes[src]["suc"] != "":
			nodes[src]["suc"] += ","
		nodes[src]["suc"] += tar
		
		if nodes[tar]["pre"]  != "":
			nodes[tar]["pre"]  += ","
		nodes[tar]["pre"] += src
		
	# Align Nodes starting with Node labeled "ENTRY" (unique)
	for i in nodes:
		#print (nodes[i]["bb"])
		if nodes[i]["bb"] == "ENTRY":
			start  = i
			ends = nodes[i]["suc"].split(",")
			nodes = align(start, ends, nodes,0) # recursive!
			break
	
	# Set edge type, depending on number of successors, ...
	for i in edges:
		linetype = "arrow"
		
		src_suc = []
		src_pre = []
		tar_suc = []
		tar_pre = []
		
		src = nodes[edges[i]["source"]]
		tar = nodes[edges[i]["target"]]
		src_id = src["id"]
		tar_id = tar["id"]
		
		src_suc = src["suc"].split(",") if src["suc"] != "" else ""
		src_pre = src["pre"].split(",") if src["pre"] != "" else ""
		tar_suc = tar["suc"].split(",") if tar["suc"] != "" else ""
		tar_pre = tar["pre"].split(",") if tar["pre"] != "" else ""
		
		xpos1,ypos1 = getPosNode(src)
		xpos2,ypos2 = getPosNode(tar)
		diffx = calcAbsDiff(xpos1,xpos2)
		diffy = calcAbsDiff(ypos1,ypos2)
		
		# Case Back & Forth
		if src_id in tar_suc and src_id in tar_pre:
			linetype = "curvedArrow"
		
		# Case Distance too wide
		if linetype == "arrow" and (diffx > (constXMove + constRange) or diffy > (constYDiff+ constRange)):
			linetype = "curvedArrow"
				
		edges[i]["line"] = linetype
		


	# Write Data
	dat_json = "{"
	
	# Edges
	dat_json += "\"edges\":[\n\t"
	b = 0
	for i in edges:
		if b != 0:
			dat_json += ","
		
		b += 1
		dat_json += "{"
		dat_json += "\t\"id\":\"" 		+ str(b) 				+ "\",\n"
		dat_json += "\t\t\"source\":\"" 	+ edges[i]["source"] 	+ "\",\n" 
		dat_json += "\t\t\"target\":\"" 	+ edges[i]["target"] 	+ "\",\n"
		dat_json += "\t\t\"type\":\"" 		+ edges[i]["line"] 		+ "\",\n"
		dat_json += "\t\t\"color\":"		+ "\"rgb(1,1,1)\",\n"
		dat_json += "\t\t\"label\":\"" 		+ edges[i]["label"] 	+ "\",\n"
		dat_json += "\t\t\"style\":\""		+ edges[i]["type"] + "\"\n"
		dat_json += "\t}"
		
		#dat_json += "\t\t\"weight\":\""
		#if nodes[edges[i]["source"]]["bb"] == "ENTRY":
		#	dat_json += "0.99"
		#elif nodes[edges[i]["target"]]["bb"] == "EXIT":
		#	dat_json += "2"
		#else:
		#	dat_json += "1"
		#dat_json += "\",\n"
		#dat_json += "\"size\":10,"

		
		#if edges[i]["type"] != "":
			#dat_json += "\"" + edges[i]["type"] + "\"],"
		
		#dat_json += "\n"
		
	dat_json += "],\n"
	
	#Nodes
	dat_json += "\"nodes\":[\n\t"
	b = 0
	for i in nodes:
		node = nodes[i]
		
		# Omit empty nodes
		if node["suc"] == "" and node["pre"] == "":
			continue
			
		if b != 0: 	# Add ',' if not the first element
			dat_json += ","
		
		b += 1 		# Increment Count
	
		dat_json += "{"
		dat_json += "\t\"id\":\"" 		+ i 						+ "\",\n" 
		dat_json += "\t\t\"label\":\"" 		+ node["bb"] 				+ "\",\n"
		dat_json += "\t\t\"size\":" 		+ str(10)					+ ",\n"
		dat_json += "\t\t\"ET\":\"" 		+ node["et"] 			+ "\",\n"
		dat_json += "\t\t\"ST\":\"" 		+ node["st"] 			+ "\",\n"
		dat_json += "\t\t\"WET\":\"" 		+ str(node["wet"]) 		+ "\",\n"
		dat_json += "\t\t\"WST\":\"" 		+ str(node["wst"]) 		+ "\",\n"
		dat_json += "\t\t\"Detail\":\"" 	+ node["Detail"] 		+ "\",\n"
		dat_json += "\t\t\"Code\":\"" 		+ node["code"] 			+ "\",\n"
		dat_json += "\t\t\"Src\":\"" 		+ node["src"] 			+ "\",\n"
		dat_json += "\t\t\"x\":" 			+ str(0 - node["x"]) 	+ ",\n"
		dat_json += "\t\t\"y\":" 			+ str(0 - node["y"]) 	+ ",\n"
		dat_json += "\t\t\"color\": \"rgb("	+ str(node["color"]["r"]) + "," \
											+ str(node["color"]["g"]) + "," \
											+ str(node["color"]["b"]) + ")\"\n"
		dat_json += "\t}"
	
	dat_json += "]}"
	
	return dat_json



# Write json to external file
def json2file(path_out_json, dat_json):
	p_out_json = path_out_json
	p_out = open(p_out_json,"w")
	p_out.write(dat_json)
	p_out.close()



# Convert json to internal representation
def json2int(dat_json):
	if sys.version_info >= (3,0,0):
		types = (str)
	else:
		types = (str,unicode)
		
	# Read in json data & use moduel to convert
	data = json.loads(dat_json)
	
	# Write required code structure
	code  = "\tvar g = {\n"
	code += "\t\tnodes: [],\n"
	code += "\t\tedges: []\n\t};\n\n"
	
	# Iterate through all nodes
	for node in data["nodes"]:
		code += "\tg.nodes.push({\n"
		
		for i in node:
			#print ( i + "=" + str(node[i])))
			code += "\t\t"+ i + ":"
			
			if isinstance(node[i], types):
				node[i] = node[i].replace("\"","\\\"")
				code += "\""+ node[i] + "\""
			else:
				code += str(node[i])
			code += ",\n"
		code = code[:-2]
		code += "\n"
		code += "\t});\n\n"
	
	for edge in data["edges"]:
		code += "\tg.edges.push({\n"
		for i in edge:
			code += "\t\t"+ i + ":"
			if isinstance(edge[i], types):
				code += "\""+ edge[i] + "\""
			else:
				code += str(edge[i])
			code += ",\n"
		code = code[:-2]
		code += "\n"
		code += "\t});\n\n"
	
	
	return code





### Create HTML output
def createHTML(path_in_dep, path_out_html, extORint, pathORdata,relORabs):
	# Get template file
	p_tmp_html = path_in_dep + "/template.html"
	p_out_html = path_out_html

	# Open files
	f_tmp = open(p_tmp_html,"r")
	p_out = open(p_out_html,"w")
	
	# Read in template files
	content = f_tmp.read()

	
	# Set path of import js files
	if relORabs:
		content = content.replace("xXdepXx", path_in_dep)
	else:
		content = content.replace("xXdepXx", os.path.relpath(path_in_dep,os.path.dirname(path_out_html)) + "/")
	
	
	if extORint: #external json file
		content = content.replace("xXtemplateXx", os.path.relpath(pathORdata,os.path.dirname(path_out_html)))
		content = content.replace("//xXgraphXx", "")
		content = content.replace("//xXjsonXx", "")
	else:		 #internal json representation
		
		# Convert json data to internal representation
		code=json2int(pathORdata)
		content = content.replace("//xXjsonXx", code)
		content = content.replace("//xXgraphXx", "graph: g,")
		content = content.replace("'xXtemplateXx'", 'g')
	
	# Write to HTML file
	p_out.write(content)
	
	f_tmp.close()
	p_out.close()



### print ( Welcome Message
def welcome():
	print ( "\
########################################################################\n\
### dot2json.py\n\
### F. Gerstmayer 2016\n\
### UAS Technikum Wien, Embsys, SAT\n\
########################################################################\n")
	sys.stdout.flush()


### Check whether the input file is of valid file extension
def file_choices(choices,fname):
	ext = os.path.splitext(fname)[1][1:]
	
	if fname == "":
		return fname
		
	if ext not in choices or ext == "":
		parser.error("file doesn't end with {}".format(choices))
	return fname


### Parsing and verifying commandline parametres, conversion and export
if __name__ == "__main__":
	
	# print ( welcome message
	welcome()
	
	# Add commandline arguments to parser with default location, parametres, functions,...
	parser = argparse.ArgumentParser()
	parser.add_argument( "-i", "--input", 	dest = "inp", 	required=True, 						help="Specify input file", type=lambda s:file_choices(("dot"),s))
	parser.add_argument( "-o", "--output", 	dest = "out", 	default=constOut, 					help="Specify output file",  type=lambda s:file_choices(("cfg.html,html"),s))
	parser.add_argument( "-j", "--json", 	dest = "json", 	default="", 						help="Create json-file (specify path)",type=lambda s:file_choices(("json"),s))
	parser.add_argument( "-d", "--depend", 	dest = "dep", 	default="./dep/", 					help="Specify path to dependency files")
	parser.add_argument( "-s", "--source", 	dest = "src", 	default="", 		nargs = '*', 	help="Specify (multiple) path(s) to source file directory")
	parser.add_argument( "-v", "--verbose", dest = "ver", 	default=0, 			action="count", help="Increase output verbosity")
	parser.add_argument( "-c", "--cloud", 	dest = "clo", 	action='store_true',				help="Copy dependencies to output")
	args = parser.parse_args()
	
	# Store parametres in variables
	verbosity 		= args.ver
	gen_json 		= False if args.json == "" else True
	path_in_dot 	= os.path.abspath(args.inp)
	path_in_dep 	= os.path.abspath(os.path.dirname(args.dep)) + "/"
	path_in_src 	= [os.path.abspath(os.path.dirname(x)) + "/" for x in args.src]
	path_out_html 	= os.path.abspath(args.out)
	path_out_json 	= os.path.abspath(args.json) if gen_json == True else ""
	
	relORabs = False
	if args.dep != constDep:
		relORabs = True

		
	
	# Check if dot input file exists
	if not os.path.exists(path_in_dot):
		parser.error("file \""+ args.inp + "\" could not be found")
	# Input-File exists and has correct format
	
	
	
	# If no output file was specified, add name of source and complete path
	if path_out_html == os.path.abspath(constOut):
		ret_dot  = path_in_dot.find(".dot")
		ret_slh  = path_in_dot.rfind("/")
		ret_slh2 = path_out_html.rfind("/")
		if ret_slh != -1 and ret_dot != -1 and ret_slh2 != -1:
			path_out_html = path_out_html[:ret_slh2]
			path_out_html += "/" + path_in_dot[ret_slh+1:ret_dot] + ".cfg.html"
	
	# Check if output dir exists, create if need be
	ret = path_out_html.rfind("/")
	if ret != -1:
		if not os.path.exists(path_out_html[:ret]):
			os.makedirs(path_out_html[:ret])
	# Path to Output-File exists
	
	
	
	# Check if path_out_json dir exists
	ret = path_out_json.rfind("/")
	if ret != -1:
		if not os.path.exists(path_out_json[:ret]):
			os.makedirs(path_out_json[:ret])
	# Path to Json-File exists and filename is correct (previous check)
	
	
	
	# Check if directories exist (dependency and source)
	for x in path_in_src + path_in_dep.split():
		if not os.path.exists(x):
			parser.error("file \""+ x + "\" could not be found")
	# Check if all path's to directories exist
	
	if args.clo:
		os.system("cp -r " + path_in_dep +  " " + os.path.dirname(path_out_html) + "/dep/" )
		path_in_dep = os.path.dirname(path_out_html)+ "/dep/"
		relORabs = False
		
	src_list = []
	for x in path_in_src:
		for files in os.listdir(x):
			if files.endswith(".c") or files.endswith(".h"):
				src_list.append(os.path.relpath(x + files))
	
	# print ( information depending on verbosity level
	print ("Input-File:     " + os.path.relpath(path_in_dot))
	print ("Verbosity:      " + str(verbosity))
	print ("Dependency-Dir: " + (path_in_dep if relORabs else os.path.relpath(path_in_dep)))
	print ("Html-Output:    " + os.path.relpath(path_out_html))
	if gen_json == True:
		print ("Json-Output:    " + os.path.relpath(path_out_json))
	if len(path_in_src) != 0:
		print ("Source-Dirs:    " + str([os.path.relpath(x)+ "/" for x in path_in_src]))
	
	
	# Main-Functionality
	# Conversion of *.dot to *.json (internal)
	dat_json= dot2json(path_in_dot)
	
	# Create json file if requested and set path
	if gen_json == True:
		json2file(path_out_json, dat_json)
		dat_json = path_out_json
	
	# Create HTML export using template
	createHTML(path_in_dep, path_out_html, gen_json, dat_json, relORabs)
