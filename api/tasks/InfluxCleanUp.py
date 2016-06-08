from __future__ import absolute_import

import logging

from celery.schedules import crontab
from celery.task.base import periodic_task
from influxdb import InfluxDBClient

from api.models import Configuration
from oinkbrew_webapp import settings

logger = logging.getLogger(__name__)


@periodic_task(
    run_every=(crontab(minute=0, hour='*/1')),
    name="task_clean_up_influx_db",
    ignore_result=True
)
def task_clean_up_influx_db():

    logger.info("Clean up InfluxDB of old data")

    # load configurations
    #   foreach configuration get the latest InfluxDB date
    #     delete all data that is older than 12 hours from latest date
    logger.debug("Load all active configurations")
    configurations = Configuration.objects.filter(archived=False)

    client = InfluxDBClient(settings.INFLUXDB_HOST, settings.INFLUXDB_PORT, settings.INFLUXDB_USER,
                            settings.INFLUXDB_PWD, settings.INFLUXDB_DB)

    for configuration in configurations:
        measurement = configuration.name.replace(" ", "_") + "_" + configuration.create_date.strftime('%Y_%m_%d')
        logger.debug("Delete old entries from {}".format(measurement
                                                         ))
        rs = client.query('select * from "{}" ORDER BY time DESC LIMIT 1;'.format(measurement))
        points = list(rs.get_points(measurement=measurement))
        if len(points) > 0:
            last_time_entry = points[0]['time']

            query = (
                "DELETE FROM {} WHERE time < (\'{}\'  - {}h)"
            ).format(measurement, last_time_entry, 12)
            client.query(query)

            logger.debug("Entries deleted")
