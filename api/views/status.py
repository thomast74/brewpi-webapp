from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from api.models import BrewPiSpark
from api.tasks import status_message


@require_http_methods(["POST"])
@csrf_exempt
def save_or_update_status(request):

    spark = BrewPiSpark.from_json(request.body)

    if spark is not None:
        spark.save()
        status_message.check_if_status_update_required.delay(spark.device_id)
        return HttpResponse("OK")
    else:
        return HttpResponse("ERROR")
