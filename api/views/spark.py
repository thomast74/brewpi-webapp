import json
import logging

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from api.models import BrewPiSpark
from api.models import Device
from api.services.spark_connector import Connector


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

    devices_json = Connector().request_device_list(spark)
    devices = Device.from_json(spark, devices_json)

    devices_ser = serializers.serialize(output_format, devices)

    logger.debug("Sparks: " + devices_ser)

    if pretty == "True":
        devices_ser = json.dumps(json.loads(devices_ser), indent=2)

    return HttpResponse(devices_ser, content_type="application/json")


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
        Connector().set_spark_mode(spark, device_mode)

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

    Connector().set_spark_name(spark, name)

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

    Connector().reset_spark(spark)

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

    Connector().update_spark_firmware(spark)

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
    except:
        logger.error("Spark {} can't be reset".format(device_id))

    spark.delete()

    return HttpResponse('{"Status":"OK"}\n', content_type="application/json")
