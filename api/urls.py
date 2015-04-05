from django.conf.urls import patterns, url

from api.views import spark
from api.views import spark_status


urlpatterns = patterns('',
                       url(r'^spark/(?P<device_id>\w+)/delete/', spark.delete),
                       url(r'^spark/(?P<device_id>\w+)/devices/(?P<actuator_id>[0-9]+)/toggle/', spark.device_toggle),
                       url(r'^spark/(?P<device_id>\w+)/devices/', spark.list_devices),
                       url(r'^spark/(?P<device_id>\w+)/mode/', spark.set_mode),
                       url(r'^spark/(?P<device_id>\w+)/name/', spark.set_name),
                       url(r'^spark/(?P<device_id>\w+)/reset/', spark.reset),
                       url(r'^spark/(?P<device_id>\w+)/firmware/', spark.update_firmware),
                       url(r'^spark/status/', spark_status.check_in),
                       url(r'^spark/', spark.list_sparks),
                       )
