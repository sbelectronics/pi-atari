from django.conf.urls import patterns, url

from atari_web_ui import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^loadCartridge$', views.loadCartridge, name='loadCartridge'),
    url(r'^reset$', views.reset, name='reset'),
    url(r'^getStatus$', views.getStatus, name='getStatus'),
)
