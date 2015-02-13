#!/bin/bash
#
# Author: Anand Takalkar <anandt@glam.com>
# Date: 06/13/2014
# Description: Script to make sure, server is Ansible ready. (to install required python packages)
#
########################################

function python_install
{
echo -e "\nCleaning yum...\n"
yum clean all

echo -e "\nInstalling python...\n"
yum -y install python; yum list installed python

OUT=$(rpm -qa | grep -w "python-json")
if [ "$OUT" != "" ] ; then
echo -e "\nRemoving python-json...\n"
yum -y remove python-json
fi

echo -e "\nInstalling python-babel, PyYAML, python-crypto, python-jinja2, python-paramiko...\n"
yum -y install python-babel PyYAML python-crypto python-jinja2 python-paramiko

case $OS in
5.*)
echo -e "\nInstalling python-simplejson...\n"
yum -y install python-simplejson
;;
esac
}

function quit
{
echo -e "\nPython installation completed...\n"
exit 0
}

#SSH="ssh -o StrictHostKeyChecking=no $host"
OS=`cat /etc/redhat-release | awk '{print $3}'`
LOG_DIR="/home/prod/logs"
LOG_FILE="${LOG_DIR}/${host}_python_install.log"

echo -e "\n====== `date` ======\n" >> ${LOG_FILE}
python_install | tee -a ${LOG_FILE}
quit
