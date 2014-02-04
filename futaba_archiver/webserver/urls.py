from django.conf.urls import patterns, include, url
from django.contrib import admin
from futaba_archive import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<board_name>[^/]+)/$',views.board, name="board"),
    url(r'^(?P<board_name>[^/]+)/(?P<post_number>\d*?)/$',views.thread, name="thread"),
    
)
