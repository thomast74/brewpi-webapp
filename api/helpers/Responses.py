import json

from django.core import serializers
from django.http import HttpResponse


class ApiResponse:
    def __init__(self):
        pass

    @staticmethod
    def ok():
        return HttpResponse('{"Status":"OK"}\n', content_type="application/json")

    @staticmethod
    def message(message):
        return HttpResponse('{{"Status":"OK",{}}}\n'.format(message), content_type="application/json")

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
