import logging

from django.views.generic import View

from api.helpers.Responses import ApiResponse
from api.tasks import RequestConfigurations

logger = logging.getLogger(__name__)


class ConfigurationCommand(View):

    def put(self, request, *args, **kwargs):
        device_id = kwargs['device_id']
        command = kwargs['command']

        logger.info("Execute configuration command '{}' on BrewPi {}: {}".format(command, device_id, request.body))

        if command == "request":
            RequestConfigurations.request_configurations.delay(device_id)
            return ApiResponse.ok()

        return ApiResponse.bad_request("Command '{}' unknown".format(command))
