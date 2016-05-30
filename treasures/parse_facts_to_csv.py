#! /usr/bin/python

import os,sys
import time
import json
import csv

MYHOME='/home/junedm/Sojourner/'
path = '/tmp/facts/'
#path = MYHOME+"facts/GGVA/"
filename = MYHOME+'inventory.csv'
TIME_FORMAT='%Y-%m-%d %H:%M:%S'

#--------------------------------------------------------------------------------
def blank_csv():
        os.rename(filename,filename+".old")
        with open(filename, 'wb') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow(['Server Name','Make','Date of acquisition','Model (if available)','Memory(MB)','HDD','CPU','OS','Role','Software used'])

#--------------------------------------------------------------------------------
def log(host, data):

    if type(data) == dict:
        pass


    print "starting %s" %(host)
    facts = data.get('ansible_facts', None)
    if facts == None:
         print "No Facts for host %s" %host
         return
    #now = time.strftime(TIME_FORMAT, time.localtime())
    Hostname = facts.get('ansible_hostname', None)
    IPV4 = facts.get('ansible_default_ipv4', None).get('address', None)
    Distribution = facts.get('ansible_distribution', None)
    Version = facts.get('ansible_distribution_version', None)
    OS = Distribution+":" + Version
    Arch = facts.get('ansible_architecture', None)
    Kernel = facts.get('ansible_kernel', None)
    Memory = facts.get("ansible_memtotal_mb",None)
    Vendor = facts.get("ansible_system_vendor",None)
    Model = facts.get("ansible_product_name",None)
    Processor = facts.get("ansible_processor",None)[0]
    Cores = facts.get("ansible_processor_vcpus",None)
    CPU = Processor + ":" + str(Cores) + "VCPU"
    #Cores = facts.get("ansible_processor_cores",None)
    if facts.get("ansible_devices",None).get("sda"):
        SDA = facts.get("ansible_devices",None).get("sda",None).get("size",None)
    elif facts.get("ansible_devices",None).get("xvda"):
        SDA = facts.get("ansible_devices",None).get("xvda",None).get("size",None)

    #print Hostname,IPV4,OS,Arch,Kernel,Memory,Processor,Cores,Vendor
    with open(filename, 'a') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow([Hostname,Vendor,'NA',Model,Memory,SDA,CPU,OS,'GALAXY','NA'])

#--------------------------------------------------------------------------------
def all():
        hostlist = os.listdir( path )
        for file in hostlist:
                if os.path.isfile(path+file):
                        json_data = open(path+file)
                        data = json.load(json_data)
                        log(file, data)
                        #os.rename(path+file,path+"done/"+file)

#--------------------------------------------------------------------------------
def single(host):
        FILE=path+host
        json_data = open(FILE)
        data = json.load(json_data)
        log(host, data)
#---------------------------------------------------------------------------------------
def main():
        if len(sys.argv) == 2 and (sys.argv[1] == '--all'):
                blank_csv()
                all()
        elif len(sys.argv) == 3 and (sys.argv[1] == '--host'):
                blank_csv()
                single(sys.argv[2])
#---------------------------------------------------------------------------------------
main()



