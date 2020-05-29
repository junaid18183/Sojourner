#!/usr/local/bin/python

# This program gets data from check_mk server using LQL query and dump the data in database
#Author: huzefah@glam.com

import argparse,collections,re,string
import sojournerdb
from tabulate import tabulate
from prettytable import PrettyTable
#from prettytable import MSWORD_FRIENDLY

opdict = collections.defaultdict(dict)


def get_args():
		parser = argparse.ArgumentParser("Inventory Parser")
		#parser.add_argument('--dump', nargs=1,help='Dump the data in mongo')
		#parser.add_argument("--list", nargs=1,choices=["role", "product"],help = 'List unique roles, products')
		#parser.add_argument("--list",help = 'List unique roles, products')

		subparser = parser.add_subparsers(title="subcommands",
                                help="additional help")
		parser_show = subparser.add_parser('show', help="show --help")
		parser_show.set_defaults(which='show')
		parser_show.add_argument('--host',required=False,default="all", help="List all the hosts")
		parser_show.add_argument('--dc', choices=["COLO","GGVA"], required=False, help="List host on basis of DC")
		parser_show.add_argument('--product', required=False, help="List host on basis of Product")
		parser_show.add_argument('--environment', required=False, help="List host on basis of Environment")
		parser_show.add_argument('--role', required=False, help="List host on basis of Role")
		parser_show.add_argument('--state', required=False, help="List host on basis of State")
		parser_show.add_argument('--column', nargs='*', required=False, help="Enter which column you want to see")
		#parser_show.add_argument('--list', nargs=1, required=False, help="Enter which column you want to see")
		
		
		parser_list = subparser.add_parser('list', help="show --help")
		parser_list.set_defaults(which='list')
		parser_list.add_argument("--print", choices=["role","product","environment","dc","column"], help="Print based on user selection")
		#parser_list.add_argument("role", help="List all the unique roles")
		#parser_list.add_argument('environment',required=True, help="List all the environments")
	
		parser_list = subparser.add_parser('dump', help="dump --help")
		parser_list.set_defaults(which='dump')
		parser_list.add_argument("--tool", choices=["cmk","ansible","all"], default="all", help="Dump data to mongodb")
		#parser_list.add_argument("--ansible", help="Dump data from check_mk")
			

	
		parser_add = subparser.add_parser('assign', help="add --help")
		parser_add.add_argument('--host', required=True, help="Add new host")

		parser_reap = subparser.add_parser('reap', help="reap --help")
		parser_reap.add_argument('--reap', required=True, help="Delete the host")

		args = vars(parser.parse_args())
		if args['which'] == 'show':
			parse_args(args)
	
		if args['which'] == 'list':
			list_data(args)
		
		if args['which'] == 'dump':
			print "dumpargs=",args
			dumpdata()


def dumpdata():
	sojournerdb.dumpall()


def list_data(args):
	value = ""
	for key in args:
		if key == "print":
			arg = args[key]
			op = sojournerdb.get_uniquevaluesdb(arg)
			for key in op:
				value += key +"\n"

	x = PrettyTable([arg.upper()])	
	x.add_row([value])
	print x
	#print op


def parse_args(args):
	#print "args=",args	
	extraargs = ""
	extraargvalue = ""
	userargs={}
	finalargs={}
	#Get the list of arguments which are not None, i.e what arguments user has passed
	for key in args:
		if key == "column":
			column = args[key]
		#print key,args[key] 
		if args[key] is not None:
			userargs[key] = args[key]
	#print "userargs=",userargs
	#Get the final arguments except host and which 
	for key in userargs:
		if key != "host" and key != "which" and key != "column":
			finalargs[key] = userargs[key]


	extraargs0 = ""
	extraargs1 = ""
	extraargvalue0 = ""
	extraargvalue1 = ""
	extraargs = []
	extraargvalue = []
	if finalargs:
		length = len(finalargs)
		get_host_details(args['host'],column,finalargs)	
		#if length > 3:
		#	print "You can only provide 3 optional args"
		#	exit()
		#if length == 2:	
		#	for key in finalargs:
		#		extraargs.append(key)
		#		extraargvalue.append(finalargs[key])
		#	get_host_details(args['host'],extraargs[0], extraargvalue[0],extraargs[1], extraargvalue[1],column,finalargs)	
		#elif length == 1:
		#	for key in finalargs:
		#		extraargs.append(key)
		#		extraargvalue.append(finalargs[key])
		#	get_host_details(args['host'],extraargs[0], extraargvalue[0],extraargs1, extraargvalue1,column)	
		#else:
		#	get_host_details(args['host'],extraargs0, extraargvalue0,extraargs1, extraargvalue1,column,finalargs)
	else:
		get_host_details(args['host'],column,finalargs)	
	
	#get_host_details(args['host'],extraargs, extraargvalue)


