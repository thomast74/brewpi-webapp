import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from api.models import BrewPi
from api.helpers.Exceptions import BrewPiException

logger = logging.getLogger(__name__)


class BrewPiSerializer:

    def __init__(self):
        pass

    @staticmethod
    def from_json(json_string):
        logger.debug("Convert json status message into BrewPi object")

        try:
            logger.debug("Received: " + json_string)
            brewpi_dic = json.loads(json_string)
        except ValueError:
            return BrewPiException("Request body contains no valid status message")

        try:
            brewpi = BrewPi.objects.get(device_id=brewpi_dic.get('device_id'))

            logger.debug("Found existing BrewPi, update fields")

            brewpi.name = brewpi_dic.get("name", brewpi.name)
            brewpi.firmware_version = brewpi_dic.get("firmware_version", brewpi.firmware_version)
            brewpi.spark_version = brewpi_dic.get("spark_version", brewpi.spark_version)
            brewpi.ip_address = brewpi_dic.get("ip_address", brewpi.ip_address)
            brewpi.web_address = brewpi_dic.get("web_address", brewpi.web_address)
            brewpi.web_port = brewpi_dic.get("web_port", brewpi.web_port)
            brewpi.brewpi_time = brewpi_dic.get("brewpi_time", brewpi.brewpi_time)
            brewpi.last_update = timezone.now()

            logger.debug(brewpi.__str__())

        except ObjectDoesNotExist:
            logger.debug("BrewPi does not exist, create a new one")

            brewpi = BrewPi.create(brewpi_dic.get("device_id"), brewpi_dic.get("firmware_version"),
                                   brewpi_dic.get("spark_version"), brewpi_dic.get("ip_address"), 
                                   brewpi_dic.get("web_address"), brewpi_dic.get("web_port"), 
                                   brewpi_dic.get("brewpi_time"))

            logger.debug(brewpi.__str__())

        return brewpi, brewpi_dic.get('command')
