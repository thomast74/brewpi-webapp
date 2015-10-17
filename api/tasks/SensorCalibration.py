from __future__ import absolute_import

import sys

from celery import shared_task
from celery.utils.log import get_task_logger

from influxdb import InfluxDBClient

from api.models import Configuration
from api.services.BrewPiConnector import BrewPiConnector

from oinkbrew_webapp import settings


logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def calculate_offset(brewpi, sensors):
    logger.info("Calculate offset for BrewPi {} and sensors {}".format(brewpi, sensors))

    client = InfluxDBClient(settings.INFLUXDB_HOST, settings.INFLUXDB_PORT, settings.INFLUXDB_USER,
                            settings.INFLUXDB_PWD, settings.INFLUXDB_DB)

    for sensor in sensors:
        try:
            result = client.query('SELECT MEAN("{}") FROM Calibration WHERE time > now() - 3m;'.format(sensor.pk))

            sensor.offset = 100 - float(result["Calibration"][0]["MEAN"])

            logger.debug("Sensor {} offset: {}".format(sensor.pk, sensor.offset))

            BrewPiConnector().send_device_offset(sensor)

            sensor.save()
        except:
            tp, value, traceback = sys.exc_info()
            logger.error("Sensor error: {}".format(value))

    validate_offset.apply_async((brewpi, sensors), countdown=200)

    return "Ok"


@shared_task(ignore_result=True)
def validate_offset(brewpi, sensors):
    logger.info("Validate offset for BrewPi {} and sensors {}".format(brewpi, sensors))

    client = InfluxDBClient(settings.INFLUXDB_HOST, settings.INFLUXDB_PORT, settings.INFLUXDB_USER,
                            settings.INFLUXDB_PWD, settings.INFLUXDB_DB)

    for sensor in sensors:
        try:
            result = client.query('SELECT MEAN("{}") FROM Calibration WHERE time > now() - 3m;'.format(sensor.pk))

            offset = 100 - float(result["Calibration"][0]["MEAN"])

            if -0.1 > offset or offset > 0.1:
                logger.info("Sensor {} is still off by {}".format(sensor, offset))
                sensor.offset_result = "Still off by: {}".format(offset)
                sensor.save()

        except:
            tp, value, traceback = sys.exc_info()
            logger.error("Sensor error: {}".format(value))

    cleanup_calibration(brewpi, sensors)

    return "Ok"


def cleanup_calibration(brewpi, sensors):
    logger.info("Calibration cleanup for BrewPi {} and sensors {}".format(brewpi, sensors))

    # remove device configuration
    for sensor in sensors:
        logger.debug("Remove sensor {} from calibration configuration".format(sensor))
        sensor.configuration = None
        sensor.save()

    # remove configuration
    Configuration.objects.filter(brewpi=brewpi, name="Calibration").delete()

    # if no other calibration exists; drop measurement Calibration
    if Configuration.objects.filter(name="Calibration").count() == 0:
        client = InfluxDBClient(settings.INFLUXDB_HOST, settings.INFLUXDB_PORT, settings.INFLUXDB_USER,
                                settings.INFLUXDB_PWD, settings.INFLUXDB_DB)
        client.query("DROP MEASUREMENT Calibration;")
