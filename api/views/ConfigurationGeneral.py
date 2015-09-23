import logging

from django.views.generic import View
from django.shortcuts import get_list_or_404
from api.helpers.Core import prepare_configuration_dic
from api.helpers.Responses import ApiResponse
from api.models import Configuration

logger = logging.getLogger(__name__)


class ConfigurationGeneral(View):

    def get(self, request, *args, **kwargs):
        pretty = request.GET.get("pretty", "True")

        logger.info("Get all configurations")

        configurations = get_list_or_404(Configuration)

        configs_arr = []
        for configuration in configurations:
            configs_arr.append(prepare_configuration_dic(configuration))

        return ApiResponse.json(configs_arr, pretty, False)
