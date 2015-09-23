import logging

from django.views.generic import View
from api.helpers.Responses import ApiResponse
from api.tasks import LogsMessage

logger = logging.getLogger(__name__)


class LogList(View):
    def post(self, request, *args, **kwargs):
        logger.info("Received new actuator and sensor data from BrewPi {}".format(kwargs['device_id']))

        LogsMessage.log_device_data.delay(kwargs['device_id'], request.body)

        return ApiResponse.ok()
