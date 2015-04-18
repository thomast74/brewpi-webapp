import logging

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from api.helpers import ApiResponse
from api.models import BrewPiSpark
from api.tasks import status_message


logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
def check_in(request):
    logger.info("Check in request received")

    spark = BrewPiSpark.from_json(request.body)

    status_message.check_if_status_update_required.delay(spark.device_id, request.META['SERVER_PORT'])

    return ApiResponse.ok()
