from __future__ import absolute_import
import json
import logging

from celery import shared_task

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from influxdb import InfluxDBClient

from api.helpers.BrewPi import get_brewpi
from api.models import Device, Configuration

from oinkbrew_webapp import settings

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def log_device_data(device_id, json_data):
    logger.debug("Received log device data for {}: {}".format(device_id, json_data))

    brewpi = get_brewpi(device_id)
    if brewpi is None:
        logger.error("BrewPi with device_id {} can't be found".format(device_id))
        return "Error"

    log_data = convert_json_data(json_data)
    if log_data is None:
        logger.error("Convert json data into log data not possible")
        return "Error"

    influx_data_dic = {}

    if "temperatures" in log_data:
        build_temperature_points(log_data.get("temperatures"), brewpi, influx_data_dic)

    if "targets" in log_data:
        build_target_points(log_data.get("targets"), brewpi, influx_data_dic)

    if len(influx_data_dic) > 0:
        save_points(influx_data_dic)

    logger.debug("-")

    return "Ok"


def get_configuration(config_id):
    try:
        return Configuration.objects.get(pk=config_id)

    except ObjectDoesNotExist:
        return None


def get_device(brewpi, pin_nr, hw_address):
    try:
        device = Device.objects.get(pin_nr=pin_nr, hw_address=hw_address)

        if device.brewpi == brewpi:
            return device
        else:
            return None

    except ObjectDoesNotExist:
        return None


def convert_json_data(json_data):
    try:
        return json.loads(json_data)

    except ValueError:
        return None


def build_temperature_points(log_data, brewpi, influx_data_dic):
    logger.debug("Build temperature points: {}".format(log_data))

    for device_data_dic in log_data:

        device = get_device(brewpi, device_data_dic.get("pin_nr"), device_data_dic.get("hw_address"))
        if device is None or device.configuration is None:
            logger.debug("No configuration assigned to device: {}".format(device))
            continue

        if device.configuration.name == "Calibration":
            name = device.configuration.name
            config_type = ""
            function = device.pk
        else:
            name = device.configuration.name.replace(" ", "_") + "_" + device.configuration.create_date.strftime(
                '%Y_%m_%d')
            config_type = device.configuration.get_type_display()
            function = device.get_function_display()

        value = float(device_data_dic.get("value"))
        if value < -120:
            # wrong reading don't log
            continue

        if name in influx_data_dic:
            influx_data_dic[name].fields[function] = value
        else:
            influx_data_dic[name] = InfluxData()
            influx_data_dic[name].name = name
            influx_data_dic[name].device_id = brewpi.device_id
            influx_data_dic[name].config_type = config_type
            influx_data_dic[name].timestamp = timezone.now()
            influx_data_dic[name].fields[function] = value


def build_target_points(target_data, brewpi, influx_data_dic):

    logger.debug("Build target temperature points: {}".format(target_data))

    for target_temperature in target_data:

        configuration = get_configuration(target_temperature.get("config_id"))
        if configuration is None:
            logger.debug("Configuration {} can't be found".format(target_temperature.get("config_id")))
            continue

        if configuration.name == "Calibration":
            continue

        name = configuration.name.replace(" ", "_") + "_" + configuration.create_date.strftime('%Y_%m_%d')
        config_type = configuration.get_type_display()
        function = "Target Temperature"
        value = float(target_temperature.get("temperature"))

        if name in influx_data_dic:
            influx_data_dic[name].fields[function] = value
        else:
            influx_data_dic[name] = InfluxData()
            influx_data_dic[name].name = name
            influx_data_dic[name].device_id = brewpi.device_id
            influx_data_dic[name].config_type = config_type
            influx_data_dic[name].timestamp = timezone.now()
            influx_data_dic[name].fields[function] = value


def save_points(influx_data_dic):
    if len(influx_data_dic) > 0:

        client = InfluxDBClient(settings.INFLUXDB_HOST, settings.INFLUXDB_PORT, settings.INFLUXDB_USER,
                                settings.INFLUXDB_PWD, settings.INFLUXDB_DB)

        for point in influx_data_dic:
            influx_point = influx_data_dic[point]
            data = convert_to_points(influx_point)
            logger.debug(data)

            client.write_points(data)

    else:
        logger.debug("No data to log received or no device part of a configuration")


def convert_to_points(influx_data):
    return [
        {
            "measurement": influx_data.name,
            "tags": {
                "device_id": influx_data.device_id,
                "config_type": influx_data.config_type
            },
            "time": influx_data.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "fields": {
                key: influx_data.fields[key] for key in influx_data.fields
                }
        }]


class InfluxData:
    name = None  # configuration.name_configuration.create_date
    device_id = None  # dictionary of <string, string> typically device_id, configuration type
    config_type = None
    timestamp = None  # UTC time
    fields = None  # dictionary of <Function (as text), Value>

    def __init__(self):
        self.fields = {}
