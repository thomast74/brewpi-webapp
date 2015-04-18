import json
import logging
import sys

from datetime import timedelta
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from brew_pi_spark import BrewPiSpark
from configuration import Configuration


logger = logging.getLogger(__name__)


class Device(models.Model):
    DEVICE_TYPE_NONE = 0
    DEVICE_TYPE_PIN = 1
    DEVICE_TYPE_ONEWIRE_TEMP = 2

    DEVICE_TYPE = (
        (DEVICE_TYPE_NONE, 'None'),
        (DEVICE_TYPE_PIN, 'Pin'),
        (DEVICE_TYPE_ONEWIRE_TEMP, 'OneWire Temp'),
    )

    DEVICE_FUNCTION_NONE = 0
    DEVICE_FUNCTION_FRIDGE_COOLING_ACTUATOR = 1
    DEVICE_FUNCTION_FRIDGE_HEATING_ACTUATOR = 2
    DEVICE_FUNCTION_FRIDGE_FAN_ACTUATOR = 3

    DEVICE_FUNCTION_HLT_HEATING_ACTUATOR = 4
    DEVICE_FUNCTION_BOIL_HEATING_ACTUATOR = 5
    DEVICE_FUNCTION_PUMP_1_ACTUATOR = 6
    DEVICE_FUNCTION_PUMP_2_ACTUATOR = 7

    DEVICE_FUNCTION_FRIDGE_BEER_1_TEMP_SENSOR = 8
    DEVICE_FUNCTION_FRIDGE_BEER_2_TEMP_SENSOR = 9
    DEVICE_FUNCTION_FRIDGE_BEER_3_TEMP_SENSOR = 10
    DEVICE_FUNCTION_FRIDGE_INSIDE_TEMP_SENSOR = 11
    DEVICE_FUNCTION_FRIDGE_OUTSIDE_TEMP_SENSOR = 12

    DEVICE_FUNCTION_HLT_IN_TEMP_SENSOR = 13
    DEVICE_FUNCTION_HLT_OUT_TEMP_SENSOR = 14
    DEVICE_FUNCTION_MASH_IN_TEMP_SENSOR = 15
    DEVICE_FUNCTION_MACH_OUT_TEMP_SENSOR = 16
    DEVICE_FUNCTION_BOIL_IN_TEMP_SENSOR = 17
    DEVICE_FUNCTION_BOIL_INSIDE_TEMP_SENSOR = 18
    DEVICE_FUNCTION_BOIL_OUT_TEMP_SENSOR = 19

    DEVICE_FUNCTION = (
        (DEVICE_FUNCTION_NONE, 'None'),

        (DEVICE_FUNCTION_FRIDGE_COOLING_ACTUATOR, 'Fridge Cooling Actuator'),
        (DEVICE_FUNCTION_FRIDGE_HEATING_ACTUATOR, 'Fridge Heating Actuator'),
        (DEVICE_FUNCTION_FRIDGE_FAN_ACTUATOR, 'Fridge Fan Actuator'),

        (DEVICE_FUNCTION_HLT_HEATING_ACTUATOR, 'HLT Heating Actuator'),
        (DEVICE_FUNCTION_BOIL_HEATING_ACTUATOR, 'Boil Heating Actuator'),
        (DEVICE_FUNCTION_PUMP_1_ACTUATOR, 'Pump 1 Actuator'),
        (DEVICE_FUNCTION_PUMP_2_ACTUATOR, 'Pump 2 Actuator'),

        (DEVICE_FUNCTION_FRIDGE_BEER_1_TEMP_SENSOR, 'Fridge Beer 1 Temp Sensor'),
        (DEVICE_FUNCTION_FRIDGE_BEER_2_TEMP_SENSOR, 'Fridge Beer 2 Temp Sensor'),
        (DEVICE_FUNCTION_FRIDGE_BEER_3_TEMP_SENSOR, 'Fridge Beer 3 Temp Sensor'),
        (DEVICE_FUNCTION_FRIDGE_INSIDE_TEMP_SENSOR, 'Fridge Inside Temp Sensor'),
        (DEVICE_FUNCTION_FRIDGE_OUTSIDE_TEMP_SENSOR, 'Outside Fridge Temp Sensor'),

        (DEVICE_FUNCTION_HLT_IN_TEMP_SENSOR, 'HLT In Temp Sensor'),
        (DEVICE_FUNCTION_HLT_OUT_TEMP_SENSOR, 'HLT Out Temp Sensor'),
        (DEVICE_FUNCTION_MASH_IN_TEMP_SENSOR, 'Mash In Temp Sensor'),
        (DEVICE_FUNCTION_MACH_OUT_TEMP_SENSOR, 'Mash Out Temp Sensor'),
        (DEVICE_FUNCTION_BOIL_IN_TEMP_SENSOR, 'Boil In Temp Sensor'),
        (DEVICE_FUNCTION_BOIL_INSIDE_TEMP_SENSOR, 'Boil Inside Temp Sensor'),
        (DEVICE_FUNCTION_BOIL_OUT_TEMP_SENSOR, 'Boil Out Temp Sensor')

    )

    spark = models.ForeignKey(BrewPiSpark, null=True)
    configuration = models.ForeignKey(Configuration, null=True)
    type = models.IntegerField(verbose_name='Hardware Type', choices=DEVICE_TYPE, default=0)
    function = models.IntegerField(verbose_name='Device Function', choices=DEVICE_FUNCTION, default=0)
    value = models.CharField(verbose_name="Value", max_length=10, default="")
    pin_nr = models.IntegerField(verbose_name='Pin Nr', default=0)
    hw_address = models.CharField(verbose_name='Hardware Address', max_length=16)
    offset = models.BigIntegerField(verbose_name='Offset', default=0)
    is_invert = models.BooleanField(verbose_name='Is Invert?', default=True)
    is_deactivate = models.BooleanField(verbose_name='Is Deactivate?', default=False)
    last_update = models.DateTimeField(verbose_name='Last Update')

    class Meta:
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
        unique_together = ('pin_nr', 'hw_address',)
        ordering = ['spark', 'type']
        get_latest_by = '-last_update'

    @staticmethod
    def from_json_list(spark, devices_json):

        logger.debug("Convert json devices into Device objects")
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
                    device.value = device_dic.get('value').lstrip()
                    device.is_invert = device_dic_hardware.get('is_invert')
                    device.offset = device_dic_hardware.get('offset')
                    device.is_deactivate = device_dic_hardware.get('is_deactivate')
                    device.last_update = timezone.now()
                    device.save()

                    logger.debug(device.__str__())

                except ObjectDoesNotExist:
                    device = Device.create(spark, device_dic.get('type'), device_dic.get('value').lstrip(),
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

    @staticmethod
    def from_json(device, device_json):

        logger.debug("Convert json devices into Device objects")
        try:
            logger.debug("Received: " + device_json)
            device_dic = json.loads(device_json)
        except ValueError:
            return None

        device_dic_hardware = device_dic.get('hardware')

        device.spark = device.spark
        device.type = device_dic.get('type')
        device.value = device_dic.get('value').lstrip()
        device.is_invert = device_dic_hardware.get('is_invert')
        device.offset = device_dic_hardware.get('offset')
        device.is_deactivate = device_dic_hardware.get('is_deactivate')
        device.last_update = timezone.now()
        device.save()

        logger.debug(device.__str__())

    @classmethod
    def create(cls, spark, hw_type, value, pin_nr, hw_address, offset, is_invert, is_deactivate):
        device = cls(spark=spark, type=hw_type, value=value, pin_nr=pin_nr, hw_address=hw_address, offset=offset,
                     is_invert=is_invert,
                     is_deactivate=is_deactivate)
        device.last_update = timezone.now()

        return device

    def __str__(self):
        return "Device: [{}] {} -> ['{}' -> {}]".format(self.last_update.strftime('%Y-%m-%d %H:%M:%S'), self.spark,
                                                        self.pin_nr, self.hw_address)
