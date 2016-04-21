import logging

from django.shortcuts import get_list_or_404
from django.views.generic import View

from api.helpers.Core import prepare_brewpi_dic
from api.helpers.Responses import ApiResponse

from api.models import BrewPi
from api.services.BrewPiSerializer import BrewPiSerializer
from api.tasks import StatusMessage

logger = logging.getLogger(__name__)


class BrewPiList(View):

    def get(self, request):
        logger.info("Request list of all registered BrewPi's")

        pretty = request.GET.get("pretty", "True")

        brewpis = get_list_or_404(BrewPi)

        brewpi_arr = []
        for brewpi in brewpis:
            brewpi_arr.append(prepare_brewpi_dic(brewpi))

        return ApiResponse.json(brewpi_arr, pretty, False)

    def post(self, request):
        logger.info("Create a new BrewPi")

        brewpi = BrewPiSerializer.from_json(request.body)

        brewpi.save()
        StatusMessage.check_if_status_update_required.delay(brewpi.device_id, request.META['SERVER_PORT'])

        return ApiResponse.ok()
