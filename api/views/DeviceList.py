import logging

from django.views.generic import View

from api.helpers.Responses import ApiResponse
from api.helpers.Core import prepare_device_dic
from api.models import Device

logger = logging.getLogger(__name__)


class DeviceList(View):

    def get(self, request):
        logger.info("Get all unassigned actuators and sensors")

        pretty = request.GET.get("pretty", "True")

        devices = Device.objects.filter(brewpi=None)

        devices_arr = []
        for device in devices:
            devices_arr.append(prepare_device_dic(device))

        return ApiResponse.json(devices_arr, pretty, False)
