from django.conf.urls import patterns, include, url

from django.contrib import admin
from api.views import IndexView
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'apel_rest.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^cloud/summaryrecord$', IndexView.as_view())
)
