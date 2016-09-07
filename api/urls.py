from django.conf.urls import url

from api.views.BrewPiDetail import BrewPiDetail
from api.views.BrewPiList import BrewPiList
from api.views.ConfigurationCommand import ConfigurationCommand
from api.views.ConfigurationDetail import ConfigurationDetail
from api.views.ConfigurationList import ConfigurationList
from api.views.ConfigurationGeneral import ConfigurationGeneral
from api.views.DeviceDetail import DeviceDetail
from api.views.DeviceList import DeviceList
from api.views.DeviceCommand import DeviceCommand
from api.views.LogDetail import LogDetail
from api.views.LogList import LogList


urlpatterns = [
    url(r'^configs/(?P<device_id>\w+)/(?P<config_id>[0-9]+)/', ConfigurationDetail.as_view()),
    url(r'^configs/(?P<device_id>\w+)/(?P<command>\w+)/', ConfigurationCommand.as_view()),
    url(r'^configs/(?P<device_id>\w+)/', ConfigurationList.as_view()),
    url(r'^configs/', ConfigurationGeneral.as_view()),

    url(r'^devices/(?P<pk>[0-9]+)/update/', DeviceDetail.as_view()),
    url(r'^devices/(?P<pk>[0-9]+)/delete/', DeviceDetail.as_view()),
    url(r'^devices/(?P<device_id>\w+)/(?P<id>[0-9]+)/', DeviceCommand.as_view()),
    url(r'^devices/(?P<device_id>\w+)/(?P<command>\w+)/', DeviceCommand.as_view()),
    url(r'^devices/(?P<device_id>\w+)/', DeviceDetail.as_view()),
    url(r'^devices/', DeviceList.as_view()),

    url(r'^logs/(?P<device_id>\w+)/(?P<config_id>[0-9]+)/', LogDetail.as_view()),
    url(r'^logs/(?P<device_id>\w+)/', LogList.as_view()),

    url(r'^brewpis/(?P<device_id>\w+)/(?P<command>\w+)/', BrewPiDetail.as_view()),
    url(r'^brewpis/(?P<device_id>\w+)/', BrewPiDetail.as_view()),
    url(r'^brewpis/', BrewPiList.as_view()),
]
