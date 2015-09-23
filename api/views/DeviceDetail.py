import logging

from django.views.generic import View
from django.shortcuts import get_object_or_404, get_list_or_404

from api.helpers.Responses import ApiResponse
from api.models import BrewPi, Device
from api.services.DeviceSerializer import DeviceSerializer

logger = logging.getLogger(__name__)


class DeviceDetail(View):

    def get(self, request, *args, **kwargs):
        device_id = kwargs['device_id']
        pretty = request.GET.get("pretty", "True")

        logger.info("Get all actuators and sensors attached to BrewPi {}".format(device_id))

        brewpi = get_object_or_404(BrewPi, device_id=device_id)
        devices = get_list_or_404(Device, brewpi=brewpi)

        return ApiResponse.json(devices, pretty)

    def put(self, request, *args, **kwargs):
        device_id = kwargs['device_id']

        logger.ingo("Receive registered device request from BrewPi {}: ".format(device_id, request.body))

        brewpi = get_object_or_404(BrewPi, device_id=device_id)

        device = DeviceSerializer.from_json(brewpi, request.body)
        device.save()

        return ApiResponse.ok()

    def post(self, request, *args, **kwargs):
        device_id = kwargs['device_id']

        logger.ingo("Update device request from BrewPi {}: ".format(device_id, request.body))

        brewpi = get_object_or_404(BrewPi, device_id=device_id)

        device = DeviceSerializer.from_json(brewpi, request.body)
        device.save()

        return ApiResponse.ok()

    def delete(self, request, *args, **kwargs):
        device_id = kwargs['device_id']

        logger.info("Delete actuator or sensor from BrewPi {}: {}".format(device_id, request.body))

        brewpi = get_object_or_404(BrewPi, device_id=device_id)

        device = DeviceSerializer.from_json(brewpi, request.body)
        device.delete()

        return ApiResponse.ok()
