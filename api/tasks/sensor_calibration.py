from __future__ import absolute_import
from django.db import transaction
import logging

from celery import shared_task
from api.models import Configuration


logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def calculate_offset(spark, sensors):
    logger.info("Calculate offset for spark {} and sensors {}".format(spark, sensors))

    # for all sensors
    #    load last 3 minutes of temp calibration data as avg
    #    calculate the offset based on boiling water is 100C
    #    set offset in database
    #    send new offset to spark

    validate_offset.apply_async((spark, sensors), countdown=200)

    return "Ok"


@shared_task(ignore_result=True)
def validate_offset(spark, sensors):
    logger.info("Validate offset for spark {} and sensors {}".format(spark, sensors))

    # for all devices
    #   load last 2 minutes of calibration temp data
    #   log error if still off by more than 0.25 degree in average

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

