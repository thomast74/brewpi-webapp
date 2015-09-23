import logging

from celery import shared_task
from api.helpers.BrewPi import get_brewpi
from api.models import Configuration
from api.services.BrewPiConnector import BrewPiConnector

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def request_configurations(device_id):
    logger.info("Send all configurations to BrewPi {}".format(device_id))

    brewpi = get_brewpi(device_id)
    if brewpi is None:
        logger.error("BrewPi {} can't be found".format(device_id))
        return "Error"

    configurations = Configuration.objects.filter(brewpi=brewpi)
    for configuration in configurations:
        tries = 0
        success = False
        while tries < 10:
            success = BrewPiConnector.send_configuration(brewpi, configuration)
            if success:
                break
            tries += 1

        if not success:
            logger.error("Configuration {} could not be send to BrewPi {}".format(configuration.pk, device_id))

    logger.info("Configurations send to BrewPi {}".format(device_id))
