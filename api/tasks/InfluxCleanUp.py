from __future__ import absolute_import

import logging

from celery.schedules import crontab
from celery.task.base import periodic_task

from oinkbrew_webapp import settings

logger = logging.getLogger(__name__)


@periodic_task(
    run_every=(crontab(minute='*/1')),
    name="task_clean_up_influx_db",
    ignore_result=True
)
def task_clean_up_influx_db():

    # load configurations
    #   foreach configuration get the latest InfluxDB date
    #     delete all data that is older than 12 hours from latest date

    logger.info("Clean up InfluxDB of old data")
