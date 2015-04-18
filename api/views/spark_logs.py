import logging

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from api.helpers import ApiResponse
from api.tasks import logs_message


logger = logging.getLogger(__name__)


@require_http_methods(["PUT"])
def add(request, device_id):
    logger.info("Received new actuator and sensor data for {}".format(device_id))

    logs_message.log_device_data.delay(device_id, request.body)

    return ApiResponse.ok()
