import json
import logging

from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from api.services.spark_connector import SparkException, SparkConnector


logger = logging.getLogger(__name__)


class BrewPiSpark(models.Model):
    SPARK_MODE_MANUAL = 0
    SPARK_MODE_CALIBRATION = 1
    SPARK_MODE_LOGGING = 2
    SPARK_MODE_AUTOMATIC = 3

    SPARK_MODE = (
        (SPARK_MODE_MANUAL, 'MANUAL'),
        (SPARK_MODE_CALIBRATION, 'CALIBRATION'),
        (SPARK_MODE_LOGGING, 'LOGGING'),
        (SPARK_MODE_AUTOMATIC, 'AUTOMATIC')
    )

    device_id = models.CharField(verbose_name='Device Id', max_length=30, primary_key=True)
    name = models.CharField(verbose_name='Name', max_length=30, unique=True, null=True)
    device_mode = models.IntegerField(verbose_name='Device Mode', choices=SPARK_MODE, default=0)
    firmware_version = models.FloatField(verbose_name='Firmware Version', default=0.0)
    ip_address = models.GenericIPAddressField(verbose_name='Ip Address')
    web_address = models.GenericIPAddressField(verbose_name='Web Address', null=True)
    web_port = models.IntegerField("Web Port", null=True)
    spark_time = models.BigIntegerField(verbose_name='Spark Time', default=0)
    last_update = models.DateTimeField(verbose_name='Last Update')

    class Meta:
        verbose_name = 'BrewPi Spark'
        verbose_name_plural = "BrewPi Sparks"
        ordering = ['name', 'device_id']
        get_latest_by = '-last_update'

    @staticmethod
    def from_json(json_string):
        logger.debug("Convert json status message into BrewPiSpark object")
        try:
            logger.debug("Received: " + json_string)
            status = json.loads(json_string)
        except ValueError:
            return SparkException("Request body contains no valid status message")

        try:
            spark = BrewPiSpark.objects.get(device_id=status.get('device_id'))

            logger.debug("Found existing spark, update fields")

            spark.device_mode = status.get("device_mode")
            spark.firmware_version = status.get("firmware_version")
            spark.ip_address = status.get("ip_address")
            spark.web_address = status.get("web_address")
            spark.web_port = status.get("web_port")
            spark.spark_time = status.get("datetime")
            spark.last_update = timezone.now()
            spark.save()

            logger.debug(spark.__str__())

        except ObjectDoesNotExist:
            logger.debug("Spark does not exist, create a new one")

            spark = BrewPiSpark.create(status.get("device_id"), status.get("device_mode"),
                                       status.get("firmware_version"), status.get("ip_address"),
                                       status.get("web_address"), status.get("web_port"), status.get("datetime"))
            spark.save()

            logger.debug(spark.__str__())

        return spark

    @classmethod
    def create(cls, device_id, device_mode, firmware_version, ip_address, web_address, web_port, spark_time):
        spark = cls(device_id, device_id, device_mode, firmware_version, ip_address, web_address, web_port, spark_time)
        spark.last_update = timezone.now()

        return spark

    def set_mode(self, device_mode):
        if device_mode >= self.SPARK_MODE_MANUAL or device_mode <= self.SPARK_MODE_AUTOMATIC:
            SparkConnector().set_spark_mode(self, device_mode)
            self.device_mode = device_mode
            self.save()
        else:
            raise SparkException("Given device mode is invalid")

    def __str__(self):
        return "BrewPiSpark: [{}] {} -> '{}' -> {}]".format(self.last_update.strftime('%Y-%m-%d %H:%M:%S'),
                                                            self.device_id, self.name, self.device_mode)
