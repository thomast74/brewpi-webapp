import logging

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from api.models import BrewPiSpark
from api.tasks import status_message


logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@csrf_exempt
def check_in(request):
    logger.info("Check in request received")
    spark = BrewPiSpark.from_json(request.body)

    if spark is not None:

        status_message.check_if_status_update_required.delay(spark.device_id)

        return HttpResponse('{"Status":"OK"}\n', content_type="application/json")
    else:
        return HttpResponse('{"Status":"ERROR"}\n', content_type="application/json", status=400)
