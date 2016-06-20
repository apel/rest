from django.conf.urls import patterns, include, url

from django.contrib import admin
from api.views.CloudRecordSummaryView import CloudRecordSummaryView
from api.views.CloudRecordView import CloudRecordView
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'apel_rest.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/cloud/record$', CloudRecordView.as_view()),
    url(r'^api/v1/cloud/record/summary$', CloudRecordSummaryView.as_view())
)
