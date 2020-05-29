from __future__ import unicode_literals
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from models import sojourner
import importData
import datetime,mongoengine
from .forms import SelectForm
import re, ast
import sys

def search(request):
	if 'q' in request.GET and request.GET['q']:
		q = request.GET['q']
		if re.search(r'\*', q):
			hosts = sojourner.objects.filter(host_name__contains=re.sub('\*', '', q)).order_by('_id')	
			return render(request, 'search_results.html', {'hosts': hosts, 'query': q})
		else:
			hosts = sojourner.objects.filter(host_name=q)
			return render(request, 'search_results.html', {'hosts': hosts, 'query': q, 'displaycontact': 1})
#		return render(request, 'search_results.html', {'hosts': hosts, 'query': q})
#	else:
#		return HttpResponse('Please submit a search term.')
#		client = mongoengine.connect('localhost', 27017)
#		db = client['inventory']
#		collection = db['ansible']
#		myhosts = collection.find_one({'_id': q})
#		hosts = list()
#		hosts = [myhosts]
	else:
		return HttpResponse('Please submit a search term.')

def dumpdata(request):
	q = request.GET
	instance = importData.manageDjangoObjects()
	#client = mongoengine.connect('localhost', 27017)
	#db = client['inventory']
	#collection = db['inventory']
	#myhosts = collection.find()
	for record in list(q.values()):
		myrecord = ast.literal_eval(record)
		if myrecord.has_key('_id'):
			instance.create(myrecord)
	return HttpResponse('Data dumped')

