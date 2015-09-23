from django.core.exceptions import ObjectDoesNotExist
from api.models import BrewPi


def get_brewpi(device_id):
    try:
        return BrewPi.objects.get(device_id=device_id)
    except ObjectDoesNotExist:
        return None
