from django.conf.urls import patterns, include, url

from django.contrib import admin
from api.views.CloudRecordSummaryView import CloudRecordSummaryView
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'apel_rest.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/cloud/summaryrecord$', CloudRecordSummaryView.as_view())
)
