from django.conf.urls import patterns, include, url
from api.views import spark
from api.views import spark_status


urlpatterns = patterns('',
    url(r'^spark/status/', spark_status.checkin),
    url(r'^spark/(?P<device_id>\w+)/reset/', spark.reset),
)
