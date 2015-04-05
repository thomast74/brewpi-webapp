import json
import logging
import sys

from datetime import timedelta
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from brew_pi_spark import BrewPiSpark


logger = logging.getLogger(__name__)


class Device(models.Model):

    DEVICE_HARDWARE_NONE = 0
    DEVICE_HARDWARE_PIN = 1
    DEVICE_HARDWARE_ONEWIRE_TEMP = 2

    HARDWARE_TYPE = (
        (DEVICE_HARDWARE_NONE, 'None'),
        (DEVICE_HARDWARE_PIN, 'Pin'),
        (DEVICE_HARDWARE_ONEWIRE_TEMP, 'OneWire Temp'),
    )

    spark = models.ForeignKey(BrewPiSpark, null=True)
    type = models.IntegerField(verbose_name='Hardware Type', choices=HARDWARE_TYPE, default=0)
    value = models.CharField(verbose_name="Value", max_length=10, default="")
    pin_nr = models.IntegerField(verbose_name='Pin Nr', default=0)
    hw_address = models.CharField(verbose_name='Hardware Address', max_length=16)
    offset = models.BigIntegerField(verbose_name='Offset', default=0)
    is_invert = models.BooleanField(verbose_name='Is Invert?', default=True)
    is_deactivate = models.BooleanField(verbose_name='Is Deactivate?', default=False)
    last_update = models.DateTimeField(verbose_name='Last Update')

    class Meta:
        verbose_name = 'Device'
        verbose_name_plural = "Devices"
        unique_together = ('pin_nr', 'hw_address',)
        ordering = ['spark', 'type']
        get_latest_by = '-last_update'

    @staticmethod
    def from_json(spark, devices_json):

        logger.debug("Convert json devices into Device object")
        try:
            logger.debug("Received: " + devices_json)
            devices_list = json.loads(devices_json)
        except ValueError:
            return None

        for device_dic in devices_list:

            try:

                device_dic_hardware = device_dic.get('hardware')

                try:
                    device = Device.objects.get(pin_nr=device_dic_hardware.get('pin_nr'),
                                                hw_address=device_dic_hardware.get("hw_address"))

                    device.spark = spark
                    device.type = device_dic.get('type')
                    device.value = device_dic.get('value')
                    device.is_invert = device_dic_hardware.get('is_invert')
                    device.offset = device_dic_hardware.get('offset')
                    device.is_deactivate = device_dic_hardware.get('is_deactivate')
                    device.last_update = timezone.now()
                    device.save()

                    logger.debug(device.__str__())

                except ObjectDoesNotExist:
                    device = Device.create(spark, device_dic.get('type'), device_dic.get('value'),
                                           device_dic_hardware.get('pin_nr'),
                                           device_dic_hardware.get('hw_address'), device_dic_hardware.get('offset'),
                                           device_dic_hardware.get('is_invert'),
                                           device_dic_hardware.get('is_deactivate'))
                    device.save()

                    logger.debug(device.__str__())
            except:
                logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
                return None

        Device.objects.filter(spark=spark, last_update__lt=(timezone.now() - timedelta(minutes=1))).delete()

        return Device.objects.filter(spark=spark)

    @classmethod
    def create(cls, spark, hw_type, value, pin_nr, hw_address, offset, is_invert, is_deactivate):
        device = cls(spark=spark, type=hw_type, value=value, pin_nr=pin_nr, hw_address=hw_address, offset=offset,
                     is_invert=is_invert,
                     is_deactivate=is_deactivate)
        device.last_update = timezone.now()

        return device

    def __str__(self):
        return "Device: [{}] {} -> '{}' -> {}]".format(self.last_update.strftime('%Y-%m-%d %H:%M:%S'), self.spark,
                                                       self.pin_nr, self.hw_address)
