from django.utils.dateparse import parse_datetime
import logging
from datetime import datetime

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from influxdb import InfluxDBClient

from oinkbrew_webapp import settings
from api.helpers import ApiResponse
from api.models import BrewPiSpark, Configuration
from api.tasks import logs_message
from api.views.errors import Http400


logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def list_logs(request, device_id, config_id):
    logger.info("List logs for device {} and configuration {}".format(device_id, config_id))
    logger.debug(request.GET.urlencode())
    pretty = request.GET.get("pretty", "True")
    limit = request.GET.get("limit", 0)

    configuration, spark = get_and_check_spark_to_config(device_id, config_id)

    config_data = {
        "pk": configuration.pk,
        "name": configuration.name,
        "create_date": timezone.localtime(configuration.create_date).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "type": configuration.get_type_display(),
        "spark_id": spark.device_id,
        "spark": spark.name
    }

    name = configuration.name.replace(" ", "_") + "_" + configuration.create_date.strftime('%Y_%m_%d')
    if limit != "ALL":
        where = "WHERE time > now() - {}m".format(limit) if int(limit) > 0 else "WHERE time > now() - 24h"

    client = InfluxDBClient(settings.INFLUXDB_HOST, settings.INFLUXDB_PORT, settings.INFLUXDB_USER,
                            settings.INFLUXDB_PWD, settings.INFLUXDB_DB)

    influx_data = client.query('select * from "{}" {};'.format(name, where))

    for point in influx_data[name]:
        time = parse_datetime(point['time'])
        point['time'] = timezone.localtime(time).strftime('%Y-%m-%dT%H:%M:%SZ')

    config_data['points'] = influx_data[name]

    return ApiResponse.json(config_data, pretty, False)

@require_http_methods(["PUT"])
def add(request, device_id):
    logger.info("Received new actuator and sensor data for {}".format(device_id))

    logs_message.log_device_data.delay(device_id, request.body)

    return ApiResponse.ok()


def get_and_check_spark_to_config(device_id, config_id):
    config = get_object_or_404(Configuration, pk=config_id)
    spark = get_object_or_404(BrewPiSpark, device_id=device_id)

    if config.spark.device_id != spark.device_id:
        raise Http400("Configuration not assigned to given Spark")

    return config, spark