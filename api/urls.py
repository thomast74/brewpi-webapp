from django.conf.urls import patterns, url

from api.views import spark
from api.views import spark_config
from api.views import spark_device
from api.views import spark_logs
from api.views import spark_status


urlpatterns = patterns('',
                       url(r'^spark/(?P<device_id>\w+)/config/', spark_config.create),
                       url(r'^spark/(?P<device_id>\w+)/config/(?P<config_id>[0-9]+)/', spark_config.update),
                       url(r'^spark/(?P<device_id>\w+)/delete/', spark.delete),
                       url(r'^spark/(?P<device_id>\w+)/devices/(?P<actuator_id>[0-9]+)/delete/', spark_device.delete),
                       url(r'^spark/(?P<device_id>\w+)/devices/(?P<actuator_id>[0-9]+)/toggle/', spark_device.toggle),
                       url(r'^spark/(?P<device_id>\w+)/devices/(?P<actuator_id>[0-9]+)/', spark_device.get),
                       url(r'^spark/(?P<device_id>\w+)/devices/', spark_device.get_list),
                       url(r'^spark/(?P<device_id>\w+)/mode/', spark.set_mode),
                       url(r'^spark/(?P<device_id>\w+)/logs/(?P<config_id>[0-9]+)/', spark_logs.list_logs),
                       url(r'^spark/(?P<device_id>\w+)/logs/', spark_logs.add),
                       url(r'^spark/(?P<device_id>\w+)/name/', spark.set_name),
                       url(r'^spark/(?P<device_id>\w+)/reset/', spark.reset),
                       url(r'^spark/(?P<device_id>\w+)/firmware/', spark.update_firmware),
                       url(r'^spark/status/', spark_status.check_in),
                       url(r'^spark/(?P<device_id>\w+)/', spark.get),
                       url(r'^spark/', spark.get_list),
                       )
