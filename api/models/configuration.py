import api
import logging

from datetime import datetime

from django.db import models
from django.utils import timezone

from api.models import BrewPiSpark

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
    spark = models.ForeignKey(BrewPiSpark, verbose_name="Spark", null=False)
    temp_sensor_id = models.IntegerField(verbose_name='Temp Sensor', null=True)
    heat_actuator_id = models.IntegerField(verbose_name='Heat Actuator', null=True)
    cool_actuator_id = models.IntegerField(verbose_name='Cool Actuator', null=True)
    fan_actuator_id = models.IntegerField(verbose_name='Fan Actuator', null=True)

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
    def create(cls, name, type_id, spark):
        logger.debug("Create new configuration: name={}, type_id={}, spark={}".format(name, type_id, spark))

        config = cls(name=name, create_date=timezone.now(), type=type_id, spark=spark)

        return config

    def get_temp_sensor(self):
        logger.debug("Temp Sensor: {}".format(self.temp_sensor_id))
        return api.models.Device.objects.get(pk=self.temp_sensor_id)

    def get_heat_actuator(self):
        logger.debug("Heat Actuator: {}".format(self.heat_actuator_id))
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

    def get_devices(self):
        logger.debug("Get all associated devices")
        return api.models.Device.objects.filter(configuration=self)

    def __str__(self):
        return "Configuration: [{} - {} -> {}]".format(self.name, self.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                                                       self.spark)


class TemperaturePhase(models.Model):
    configuration = models.ForeignKey(Configuration, verbose_name="Configuration", related_name='phases', null=False)
    order = models.IntegerField(verbose_name="Order", null=False)
    start_date = models.DateTimeField(verbose_name="Start Date", null=False, default=datetime(1970, 1, 1))
    duration = models.IntegerField(verbose_name="Duration", null=False, default=0)
    temperature = models.FloatField(verbose_name="Temperature", null=False)
    done = models.BooleanField(verbose_name="Done", null=False, default=False)

    class Meta:
        verbose_name = 'Temperature Phase'
        verbose_name_plural = 'Temperature Phases'
        ordering = ['configuration', 'order']

    @classmethod
    def create(cls, configuration, order, start_date, duration, temperature, done):
        logger.debug(
            "Create new temp_pase: configuration={}, order={}, start_date={}, duration={}, temperature={}, done={}".
                format(configuration, order, start_date, duration, temperature, done))

        temp_phase = cls(configuration=configuration, order=order, start_date=start_date, duration=duration,
                         temperature=temperature, done=done)

        return temp_phase

    def __str__(self):
        return "TemperaturePhase: [{}; {}; {}; {}; {}]".format(self.configuration,
                                                               self.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                                                               self.duration,
                                                               self.temperature,
                                                               self.done)
