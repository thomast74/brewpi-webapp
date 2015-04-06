import json
import logging

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from api.models import BrewPiSpark
from api.models import Device
from api.services.spark_connector import Connector, SparkException


logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def list_sparks(request):
    logger.info("Request list of all registered sparks")
    output_format = request.GET.get("format", "json")
    pretty = request.GET.get("pretty", "True")

    if output_format not in 'json':
        return HttpResponse('{"Status":"ERROR","Message":"Only Json supported"}\n', content_type="application/json",
                            status=400)

    sparks = serializers.serialize(output_format, BrewPiSpark.objects.all())

    logger.debug("Sparks: " + sparks)

    if pretty == "True":
        sparks = json.dumps(json.loads(sparks), indent=2)

    return HttpResponse(sparks, content_type="application/json")


@require_http_methods(["GET"])
def list_devices(request, device_id):
    logger.info("Request list of devices connected to Spark {}".format(device_id))

    output_format = request.GET.get("format", "json")
    pretty = request.GET.get("pretty", "True")

    if output_format not in 'json':
        return HttpResponse('{"Status":"ERROR","Message":"Only Json supported"}\n', content_type="application/json",
                            status=400)

    try:
        spark = BrewPiSpark.objects.get(device_id=device_id)
    except ObjectDoesNotExist:
        return HttpResponse('{"Status":"ERROR",Message="Spark does not exists"}\n', content_type="application/json",
                            status=400)

    try:
        devices_json = Connector().request_device_list(spark)
    except SparkException as e:
        return HttpResponse('{{"Status":"ERROR","Message":"{}"}}\n'.format(e.value),
                            status=500,
                            content_type="application/json")

    devices = Device.from_json_list(spark, devices_json)

    devices_ser = serializers.serialize(output_format, devices)

    logger.debug("Sparks: " + devices_ser)

    if pretty == "True":
        devices_ser = json.dumps(json.loads(devices_ser), indent=2)

    return HttpResponse(devices_ser, content_type="application/json")

@require_http_methods(["GET"])
def list_device(request, device_id, actuator_id):
    logger.info("Request device {} from {}".format(actuator_id, device_id))

    output_format = request.GET.get("format", "json")
    pretty = request.GET.get("pretty", "True")

    try:
        device = Device.objects.get(pk=actuator_id)
    except ObjectDoesNotExist:
        return HttpResponse('{"Status":"ERROR",Message="Device does not exists"}\n',
                            content_type="application/json",
                            status=400)

    if device.spark.device_id != device_id:
        return HttpResponse('{"Status":"ERROR",Message="Device not assigned to given Spark"}\n',
                            content_type="application/json",
                            status=400)

    try:
        device_json = Connector().request_device(device)
    except SparkException as e:
        return HttpResponse('{{"Status":"ERROR","Message":"{}"}}\n'.format(e.value),
                            status=500,
                            content_type="application/json")

    Device.from_json(device, device_json)

    device_ser = serializers.serialize(output_format, [device])

    logger.debug("Spark device: " + device_ser)

    if pretty == "True":
        device_ser = json.dumps(json.loads(device_ser), indent=2)

    return HttpResponse(device_ser, content_type="application/json")

@require_http_methods(["POST"])
def set_mode(request, device_id):
    logger.info("Received spark set mode request for {}".format(device_id))

    try:
        spark = BrewPiSpark.objects.get(device_id=device_id)
    except ObjectDoesNotExist:
        return HttpResponse('{"Status":"ERROR",Message="Spark does not exists"}\n', content_type="application/json",
                            status=400)

    device_mode = request.POST.get("device_mode", "MANUAL")

    if device_mode in ('MANUAL', 'LOGGING', 'AUTOMATIC'):
        try:
            Connector().set_spark_mode(spark, device_mode)
        except SparkException as e:
            return HttpResponse('{{"Status":"ERROR","Message":"{}"}}\n'.format(e.value),
                                status=500,
                                content_type="application/json")

        spark.device_mode = device_mode
        spark.save()

        return HttpResponse('{"Status":"OK"}\n', content_type="application/json")
    else:
        return HttpResponse('{"Status":"ERROR","Message","Only MANUAL, LOGGING or AUTOMATIC is supported"}\n',
                            content_type="application/json", status=400)


@require_http_methods(["POST"])
def set_name(request, device_id):
    logger.info("Received spark set name request for {}".format(device_id))

    try:
        spark = BrewPiSpark.objects.get(device_id=device_id)
    except ObjectDoesNotExist:
        return HttpResponse('{"Status":"ERROR",Message="Spark does not exists"}\n', content_type="application/json",
                            status=400)

    name = request.POST.get("name", None)

    try:
        Connector().set_spark_name(spark, name)
    except SparkException as e:
        return HttpResponse('{{"Status":"ERROR","Message":"{}"}}\n'.format(e.value),
                            status=500,
                            content_type="application/json")
    spark.name = name
    spark.save()

    return HttpResponse('{"Status":"OK"}\n', content_type="application/json")


