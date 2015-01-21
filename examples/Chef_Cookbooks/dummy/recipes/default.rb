#
# Cookbook Name:: dummy
# Recipe:: default
#
# Copyright 2014, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#
template "/var/tmp/dummy.conf" do 
    source "dummy.erb" 
    variables( :myname => "Juned Memon" )
end
