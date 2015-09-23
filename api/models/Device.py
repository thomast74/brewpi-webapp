from __builtin__ import staticmethod
import logging

from django.db import models
from django.utils import timezone

from BrewPi import BrewPi
from Configuration import Configuration


logger = logging.getLogger(__name__)


class Device(models.Model):
    DEVICE_TYPE_NONE = 0
    DEVICE_TYPE_ACTUATOR_PIN = 1
    DEVICE_TYPE_ACTUATOR_PWM = 2
    DEVICE_TYPE_ONEWIRE_TEMP = 3

    DEVICE_TYPE = (
        (DEVICE_TYPE_NONE, 'None'),
        (DEVICE_TYPE_ACTUATOR_PIN, 'Actuator Digital'),
        (DEVICE_TYPE_ACTUATOR_PWM, 'Actuator PWM'),
        (DEVICE_TYPE_ONEWIRE_TEMP, 'OneWire Temp. Sensor'),
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
    DEVICE_FUNCTION_HLT_INSIDE_TEMP_SENSOR = 14
    DEVICE_FUNCTION_HLT_OUT_TEMP_SENSOR = 15
    DEVICE_FUNCTION_MASH_IN_TEMP_SENSOR = 16
    DEVICE_FUNCTION_MASH_INSIDE_TEMP_SENSOR = 17
    DEVICE_FUNCTION_MASH_OUT_TEMP_SENSOR = 18
    DEVICE_FUNCTION_BOIL_IN_TEMP_SENSOR = 19
    DEVICE_FUNCTION_BOIL_INSIDE_TEMP_SENSOR = 20
    DEVICE_FUNCTION_BOIL_OUT_TEMP_SENSOR = 21

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
        (DEVICE_FUNCTION_HLT_INSIDE_TEMP_SENSOR, 'HLT Inside Temp Sensor'),
        (DEVICE_FUNCTION_HLT_OUT_TEMP_SENSOR, 'HLT Out Temp Sensor'),
        (DEVICE_FUNCTION_MASH_IN_TEMP_SENSOR, 'Mash In Temp Sensor'),
        (DEVICE_FUNCTION_MASH_INSIDE_TEMP_SENSOR, 'Mash Inside Temp Sensor'),
        (DEVICE_FUNCTION_MASH_OUT_TEMP_SENSOR, 'Mash Out Temp Sensor'),
        (DEVICE_FUNCTION_BOIL_IN_TEMP_SENSOR, 'Boil In Temp Sensor'),
        (DEVICE_FUNCTION_BOIL_INSIDE_TEMP_SENSOR, 'Boil Inside Temp Sensor'),
        (DEVICE_FUNCTION_BOIL_OUT_TEMP_SENSOR, 'Boil Out Temp Sensor')
    )

    brewpi = models.ForeignKey(BrewPi, null=True)
    configuration = models.ForeignKey(Configuration, null=True)
    device_type = models.IntegerField(verbose_name='Hardware Type', choices=DEVICE_TYPE, default=0)
    function = models.IntegerField(verbose_name='Device Function', choices=DEVICE_FUNCTION, default=0)
    value = models.FloatField(verbose_name="Value", default=0)
    pin_nr = models.IntegerField(verbose_name='Pin Nr', default=0)
    hw_address = models.CharField(verbose_name='Hardware Address', max_length=16)
    offset = models.FloatField(verbose_name='Offset', default=0)
    offset_from_brewpi = models.FloatField(verbose_name='Offset From BrewPi', default=0)
    offset_result = models.CharField(verbose_name="Calibration Result", max_length=30, default="")
    is_deactivate = models.BooleanField(verbose_name='Is Deactivate?', default=False)
    last_update = models.DateTimeField(verbose_name='Last Update')

    class Meta:
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
        unique_together = ('pin_nr', 'hw_address', 'brewpi')
        ordering = ['brewpi', 'device_type']
        get_latest_by = '-last_update'

    @staticmethod
    def get_function(function_display):
        for choice in Device.DEVICE_FUNCTION:
            if choice[1] == function_display:
                return choice[0]

        return Device.DEVICE_FUNCTION_NONE

    @classmethod
    def create(cls, brewpi, device_type, function, value, pin_nr, hw_address, offset_from_brewpi, is_deactivate):
        device = cls(brewpi=brewpi, device_type=device_type, function=function, value=value, pin_nr=pin_nr,
                     hw_address=hw_address, offset_from_brewpi=offset_from_brewpi, is_deactivate=is_deactivate)
        device.last_update = timezone.now()

        return device

    def __str__(self):
        return "Device: [{}] {} -> ['{}' -> {}]".format(self.last_update.strftime('%Y-%m-%d %H:%M:%S'), self.brewpi,
                                                        self.pin_nr, self.hw_address)
