import json
import logging

from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from api.models import BrewPiSpark, Device, Configuration
from api.helpers import ApiResponse
from api.tasks import sensor_calibration
from api.views.errors import Http400
from api.services.spark_connector import SparkConnector


logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
def start(request, device_id):
    logger.info("Start a calibration session on spark {}".format(device_id))

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)

    actuator_ids = get_actuator_ids(request.body)
    sensors = Device.objects.filter(pk__in=actuator_ids, spark=spark)

    check_if_calibration_is_possible(spark, sensors)
    set_spark_mode(spark)
    configure_sensors_for_calibration(spark, sensors)
    sensor_calibration.calculate_offset.apply_async((spark, sensors), countdown=200)

    return ApiResponse.ok()


def get_actuator_ids(json_string):
    logger.debug("Convert json actuator list into array")
    try:
        logger.debug("Received: " + json_string)
        json_dic = json.loads(json_string)

        return json_dic.get("sensors")

    except ValueError:
        raise Http400("POST does not contain a valid json string")


def check_if_calibration_is_possible(spark, devices):
    if len(devices) == 0:
        logger.debug("No devices to calibrate")
        raise Http400("No sensors to calibrate")

    if not all(device.device_type == Device.DEVICE_TYPE_ONEWIRE_TEMP for device in devices):
        logger.debug("Not all sensors are temperature sensors")
        raise Http400("Not all sensors are temperature sensors")

    if not all(device.configuration is None for device in devices):
        logger.debug("Some temperature sensors are assigned to a configuration")
        raise Http400("Some temperature sensors are assigned to a configuration")

    configs = Configuration.objects.filter(spark=spark, name="Calibration")
    if configs.count() > 0:
        logger.debug("Spark already calibrates sensors")
        raise Http400("Spark already calibrates sensors")


def set_spark_mode(spark):
    if spark.device_mode == spark.SPARK_MODE_MANUAL:
        logger.debug("Need to change spark mode to calibration")
        spark.set_mode(spark.SPARK_MODE_CALIBRATION)


def configure_sensors_for_calibration(spark, devices):
    config = Configuration.create(name="Calibration", config_type=Configuration.CONFIG_TYPE_CALIBRATION, spark=spark)
    config.save()

    for device in devices:
        device.offset = 0
        device.offset_result = ""
        device.configuration = config
        SparkConnector.set_device_offset(device)
        device.save()

