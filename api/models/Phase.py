import logging

from django.db import models

from api.models import Configuration

logger = logging.getLogger(__name__)


class Phase(models.Model):
    configuration = models.ForeignKey(Configuration, verbose_name="Configuration", related_name='phases', null=False)
    start_date = models.DateTimeField(verbose_name="Start Date", null=False)
    temperature = models.FloatField(verbose_name="Temperature", null=False)
    heat_pwm = models.FloatField(verbose_name="Heat PWM", null=False)
    fan_pwm = models.FloatField(verbose_name="Fan PWM", null=False)
    p = models.FloatField(verbose_name="P", null=False)
    i = models.FloatField(verbose_name="I", null=False)
    d = models.FloatField(verbose_name="D", null=False)
    done = models.BooleanField(verbose_name="Done", null=False, default=False)

    class Meta:
        verbose_name = 'Phase'
        verbose_name_plural = 'Phases'
        ordering = ['configuration', 'start_date']

    @classmethod
    def create(cls, configuration, start_date, temperature, heat_pwm, fan_pwm, p, i, d, done):
        logger.debug(
            "Create new Phase: configuration={}, start_date={}, temperature={}, heat_pwm={}, fan_pwm={}, "
            "p={}, i={}, d={}, done={}".format(configuration,
                                               start_date,
                                               temperature,
                                               heat_pwm,
                                               fan_pwm,
                                               p, i, d,
                                               done))

        temp_phase = cls(configuration=configuration, start_date=start_date, temperature=temperature, heat_pwm=heat_pwm,
                         fan_pwm=fan_pwm, p=p, i=i, d=d, done=done)

        return temp_phase

    def __str__(self):
        return "Phase: [{}; {}; {}; {}; {}; {}; {}; {}; {}]".format(self.configuration,
                                                                    self.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                                                                    self.temperature,
                                                                    self.heat_pwm,
                                                                    self.fan_pwm,
                                                                    self.p,
                                                                    self.i,
                                                                    self.d,
                                                                    self.done)