def dashboard(request):

	array = dict()
	colo_count = sojourner.objects.filter(dc='COLO').count()
	ggva_count = sojourner.objects.filter(dc='GGVA').count()
	colo_count_physical = sojourner.objects.filter(dc='COLO', virt='N').count()
	colo_count_virtual = sojourner.objects.filter(dc='COLO', virt='Y').count()
	ggva_count_physical = sojourner.objects.filter(dc='GGVA', virt='N').count()
	ggva_count_virtual =  sojourner.objects.filter(dc='GGVA', virt='Y').count()
	colo_count_down = sojourner.objects.filter(dc='COLO', state='DOWN').count()
	ggva_count_down = sojourner.objects.filter(dc='GGVA', state='DOWN').count()
	total = int(colo_count) + int(ggva_count)
	total_physical = int(colo_count_physical) + int(ggva_count_physical)
	total_virtual = int(colo_count_virtual) + int(ggva_count_virtual)
	total_down = int(colo_count_down) + int(ggva_count_down)

	dc = sojourner.objects.distinct('dc')
	dc.append('ALL')
	product = sojourner.objects.distinct('product')
	product.append('ALL')
	role = sojourner.objects.distinct('role')
	role.append('ALL')
	env = sojourner.objects.distinct('environment')
	env.append('ALL')

	if request.method == 'POST':

		pdata = request.POST.copy()
		if pdata['dc'] in dc and pdata['product'] not in product and pdata['role'] not in role and pdata['env'] not in env:
			#form = SelectForm(request.POST) 
			dc = [pdata['dc']]
			if dc[0] == 'ALL':
				product = sojourner.objects.distinct('product')
			else:
				product = sojourner.objects.filter(dc=dc[0]).distinct('product')
			if len(product) > 1:
				product.append('ALL')
			array = {'a': colo_count, 'b': colo_count_physical, 'c': colo_count_virtual, 'd': colo_count_down, 'e': ggva_count, 'f': ggva_count_physical, 'g': ggva_count_virtual, 'h': ggva_count_down, 'm': total, 'n': total_physical, 'o': total_virtual, 'p': total_down, 'dc': dc, 'product': product, 'dflag': 1}
			return render(request, 'home.html', {'array': array})
	
		if pdata['dc'] in dc and pdata['product'] in product and pdata['role'] not in role and pdata['env'] not in env:
			dc = [pdata['dc']]
			product = [pdata['product']]
	
			if dc[0] == 'ALL' and product[0] == 'ALL':		
				role = sojourner.objects.distinct('role')
			elif dc[0] == 'ALL' and product[0] != 'ALL':
				role = sojourner.objects.filter(product=product[0]).distinct('role')
			elif dc[0] != 'ALL' and product[0] == 'ALL':
				role = sojourner.objects.filter(dc=dc[0]).distinct('role')
			else:
				role = sojourner.objects.filter(dc=dc[0], product=product[0]).distinct('role')
			if len(role) > 1:
				role.append('ALL')
			array = {'a': colo_count, 'b': colo_count_physical, 'c': colo_count_virtual, 'd': colo_count_down, 'e': ggva_count, 'f': ggva_count_physical, 'g': ggva_count_virtual, 'h': ggva_count_down, 'm': total, 'n': total_physical, 'o': total_virtual, 'p': total_down, 'dc': dc, 'product': product, 'role': role, 'dflag':1, 'pflag':1}
			return render(request, 'home.html', {'array': array})
		if pdata['dc'] in dc and pdata['product'] in product and pdata['role'] in role and pdata['env'] not in env:
			dc = [pdata['dc']]
			product = [pdata['product']]
			role = [pdata['role']]	
			if dc[0] == 'ALL' and product[0] == 'ALL' and role[0] == 'ALL':
				env = sojourner.objects.distinct('environment')				
			elif dc[0] != 'ALL' and product[0] == 'ALL' and role[0] == 'ALL':
				env = sojourner.objects.filter(dc=dc[0]).distinct('environment')
			elif dc[0] == 'ALL' and product[0] != 'ALL' and role[0] == 'ALL':
				env = sojourner.objects.filter(product=product[0]).distinct('environment')
			elif dc[0] == 'ALL' and product[0] == 'ALL' and role[0] != 'ALL':
				env = sojourner.objects.filter(role=role[0]).distinct('environment')
			elif dc[0] == 'ALL' and product[0] != 'ALL' and role[0] != 'ALL':
				env = sojourner.objects.filter(product=product[0], role=role[0]).distinct('environment')
			elif dc[0] != 'ALL' and product[0] != 'ALL' and role[0] == 'ALL':
				env = sojourner.objects.filter(dc=dc[0], product=product[0]).distinct('environment')
			elif dc[0] != 'ALL' and product[0] == 'ALL' and role[0] != 'ALL':
				env = sojourner.objects.filter(dc=dc[0], role=role[0]).distinct('environment')
			else:
				env = sojourner.objects.filter(dc=dc[0], product=product[0], role=role[0]).distinct('environment')
			if len(env) > 1:
				env.append('ALL')
			array = {'a': colo_count, 'b': colo_count_physical, 'c': colo_count_virtual, 'd': colo_count_down, 'e': ggva_count, 'f': ggva_count_physical, 'g': ggva_count_virtual, 'h': ggva_count_down, 'm': total, 'n': total_physical, 'o': total_virtual, 'p': total_down, 'dc': dc, 'product': product, 'role': role, 'env': env, 'dflag':1, 'pflag':1, 'rflag':1}
			return render(request, 'home.html', {'array': array})

		#dc = request.POST.get('dc')
	#	product = request.POST.get('product')
	#	role = request.POST.get('role')
	#	env = request.POST.get('env')
	#	hosts = sojourner.objects.filter(dc=dc, product=product, role=role, environment=env)
	#	varx = sojourner.objects.filter(dc=dc).distinct('product')
	#	vary = sojourner.objects.filter(dc=dc, product=product).distinct('role')
	#	varz = sojourner.objects.filter(dc=dc, product=product, role=role).distinct('environment')
		
		#if form.is_valid():
		if pdata['dc'] in dc and pdata['product'] in product and pdata['role'] in role and pdata['env'] in env and not pdata.has_key('go'):
			dc = [pdata['dc']]
			product = [pdata['product']]
			role = [pdata['role']]
			env = [pdata['env']]
			array = {'a': colo_count, 'b': colo_count_physical, 'c': colo_count_virtual, 'd': colo_count_down, 'e': ggva_count, 'f': ggva_count_physical, 'g': ggva_count_virtual, 'h': ggva_count_down, 'm': total, 'n': total_physical, 'o': total_virtual, 'p': total_down, 'dc': dc, 'product': product, 'role': role, 'env': env, 'dflag':1, 'pflag':1, 'rflag':1, 'eflag':1}
			return render(request, 'home.html', {'array': array})

		if pdata['dc'] in dc and pdata['product'] in product and pdata['role'] in role and pdata['env'] in env and pdata.has_key('go'):	
			dc = [pdata['dc']]
			product = [pdata['product']]
			role = [pdata['role']]
			env = [pdata['env']]
			if dc[0] == 'ALL' and product[0] == 'ALL' and role[0] == 'ALL' and env[0] == 'ALL':
				hosts = sojourner.objects.all().order_by('_id')
			elif dc[0] == 'ALL' and product[0] != 'ALL' and role[0] != 'ALL' and env[0] != 'ALL':
				hosts = sojourner.objects.filter(product=product[0], role=role[0], environment=env[0]).order_by('_id')
			elif dc[0] == 'ALL' and product[0] == 'ALL' and role[0] != 'ALL' and env[0] != 'ALL':
				hosts = sojourner.objects.filter(role=role[0], environment=env[0]).order_by('_id')
			elif dc[0] == 'ALL' and product[0] == 'ALL' and role[0] == 'ALL' and env[0] != 'ALL':
				hosts = sojourner.objects.filter(environment=env[0]).order_by('_id')
			elif dc[0] != 'ALL' and product[0] == 'ALL' and role[0] != 'ALL' and env[0] != 'ALL':
				hosts = sojourner.objects.filter(dc=dc[0], role=role[0], environment=env[0]).order_by('_id')
			elif dc[0] != 'ALL' and product[0] == 'ALL' and role[0] == 'ALL' and env[0] != 'ALL':
				hosts = sojourner.objects.filter(dc=dc[0], environment=env[0]).order_by('_id')
			elif dc[0] != 'ALL' and product[0] == 'ALL' and role[0] == 'ALL' and env[0] == 'ALL':
				hosts = sojourner.objects.filter(dc=dc[0]).order_by('_id')
			elif dc[0] == 'ALL' and product[0] != 'ALL' and role[0] == 'ALL' and env[0] == 'ALL':
				hosts = sojourner.objects.filter(product=product[0]).order_by('_id')
			elif dc[0] == 'ALL' and product[0] != 'ALL' and role[0] == 'ALL' and env[0] != 'ALL':
				hosts = sojourner.objects.filter(product=product[0], environment=env[0]).order_by('_id')
			elif dc[0] != 'ALL' and product[0] != 'ALL' and role[0] == 'ALL' and env[0] == 'ALL':
				hosts = sojourner.objects.filter(dc=dc[0], product=product[0]).order_by('_id')
			elif dc[0] != 'ALL' and product[0] != 'ALL' and role[0] != 'ALL' and env[0] == 'ALL':
				hosts = sojourner.objects.filter(dc=dc[0], product=product[0], role=role[0]).order_by('_id')
			elif dc[0] != 'ALL' and product[0] != 'ALL' and role[0] == 'ALL' and env[0] != 'ALL':
				hosts = sojourner.objects.filter(dc=dc[0], product=product[0], environment=env[0]).order_by('_id')
			elif dc[0] == 'ALL' and product[0] == 'ALL' and role[0] != 'ALL' and env[0] == 'ALL':
				hosts = sojourner.objects.filter(role=role[0]).order_by('_id')
			elif dc[0] != 'ALL' and product[0] == 'ALL' and role[0] != 'ALL' and env[0] == 'ALL':
				hosts = sojourner.objects.filter(dc=dc[0], role=role[0]).order_by('_id')
			elif dc[0] == 'ALL' and product[0] != 'ALL' and role[0] != 'ALL' and env[0] == 'ALL':
				hosts = sojourner.objects.filter(product=product[0], role=role[0]).order_by('_id')
			else:
				hosts = sojourner.objects.filter(dc=dc[0], product=product[0], role=role[0], environment=env[0]).order_by('_id')
			
			mysum = 0
			for chost in hosts:
				if chost.cost is not None:
					mycost = float(chost.cost.lstrip('$'))
					mysum = mycost + mysum

			mysum = '$' + str(mysum)
			mypattern = 'DC: ' + dc[0] + ', Product: ' + product[0] + ', Role: ' + role[0] + ', Env: ' + env[0]
			return render(request, 'pattern_search.html', {'hosts': hosts, 'mypattern': mypattern, 'mysum': mysum})
	else:
		array = {'a': colo_count, 'b': colo_count_physical, 'c': colo_count_virtual, 'd': colo_count_down, 'e': ggva_count, 'f': ggva_count_physical, 'g': ggva_count_virtual, 'h': ggva_count_down, 'm': total, 'n': total_physical, 'o': total_virtual, 'p': total_down, 'dc': dc, 'dflag':0, 'pflag':0, 'rflag':0, 'eflag':0}
		return render(request, 'home.html', {'array': array})
	
   
def status(request, dc):
	if dc != 'ALL':
		hosts = sojourner.objects.filter(dc=dc, state='DOWN')
	else:
		hosts = sojourner.objects.filter(state='DOWN')
	return render(request, 'down_search.html', {'hosts': hosts, 'selectdc': dc})

def listing(request):
	dc = request.GET['dc']
	if dc != 'ALL':
		hosts = sojourner.objects.filter(dc=dc)
	else:
		hosts = sojourner.objects.all()
	
	mysum = 0
	for chost in hosts:
		if chost.cost is not None:
			mycost = float(chost.cost.lstrip('$'))
			mysum = mycost + mysum

	mysum = '$' + str(mysum)
		
	return render(request, 'listing.html', {'hosts': hosts, 'selectdc': dc, 'mysum': mysum})

def showvip(request):
	hosts = sojourner.objects.all()
	virtualip = dict()
	for host in hosts:
		if (host.network).has_key('vip'):
			vipvalue = ', '.join(host.network['vip'])
			virtualip[host.host_name] = vipvalue
	return render(request, 'showvip.html', {'virtualip': virtualip})
		
