import logging

from django.shortcuts import get_object_or_404
from django.views.generic import View

from api.helpers.Responses import ApiResponse
from api.models import BrewPi, Device
from api.services.BrewPiSerializer import BrewPiSerializer
from api.services.BrewPiConnector import BrewPiConnector
from api.tasks import StatusMessage

logger = logging.getLogger(__name__)


class BrewPiDetail(View):

    def get(self, request, *args, **kwargs):
        logger.info("Get BrewPi detail information for {}".format(kwargs['device_id']))

        pretty = request.GET.get("pretty", "True")
        brewpi = get_object_or_404(BrewPi, device_id=kwargs['device_id'])

        return ApiResponse.json([brewpi], pretty)

    def put(self, request, *args, **kwargs):
        logger.info("Received PUT request for BrewPi {}".format(kwargs['device_id']))

        brewpi, command = BrewPiSerializer.from_json(request.body)

        logger.info("Command: {}".format(command))

        if command == "status" or command == "update" or command == "name":
            self.update(brewpi, request)
        elif command == "reset":
            self.reset(brewpi)

        return ApiResponse.ok()

    def delete(self, request, *args, **kwargs):
        logger.info("Delete BrewPi {}".format(kwargs['device_id']))

        brewpi = get_object_or_404(BrewPi, device_id=kwargs['device_id'])
        BrewPiConnector.send_reset(brewpi)

        Device.objects.filter(brewpi=brewpi).exclude(device_type=Device.DEVICE_TYPE_ONEWIRE_TEMP).delete()
        Device.objects.filter(brewpi=brewpi, device_type=Device.DEVICE_TYPE_ONEWIRE_TEMP).update(brewpi=None)
        brewpi.delete()

        return ApiResponse.ok()

    def update(self, brewpi, request):
        logger.info("Received BrewPi status/update request for {}".format(brewpi.device_id))

        brewpi.save()

        StatusMessage.check_if_status_update_required.delay(brewpi.device_id, request.META['SERVER_PORT'])

        return ApiResponse.ok()

    def reset(self, brewpi):
        logger.info("Received BrewPi reset request for {}".format(brewpi.pk))

        BrewPiConnector.send_reset(brewpi)

        brewpi.send_reset()
        brewpi.save()

        return ApiResponse.ok()
