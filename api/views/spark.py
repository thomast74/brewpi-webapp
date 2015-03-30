from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from api.models import BrewPiSpark
from api.services import spark_connector

import logging


logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@csrf_exempt
def set_mode(request, device_id):
    logger.info("Received spark set mode request for {}".format(device_id))
    spark = BrewPiSpark.objects.get(device_id=device_id)
    device_mode = request.POST.get("device_mode", "MANUAL")

    if spark is not None and device_mode in ('MANUAL','LOGGING','AUTOMATIC'):
        spark_connector.set_mode(spark, device_mode)
        spark.device_mode = device_mode
        spark.save()

        return HttpResponse("OK")
    else:
        return HttpResponse("ERROR")


@require_http_methods(["POST"])
@csrf_exempt
def reset(request, device_id):
    logger.info("Received spark reset request for {}".format(device_id))
    spark = BrewPiSpark.objects.get(device_id=device_id)

    if spark is not None:
        spark_connector.reset_device(spark)

        spark.name = None
        spark.device_mode = "MANUAL"
        spark.device_config = "None"
        spark.firmware_version = 0.0
        spark.board_revision = ""
        spark.ip_address = "0.0.0.0"
        spark.web_address = "0.0.0.0"
        spark.last_update = timezone.now()
        spark.save()

        return HttpResponse("OK")
    else:
        return HttpResponse("ERROR")