def get_host_details(host,column,finalargs):
	#op = sojournerdb_v5.parse_userquery(host,extraargs,extraargvalue)
	op,count = sojournerdb.parse_userquery(host,finalargs)
	#print op
	#print tabulate(op, headers="keys")
	#tempdict = collections.defaultdict(dict)
	#print "column=",column
	header = ""
	field_name = ["Host_Name", "State","Environment", "Product", "Role", "DC","CRID","ASSET_ID","RACK"]
	if column:
		for i in column:
			#header += '"Host_Name", "State","Environment", "Product", "Role", "DC","CRID","ASSET_ID","RACK"' + i
			field_name.append(i)	
		x = PrettyTable(field_name)
		#print x	
	else:
		x = PrettyTable(["Host_Name", "State","Environment", "Product", "Role", "DC","CRID","ASSET_ID","RACK"])
	#print op
	if host != "all":
		if op:
			#y=create_table(op,x)	
			y=create_table(op,x,field_name,column)	
			print y
			print "Total host found=%s\n" %count 
		else:
			print "%s not found in inventory" %host
	elif host == "all":
		if op:
			for value in op:
			#print "value=",value
				y=create_table(value,x,field_name,column)
				#print "y=",y
			if y:
				print y
				print "Total host found=%s\n" %count
			else:
				print "No host found for your query\n"
			#print "Total host found=%s\n" %count
		else:
			print "No Document found for your query\n" 
	else:
		print "Wrong hostname"

def create_table(op,x):
	crid = ""
	asset_id = ""
	rack = ""
	print "op=",op
	values = []
	for key in op:
		if key == "_id":
			host_name = op[key]
		if key == "product":
			product = op[key]
		if key == "role":
			role = ""
			for r in op[key]:
				role += r +"\n"
		if "crid" in key:
			if key == "crid":
				crid = op[key]
			#if crid == "":
			#	crid = ""
			else:
				crid = '' 
		if "asset_id" in key:
			if key == "asset_id":	
				asset_id = op[key]
			else:
				asset_id = ""
		if key == "state":
			state = op[key]
		if key == "environment":
			environment = op[key]
		if key == "dc":
			dc = op[key]
		if "rack" in key:
			if key == "rack":	
				rack = op[key]
			else:
				rack = ""

	x.add_row([host_name,state, environment,product, role,dc, crid,asset_id, rack])
	#x.add_row(values)
	x.padding_width = 0
	#x.add_row([host_name,state, environment,product, role,dc,crid])
	return x

def create_table(op,x,field_name,column):
	values = []
	mac = "" 
	macip = "" 
	temp = False
	ipv4 = ""
	role = ""
	disk = []
	for field in field_name:
		if field == "Host_Name":
			field = "_id"
		if field ==  "ip":
			field = "network"
			test = "ip"
		if field == "mac":
			field = "network"
			test = "mac"
		if field.lower() in op:
			for key in op:
				if re.search(r'^' + re.escape(field.lower()) + '$',key):
					#values.append(op[key])
					if key == "network" and test == "ip" and not temp:
						temp  = True	
						for eth in op[key]:
							#Cheking for VIP	
							if re.search(r'((vip))', eth):
								for value in op[key]["vip"]:
									ipv4 += value
							if re.search(r'((eth\d)(([.]\d+)?)$)', eth) or re.search(r'((bond\d)(([.]\d+)?)$)',eth):
								ipv4 += op[key][eth]["ipv4"] +"\n"
						values.append(ipv4)
					elif key == "network" and test == "mac":
						for eth in op[key]:
							if re.search(r'((eth\d)(([.]\d+)?)$)', eth):
								mac += op[key][eth]["mac"] +"\n" 
								#mac.append(temp)
						values.append(mac)
					elif key == "role":
						for r in op[key]:
							role += r +"\n"
						values.append(role)
					elif key == "disk":
						for disk in op[key]:
							if disk == "raw":
								for raw in op[key]["raw"]:
									if re.search(r'((sd*))', raw):
										temp = raw +":" + op[key]["raw"][raw] +"\n"
									#	print "temp=",temp			
									#	disk.append(temp)
						values.append(temp)	
					else:
						values.append(op[key])
		else:
			values.append("")
	x.add_row(values)
	x.padding_width = 0
	#x.set_style(MSWORD_FRIENDLY)
	return x

get_args()
