from django.conf.urls import url

from . import views

urlpatterns = [
  url(r'^$', views.dashboard, name='dashboard'),
	url(r'^search/$', views.search, name='search'),
	url(r'^dumpdata/$', views.dumpdata, name='dumpdata'),
	url(r'^group-search/$', views.dashboard, name='dashboard'),
	url(r'^status/(?P<dc>\w+)/$', views.status, name='status'),
	url(r'^listing', views.listing, name='listing'),
	url(r'^showvip', views.showvip, name='showvip'),
]

