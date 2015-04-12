import logging

from django.shortcuts import get_object_or_404, get_list_or_404
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from api.models import BrewPiSpark
from api.helpers import ApiResponse, check_parameter
from api.services.spark_connector import Connector


logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def get_list(request):
    logger.info("Request list of all registered sparks")
    pretty = request.GET.get("pretty", "True")

    sparks = get_list_or_404(BrewPiSpark)

    return ApiResponse.json(sparks, pretty)


@require_http_methods(["GET"])
def get(request, device_id):
    logger.info("Request spark information for {}".format(device_id))
    pretty = request.GET.get("pretty", "True")

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)

    return ApiResponse.json([spark], pretty)


@require_http_methods(["POST"])
def set_mode(request, device_id):
    logger.info("Received spark set mode request for {}".format(device_id))
    device_mode = request.POST.get("device_mode", "MANUAL")

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)
    check_parameter(device_mode, ['MANUAL', 'LOGGING', 'AUTOMATIC'], "device_mode")

    Connector().set_spark_mode(spark, device_mode)
    spark.device_mode = device_mode
    spark.save()

    return ApiResponse.ok()


@require_http_methods(["POST"])
def set_name(request, device_id):
    logger.info("Received spark set name request for {}".format(device_id))
    name = request.POST.get("name", None)

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)

    Connector().set_spark_name(spark, name)

    spark.name = name
    spark.save()

    return ApiResponse.ok()


@require_http_methods(["POST"])
def reset(request, device_id):
    logger.info("Received spark reset request for {}".format(device_id))

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)

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

    return ApiResponse.ok()


@require_http_methods(["POST"])
def update_firmware(request, device_id):
    logger.info("Update firmware on {}".format(device_id))

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)

    # TODO: get latest firmware => from where???
    # TODO: check version with version of Spark; if different send new firmware

    Connector().update_spark_firmware(spark)

    return ApiResponse.ok()


@require_http_methods(["DELETE"])
def delete(request, device_id):
    logger.info("Delete spark {} from database".format(device_id))

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)

    Connector().reset_spark(spark)

    spark.delete()

    return ApiResponse.ok()
