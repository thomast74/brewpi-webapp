import json
import logging

from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from api.models import Device, BrewPiSpark
from api.views.errors import Http400


logger = logging.getLogger(__name__)


def check_parameter(parameter, values, field_name):
    if parameter not in values:
        message = "Provided value for '{}' is not valid".format(field_name)
        logger.info("BAD REQUEST: " + message)
        raise Http400(message)

    return None


def get_and_check_spark_to_device(device_id, actuator_id):
    device = get_object_or_404(Device, pk=actuator_id)
    spark = get_object_or_404(BrewPiSpark, device_id=device_id)

    if device.spark.device_id != spark.device_id:
        raise Http400("Device not assigned to given Spark")

    return device, spark


class ApiResponse:
    def __init__(self):
        pass

    @staticmethod
    def ok():
        return HttpResponse('{"Status":"OK"}\n', content_type="application/json")

    @staticmethod
    def json(objects, pretty, is_models=True):
        if is_models:
            objects_serialized = serializers.serialize('json', objects)
            if pretty == "True":
                objects_serialized = json.dumps(json.loads(objects_serialized), indent=2)
        else:
            objects_serialized = json.dumps(objects, indent=2) if pretty == "True" else json.dumps(objects)

        return HttpResponse(objects_serialized, content_type="application/json")

    @staticmethod
    def bad_request(message):
        return HttpResponse('{{"Status":"ERROR","Message":"{}"}}\n'.format(message),
                            content_type="application/json", status=400)