@require_http_methods(["POST"])
def reset(request, device_id):
    logger.info("Received spark reset request for {}".format(device_id))

    try:
        spark = BrewPiSpark.objects.get(device_id=device_id)
    except ObjectDoesNotExist:
        return HttpResponse('{"Status":"ERROR",Message="Spark does not exists"}\n', content_type="application/json",
                            status=400)
    try:
        Connector().reset_spark(spark)
    except SparkException as e:
        return HttpResponse('{{"Status":"ERROR","Message":"{}"}}\n'.format(e.value),
                            status=500,
                            content_type="application/json")

    spark.name = None
    spark.device_mode = "MANUAL"
    spark.device_config = "None"
    spark.firmware_version = 0.0
    spark.board_revision = ""
    spark.ip_address = "0.0.0.0"
    spark.web_address = "0.0.0.0"
    spark.last_update = timezone.now()
    spark.save()

    return HttpResponse('{"Status":"OK"}\n', content_type="application/json")


@require_http_methods(["POST"])
def update_firmware(request, device_id):
    logger.info("Update firmware on {}".format(device_id))

    try:
        spark = BrewPiSpark.objects.get(device_id=device_id)
    except ObjectDoesNotExist:
        return HttpResponse('{"Status":"ERROR",Message="Spark does not exists"}\n', content_type="application/json",
                            status=400)

    # get latest firmware => from where???
    # check version with version of Spark
    # if different send new firmware

    try:
        Connector().update_spark_firmware(spark)
    except SparkException as e:
        return HttpResponse('{{"Status":"ERROR","Message":"{}"}}\n'.format(e.value),
                            status=500,
                            content_type="application/json")

    return HttpResponse('{"Status":"OK"}\n', content_type="application/json")


@require_http_methods(["DELETE"])
def delete(request, device_id):
    logger.info("Delete spark {} from database".format(device_id))

    try:
        spark = BrewPiSpark.objects.get(device_id=device_id)
    except ObjectDoesNotExist:
        return HttpResponse('{"Status":"ERROR",Message="Spark does not exists"}\n', content_type="application/json",
                            status=400)

    try:
        Connector().reset_spark(spark)
    except SparkException as e:
        return HttpResponse('{{"Status":"ERROR","Message":"{}"}}\n'.format(e.value),
                            status=500,
                            content_type="application/json")

    spark.delete()

    return HttpResponse('{"Status":"OK"}\n', content_type="application/json")

@require_http_methods(["DELETE"])
def device_delete(request, device_id, actuator_id):
    logger.info("Delete device {} from spark {} from database".format(actuator_id, device_id))

    try:
        device = Device.objects.get(pk=actuator_id)
    except ObjectDoesNotExist:
        return HttpResponse('{"Status":"ERROR",Message="Device does not exists"}\n',
                            content_type="application/json",
                            status=400)

    if device.spark.device_id != device_id:
        return HttpResponse('{"Status":"ERROR",Message="Device not assigned to given Spark"}\n',
                            content_type="application/json",
                            status=400)

    device.delete()

    return HttpResponse('{"Status":"OK"}\n', content_type="application/json")

@require_http_methods(["POST"])
def device_toggle(request, device_id, actuator_id):
    logger.info("Toggle actuator on {} and actuator {}".format(device_id, actuator_id))

    try:
        device = Device.objects.get(pk=actuator_id)
    except ObjectDoesNotExist:
        return HttpResponse('{"Status":"ERROR",Message="Device does not exists"}\n',
                            content_type="application/json",
                            status=400)

    if device.spark.device_id != device_id:
        return HttpResponse('{"Status":"ERROR",Message="Device not assigned to given Spark"}\n',
                            content_type="application/json",
                            status=400)

    if device.type != Device.DEVICE_HARDWARE_PIN:
        return HttpResponse('{"Status":"ERROR",Message="Device is not a Actuator"}\n',
                            content_type="application/json",
                            status=400)

    try:
        actuator_state = Connector().device_toggle(device)

        device.value = actuator_state
        device.save()

        return HttpResponse('{{"Status":"OK","ActuatorState":"{}"}}\n'.format(actuator_state),
                            content_type="application/json")
    except SparkException as e:
        return HttpResponse('{{"Status":"ERROR","Message":"{}"}}\n'.format(e.value),
                            status=500,
                            content_type="application/json")
