from django.conf.urls import patterns, include, url
from django.contrib import admin

from . import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'moviebar.views.home', name='home'),
    # url(r'^moviebar/', include('moviebar.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^alltags/', views.alltags),
    url(r'^tag/(?P<tag_id>\d+)/$', views.tag),
    url(r'^selected/', views.selected),
    url(r'^movie/(?P<movie_id>\d+)/$', views.movie),
    url(r'^search/$', views.search),
    url(r'^coupon/', views.coupon),
    url(r'^update/$', views.update),
    url(r'^$', views.home, name='home'),

)
