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
        limit = request.GET.get("limit", 3)

        logger.info("Get list of logs for BrewPi {} and Configuration {}".format(device_id, config_id))

        client = InfluxDBClient(settings.INFLUXDB_HOST, settings.INFLUXDB_PORT, settings.INFLUXDB_USER,
                                settings.INFLUXDB_PWD, settings.INFLUXDB_DB)

        configuration, brewpi = self.get_and_check_brewpi_to_config(device_id, config_id)

        config_data = {
            "pk": configuration.pk,
            "name": configuration.name,
            "create_date": timezone.localtime(configuration.create_date).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "type": configuration.get_type_display(),
            "device_id": brewpi.device_id,
            "name": brewpi.name
        }

        config_type = configuration.get_type_display()
        name = config_type + "_" + configuration.name.replace(" ",
                                                                     "_") + "_" + configuration.create_date.strftime(
            '%Y_%m_%d')

        rs = client.query('select * from "{}" ORDER BY time DESC LIMIT 1;'.format(name))
        last_time_entry = list(rs.get_points(measurement=name))[0]['time']

        if configuration.type == Configuration.CONFIG_TYPE_FERMENTATION:
            query = (
                "SELECT mean(\"Fridge Beer 1 Temp Sensor\") AS Beer_1, "
                "       mean(\"Fridge Beer 2 Temp Sensor\") AS Beer_2, "
                "       mean(\"Fridge Inside Temp Sensor\") AS Fridge, "
                "       mean(\"Target Temperature\") AS Target, "
                "       mean(\"Fridge Cooling Actuator\") AS Cooling, "
                "       mean(\"Fridge Heating Actuator\") AS Heating "
                "FROM {} WHERE time > (\'{}\'  - {}h) AND time <= \'{}\' "
                "GROUP BY time(1m) fill(null) ORDER BY time"
            ).format(name, last_time_entry, limit, last_time_entry)
        else:
            query = (
                "SELECT mean(\"Boil Heating Actuator\") AS Boil_Heating, "
                "       mean(\"HLT Heating Actuator\") AS HLT_Heating, "
                "       mean(\"Pump 1 Actuator\") AS Pump_1, "
                "       mean(\"Pump 2 Actuator\") AS Pump_2, "
                "       mean(\"HLT Out Temp Sensor\") AS HLT_Out, "
                "       mean(\"Mash In Temp Sensor\") AS Mash_In, "
                "       mean(\"Mash Out Temp Sensor\") AS Mast_Out, "
                "       mean(\"Target Temperature\") AS Target "
                "FROM {} WHERE time > (\'{}\'  - {}h) AND time <= \'{}\' "
                "GROUP BY time(5s) fill(null) ORDER BY time"
            ).format(name, last_time_entry, limit, last_time_entry)

        rs = client.query(query)

        for point in list(rs.get_points(measurement=name)):
            time = parse_datetime(point['time'])
            point['time'] = timezone.localtime(time).strftime('%Y-%m-%dT%H:%M:%SZ')

        config_data['points'] = list(rs.get_points(measurement=name))

        return ApiResponse.json(config_data, pretty, False)

    def delete(self, request, *args, **kwargs):
        device_id = kwargs['device_id']
        config_id = kwargs['config_id']

        logger.info("Delete logs for BrewPi {} and Configuration {}".format(device_id, config_id))

        configuration, brewpi = self.get_and_check_brewpi_to_config(device_id, config_id)

        config_type = configuration.get_type_display()
        name = config_type + "_" + configuration.name.replace(" ", "_") + "_" + configuration.create_date.strftime(
            '%Y_%m_%d')

        client = InfluxDBClient(settings.INFLUXDB_HOST, settings.INFLUXDB_PORT, settings.INFLUXDB_USER,
                                settings.INFLUXDB_PWD, settings.INFLUXDB_DB)

        client.query("DROP SERIES {}".format(name))

    def get_and_check_brewpi_to_config(self, device_id, config_id):
        config = get_object_or_404(Configuration, pk=config_id)
        brewpi = get_object_or_404(BrewPi, device_id=device_id)

        if config.brewpi.device_id != brewpi.device_id:
            raise Http400("Configuration not assigned to given BrewPi")

        return config, brewpi
