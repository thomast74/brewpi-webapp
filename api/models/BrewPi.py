import logging

from django.db import models
from django.utils import timezone


logger = logging.getLogger(__name__)


class BrewPi(models.Model):

    device_id = models.CharField(verbose_name='Device Id', max_length=30, primary_key=True)
    name = models.CharField(verbose_name='Name', max_length=30, unique=True, null=True)
    firmware_version = models.FloatField(verbose_name='Firmware Version', default=0.0)
    spark_version = models.CharField(verbose_name='Spark Version', max_length=2, default='')
    ip_address = models.GenericIPAddressField(verbose_name='Ip Address')
    web_address = models.GenericIPAddressField(verbose_name='Web Address', null=True)
    web_port = models.IntegerField("Web Port", null=True)
    brewpi_time = models.BigIntegerField(verbose_name='BrewPi Time', default=0)
    last_update = models.DateTimeField(verbose_name='Last Update')

    class Meta:
        verbose_name = 'BrewPi'
        verbose_name_plural = "BrewPis"
        ordering = ['name', 'device_id']
        get_latest_by = '-last_update'

    @classmethod
    def create(cls, device_id, firmware_version, spark_version, ip_address, web_address, web_port, brewpi_time):
        brewpi = cls(device_id, device_id, firmware_version, spark_version, ip_address, web_address, web_port, brewpi_time)
        brewpi.last_update = timezone.now()

        return brewpi

    def reset(self):
        self.name = None
        self.firmware_version = 0.0
        self.spark_version = ''
        self.ip_address = "0.0.0.0"
        self.web_address = "0.0.0.0"
        self.web_port = 80
        self.brewpi_time = 0
        self.last_update = timezone.now()

    def __str__(self):
        return "BrewPi: [{}/{}] {} -> '{}']".format(self.name, self.spark_version, self.device_id,
                                                 self.last_update.strftime('%Y-%m-%d %H:%M:%S'))
