import logging

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods


logger = logging.getLogger(__name__)


@require_http_methods(["PUT"])
def create():
    config_id = 0

    return HttpResponse('{{"Status":"OK","ConfigId":"{}"}}\n'.format(config_id),
                        content_type="application/json")


@require_http_methods(["PUT"])
def update(config_id):
    return HttpResponse('{{"Status":"OK","ConfigId":"{}"}}\n'.format(config_id),
                        content_type="application/json")
