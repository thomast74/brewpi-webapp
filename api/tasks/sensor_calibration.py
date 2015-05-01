from __future__ import absolute_import
import logging
import sys

from celery import shared_task
from influxdb import InfluxDBClient
from api.models import Configuration
from api.services.spark_connector import SparkConnector
from oinkbrew_webapp import settings


logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def calculate_offset(spark, sensors):
    logger.info("Calculate offset for spark {} and sensors {}".format(spark, sensors))

    client = InfluxDBClient(settings.INFLUXDB_HOST, settings.INFLUXDB_PORT, settings.INFLUXDB_USER,
                            settings.INFLUXDB_PWD, settings.INFLUXDB_DB)

    for sensor in sensors:
        try:
            result = client.query('SELECT MEAN("{}") FROM Calibration WHERE time > now() - 3m;'.format(sensor.pk))

            sensor.offset = 100 - float(result["Calibration"][0]["MEAN"])

            logger.debug("Sensor {} offset: {}".format(sensor.pk, sensor.offset))

            SparkConnector().set_device_offset(sensor)

            sensor.save()
        except:
            tp, value, traceback = sys.exc_info()
            logger.error("Sensor error: {}".format(value))

    validate_offset.apply_async((spark, sensors), countdown=200)

    return "Ok"


@shared_task(ignore_result=True)
def validate_offset(spark, sensors):
    logger.info("Validate offset for spark {} and sensors {}".format(spark, sensors))

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

    cleanup_calibration(spark, sensors)

    return "Ok"


def cleanup_calibration(spark, sensors):
    logger.info("Calibration cleanup for spark {} and sensors {}".format(spark, sensors))

    # set spark mode to MANUAL if in CALIBRATION
    if spark.device_mode == spark.SPARK_MODE_CALIBRATION:
        logger.debug("Set spark {} mode to MANUAL".format(spark))
        spark.set_mode(spark.SPARK_MODE_MANUAL)

    # remove device configuration
    for sensor in sensors:
        logger.debug("Remove sensor {} from calibration configuration".format(sensor))
        sensor.configuration = None
        sensor.save()

    # remove configuration
    Configuration.objects.filter(spark=spark, name="Calibration").delete()

    # if no other calibration exists; drop measurement Calibration
    if Configuration.objects.filter(name="Calibration").count() == 0:
        client = InfluxDBClient(settings.INFLUXDB_HOST, settings.INFLUXDB_PORT, settings.INFLUXDB_USER,
                                settings.INFLUXDB_PWD, settings.INFLUXDB_DB)
        # client.query("DROP MEASUREMENT Calibration;")


