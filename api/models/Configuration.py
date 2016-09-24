import api
import logging

from django.db import models
from django.utils import timezone

from api.models import BrewPi

logger = logging.getLogger(__name__)


class Configuration(models.Model):

    CONFIG_TYPE_NONE = 0
    CONFIG_TYPE_BREW = 1
    CONFIG_TYPE_FERMENTATION = 2
    CONFIG_TYPE_CALIBRATION = 3

    CONFIG_TYPE = (
        (CONFIG_TYPE_NONE, 'None'),
        (CONFIG_TYPE_BREW, 'Brew'),
        (CONFIG_TYPE_FERMENTATION, 'Fermentation'),
        (CONFIG_TYPE_CALIBRATION, 'Calibration')
    )

    name = models.CharField(verbose_name="Name", max_length=30)
    create_date = models.DateTimeField(verbose_name='Create Date', editable=False)
    type = models.IntegerField(verbose_name='Configuration Type', choices=CONFIG_TYPE)
    brewpi = models.ForeignKey(BrewPi, verbose_name="BrewPi", null=True)
    temp_sensor_id = models.IntegerField(verbose_name='Temp Sensor', null=True)
    heat_actuator_id = models.IntegerField(verbose_name='Heat Actuator', null=True)
    cool_actuator_id = models.IntegerField(verbose_name='Cool Actuator', null=True)
    fan_actuator_id = models.IntegerField(verbose_name='Fan Actuator', null=True)
    pump_1_actuator_id = models.IntegerField(verbose_name='Pump 1 Actuator', null=True)
    pump_2_actuator_id = models.IntegerField(verbose_name='Pump 2 Actuator', null=True)
    archived = models.BooleanField(verbose_name='Archived', null=False, default=False)

    class Meta:
        verbose_name = 'Configuration'
        verbose_name_plural = 'Configurations'
        ordering = ['create_date', 'name']
        get_latest_by = '-create_date'

    @staticmethod
    def get_config_type(type_name):
        for choice in Configuration.CONFIG_TYPE:
            if choice[1] == type_name:
                return choice[0]

        return Configuration.CONFIG_TYPE_NONE

    @classmethod
    def create(cls, name, type_id, brewpi):
        logger.debug("Create new configuration: name={}, type_id={}, brewpi={}".format(name, type_id, brewpi))

        config = cls(name=name, create_date=timezone.now(), type=type_id, brewpi=brewpi, archived=False)

        return config

    def get_temp_sensor(self):
        logger.debug("Temp Sensor: {}".format(self.temp_sensor_id))
        if self.temp_sensor_id is None:
            return None
        else:
            return api.models.Device.objects.get(pk=self.temp_sensor_id)

    def get_heat_actuator(self):
        logger.debug("Heat Actuator: {}".format(self.heat_actuator_id))
        if self.heat_actuator_id is None:
            return None
        else:
            return api.models.Device.objects.get(id=self.heat_actuator_id)

    def get_cool_actuator(self):
        logger.debug("Cool Actuator: {}".format(self.cool_actuator_id))
        if self.cool_actuator_id is None:
            return None
        else:
            return api.models.Device.objects.get(id=self.cool_actuator_id)

    def get_fan_actuator(self):
        logger.debug("Fan Actuator: {}".format(self.fan_actuator_id))
        if self.fan_actuator_id is None:
            return None
        else:
            return api.models.Device.objects.get(id=self.fan_actuator_id)

    def get_pump_1_actuator(self):
        logger.debug("Pump 1 Actuator: {}".format(self.pump_1_actuator_id))
        if self.pump_1_actuator_id is None:
            return None
        else:
            return api.models.Device.objects.get(id=self.pump_1_actuator_id)

    def get_pump_2_actuator(self):
        logger.debug("Pump 2 Actuator: {}".format(self.pump_2_actuator_id))
        if self.pump_2_actuator_id is None:
            return None
        else:
            return api.models.Device.objects.get(id=self.pump_2_actuator_id)

    def get_devices(self):
        logger.debug("Get all associated devices")
        return api.models.Device.objects.filter(configuration=self)

    def __str__(self):
        return "Configuration: [{} - {} -> {}]".format(self.name, self.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                                                       self.brewpi)
