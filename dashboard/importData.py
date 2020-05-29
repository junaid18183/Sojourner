import pymongo
from django.core.exceptions import ValidationError
from models import sojourner

class manageDjangoObjects():

	def __init__(self):
		print 'initated'

	def create(self, record):
		document = sojourner.objects.create(
		host_name = record['_id'],
   		asset_id = record['asset_id'],
		network = record['network'],
		crid = record['crid'],
		virt = record['virt'],
		last_update_ansible = record['last_update_ansible'],
		last_update_cmk = record['last_update_cmk'],
	    	ncpu = record['ncpu'],
	    	mem = record['mem'],
	    	model = record['model'],
	    	disk = record['disk'],
	    	os = record['os'],
	    	rack = record['rack'],
	    	os_ver = record['os_ver'],
		role = record['role'],
	    	state = record['state'],
		dc = record['dc'],
		contacts = record['contacts'],
		environment = record['environment'],
		product = record['product'],
		contact_groups = record['contact_groups'],
		)
		try:
			document.save()
		except ValidationError:
			print 'ignore'
