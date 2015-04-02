from django.conf.urls import patterns, include, url
from api.views import spark
from api.views import spark_status


urlpatterns = patterns('',
    url(r'^spark/', spark.list),
    url(r'^spark/status/', spark_status.checkin),
    url(r'^spark/(?P<device_id>\w+)/mode/', spark.set_mode),
    url(r'^spark/(?P<device_id>\w+)/name/', spark.set_name),
    url(r'^spark/(?P<device_id>\w+)/reset/', spark.reset),
    url(r'^spark/(?P<device_id>\w+)/firmware/', spark.update_firmware),
)
