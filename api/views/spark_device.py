import logging

from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from api.models import BrewPiSpark
from api.models import Device
from api.services.spark_connector import Connector
from api.views.errors import Http400, Http500
from api.helpers import ApiResponse, get_and_check_spark_to_device


logger = logging.getLogger(__name__)


def get_add_or_delete(request, device_id):
    if request.method == 'PUT':
        return add(request, device_id)
    elif request.method == 'DELETE':
        return delete_from_spark(request, device_id)
    else:
        return get_list(request, device_id)


def add(request, device_id):
    logger.info("Add new device to Spark {}".format(device_id))

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)
    Device.from_json(spark, request.body)

    logger.debug("-")

    return ApiResponse.ok()


def get_list(request, device_id):
    logger.info("Request list of devices connected to Spark {}\n".format(device_id))
    pretty = request.GET.get("pretty", "True")

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)

    devices_json = Connector().request_device_list(spark)
    devices = Device.from_json_list(spark, devices_json)

    return ApiResponse.json(devices, pretty)


@require_http_methods(["GET"])
def get(request, device_id, actuator_id):
    logger.info("Request device {} from {}".format(actuator_id, device_id))
    pretty = request.GET.get("pretty", "True")

    device, spark = get_and_check_spark_to_device(device_id, actuator_id)

    device_json = Connector().request_device(device)
    Device.update_from_json(device, device_json)

    return ApiResponse.json([device], pretty)


def delete_from_spark(request, device_id):
    logger.info("Receive disconnected device request from spark {}".format(device_id))

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)
    device = Device.from_json(spark, request.body)

    device.delete()

    return ApiResponse.ok()


@require_http_methods(["DELETE"])
def delete(request, device_id, actuator_id):
    logger.info("Delete device {} from spark {} from database".format(actuator_id, device_id))

    device, spark = get_and_check_spark_to_device(device_id, actuator_id)

    response = Connector().deleteDevice(device)
    if response == "OK":
        device.delete()
        return ApiResponse.ok()
    else:
        raise Http500(response)


@require_http_methods(["POST"])
def toggle(request, device_id, actuator_id):
    logger.info("Toggle actuator on {} and actuator {}".format(device_id, actuator_id))

    device, spark = get_and_check_spark_to_device(device_id, actuator_id)

    if device.type != Device.DEVICE_TYPE_PIN:
        raise Http400("Device is not an Actuator")

    value = request.POST.get("value", 0)

    actuator_state = Connector().device_toggle(device, value)

    device.value = actuator_state
    device.save()

    return ApiResponse.ok()