from __future__ import absolute_import
import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task
from django.utils import timezone
from influxdb import InfluxDBClient

from api.models import Device
from api.models.brew_pi_spark import BrewPiSpark
from oinkbrew_webapp import settings


logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def log_device_data(device_id, json_data):
    logger.debug("Received log device data for {}: {}".format(device_id, json_data))

    spark = get_spark(device_id)
    if spark is None:
        logger.error("Spark with device_id {} can't be found".format(device_id))
        return "Error"

    log_data = convert_json_data(json_data)
    if log_data is None:
        logger.error("Convert json data into log data not possible")
        return "Error"

    influx_data = build_points(log_data, spark)
    save_points(influx_data)

    logger.debug("-")

    return "Ok"


def get_spark(device_id):
    try:
        return BrewPiSpark.objects.get(device_id=device_id)

    except ObjectDoesNotExist:
        return None


def get_device(spark, pin_nr, hw_address):
    try:
        device = Device.objects.get(pin_nr=pin_nr, hw_address=hw_address)

        if device.spark == spark:
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


def build_points(log_data, spark):
    influx_data_dic = {}

    for device_data_dic in log_data:

        device = get_device(spark, device_data_dic.get("pin_nr"), device_data_dic.get("hw_address"))
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
            influx_data_dic[name].device_id = spark.device_id
            influx_data_dic[name].config_type = config_type
            influx_data_dic[name].timestamp = timezone.now()
            influx_data_dic[name].fields[function] = value

    return influx_data_dic


def save_points(influx_data_dic):
    if len(influx_data_dic) > 0:

        client = InfluxDBClient(settings.INFLUXDB_HOST, settings.INFLUXDB_PORT, settings.INFLUXDB_USER,
                                settings.INFLUXDB_PWD, settings.INFLUXDB_DB)

        for point in influx_data_dic:
            influx_point = influx_data_dic[point]
            data = convert_to_points(influx_point)

            client.write_points(data)

    else:
        logger.debug("No data to log received or no device part of a configuration")


def convert_to_points(influx_data):
    return [
        {
            "name": influx_data.name,
            "tags": {
                "device_id": influx_data.device_id,
                "config_type": influx_data.config_type
            },
            "timestamp": influx_data.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
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
