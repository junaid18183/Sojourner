from __future__ import unicode_literals

from django.db import models
from mongoengine import *

class sojourner(Document):
	host_name = StringField(primary_key=True, required=True)
	asset_id = StringField(blank=True)
	network = DictField()
	crid = StringField(blank=True)
	virt = StringField()
	last_update_ansible = StringField() 
	last_update_cmk = StringField()
	ncpu = IntField()
	mem = IntField()
	model = StringField()
	disk = DictField(blank=True)
	os = StringField()
	rack = StringField(blank=True)
	os_ver = StringField()
	role = ListField(StringField())
	state = StringField()
	dc = StringField()
	contacts = StringField()
	environment = StringField()
	product = StringField()
	contact_groups = StringField()
	cost = StringField()
	commission_date = StringField()
	termination_date = StringField()
