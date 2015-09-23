import logging

from django.views.generic import View
from api.helpers.Responses import ApiResponse
from api.models import Device

logger = logging.getLogger(__name__)


class DeviceList(View):

    def get(self, request):
        logger.info("Get all unassigned actuators and sensors")

        pretty = request.GET.get("pretty", "True")

        devices = Device.objects.filter(brewpi=None)

        return ApiResponse.json(devices, pretty)
