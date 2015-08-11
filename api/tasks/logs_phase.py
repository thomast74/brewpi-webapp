from __future__ import absolute_import
from datetime import datetime
import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task
from pytz import utc
from api.models import TemperaturePhase, Configuration

from api.models.brew_pi_spark import BrewPiSpark

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def log_phase_data(device_id, config_id, json_data):
    logger.debug("Received log phase data for {}: {}".format(device_id, json_data))

    spark = get_spark(device_id)
    if spark is None:
        logger.error("Spark with device_id {} can't be found".format(device_id))
        return "Error"

    config = get_config(config_id, spark)
    if spark is None:
        logger.error("Configuration with id {} can't be found".format(config_id))
        return "Error"

    log_phase_dic = convert_json_data(json_data)
    if log_phase_dic is None:
        logger.error("Convert json data into log phase not possible")
        return "Error"

    phase = get_phase(config, log_phase_dic)
    if phase is None:
        logger.error("Phase for configuration could not be found")
        return "Error"

    logger.debug("Phase {} change to {}".format(phase, log_phase_dic.get("done")))
    phase.done = log_phase_dic.get("done")
    phase.save()

    return "Ok"


def get_spark(device_id):
    try:
        return BrewPiSpark.objects.get(device_id=device_id)

    except ObjectDoesNotExist:
        return None


def get_config(config_id, spark):
    try:
        return Configuration.objects.get(pk=config_id, spark=spark)

    except ObjectDoesNotExist:
        return None


def convert_json_data(json_data):
    try:
        return json.loads(json_data)

    except ValueError:
        return None


def get_phase(config, log_phase_dic):
    try:

        start_date = datetime.fromtimestamp(log_phase_dic.get("start_date")).replace(tzinfo=utc)
        duration = log_phase_dic.get("duration") / 60000
        temperature = log_phase_dic.get("temperature") / 1000

        logger.debug(
            "Phase to update: [config: {}; start_date: {}; duration: {}; temperature: {};]".format(config,
                                                                                                   start_date,
                                                                                                   duration,
                                                                                                   temperature))

        phase = TemperaturePhase.objects.get(configuration=config, start_date=start_date, duration=duration,
                                             temperature=temperature)

    except ObjectDoesNotExist:
        return None

    return phase
