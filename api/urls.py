from django.conf.urls import patterns, include, url
from api.views import status


urlpatterns = patterns('',
    url(r'^status/', status.save_or_update_status),
)
