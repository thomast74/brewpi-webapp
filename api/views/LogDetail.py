import logging

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.generic import View
from django.shortcuts import get_object_or_404

from influxdb import InfluxDBClient

from api.helpers.Responses import ApiResponse
from api.models import Configuration, BrewPi
from api.views.errors import Http400

from oinkbrew_webapp import settings

logger = logging.getLogger(__name__)


class LogDetail(View):

    def get(self, request, *args, **kwargs):
        device_id = kwargs['device_id']
        config_id = kwargs['config_id']
        pretty = request.GET.get("pretty", "True")
        limit = request.GET.get("limit", 0)

        logger.info("Get list of logs for BrewPi {} and Configuration {}".format(device_id, config_id))

        configuration, brewpi = self.get_and_check_brewpi_to_config(device_id, config_id)

        config_data = {
            "pk": configuration.pk,
            "name": configuration.name,
            "create_date": timezone.localtime(configuration.create_date).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "type": configuration.get_type_display(),
            "device_id": brewpi.device_id,
            "name": brewpi.name
        }

        name = configuration.name.replace(" ", "_") + "_" + configuration.create_date.strftime('%Y_%m_%d')
        where = ""
        if "ALL" != limit:
            where = "WHERE time > now() - {}m".format(limit) if int(limit) > 0 else "WHERE time > now() - 24h"

        client = InfluxDBClient(settings.INFLUXDB_HOST, settings.INFLUXDB_PORT, settings.INFLUXDB_USER,
                                settings.INFLUXDB_PWD, settings.INFLUXDB_DB)

        influx_data = client.query('select * from "{}" {};'.format(name, where))

        for point in influx_data[name]:
            time = parse_datetime(point['time'])
            point['time'] = timezone.localtime(time).strftime('%Y-%m-%dT%H:%M:%SZ')

        config_data['points'] = influx_data[name]

        return ApiResponse.json(config_data, pretty, False)

    def delete(self, request, *args, **kwargs):
        device_id = kwargs['device_id']
        config_id = kwargs['config_id']

        logger.info("Delete logs for BrewPi {} and Configuration {}".format(device_id, config_id))

        configuration, brewpi = self.get_and_check_brewpi_to_config(device_id, config_id)

        name = configuration.name.replace(" ", "_") + "_" + configuration.create_date.strftime('%Y_%m_%d')

        client = InfluxDBClient(settings.INFLUXDB_HOST, settings.INFLUXDB_PORT, settings.INFLUXDB_USER,
                                settings.INFLUXDB_PWD, settings.INFLUXDB_DB)

        client.query("DROP SERIES {}".format(name))

    def get_and_check_brewpi_to_config(self, device_id, config_id):
        config = get_object_or_404(Configuration, pk=config_id)
        brewpi = get_object_or_404(BrewPi, device_id=device_id)

        if config.brewpi.device_id != brewpi.device_id:
            raise Http400("Configuration not assigned to given BrewPi")

        return config, brewpi
