from django.db import models
from api.models import BrewPiSpark


class Configuration(models.Model):

    CONFIG_TYPE_NONE = 0
    CONFIG_TYPE_BREW = 1
    CONFIG_TYPE_FERMENTATION = 2

    CONFIG_TYPE = (
        (CONFIG_TYPE_NONE, 'None'),
        (CONFIG_TYPE_BREW, 'Brew'),
        (CONFIG_TYPE_FERMENTATION, 'Fermentation'),
    )

    name = models.CharField(verbose_name="Name", max_length=30, unique=True)
    create_date = models.DateTimeField(verbose_name='Create Date', editable=False)
    type = models.IntegerField(verbose_name='Configuration Type', choices=CONFIG_TYPE)
    spark = models.ForeignKey(BrewPiSpark, null=True)

    # TODO Add Target Temperature with phases with an end date time
    # TODO Add ruling temp sensor
    # TODO Add acting actuator for heat
    # TODO Add acting actuator for cool

    class Meta:
        verbose_name = 'Configuration'
        verbose_name_plural = 'Configurations'
        ordering = ['create_date', 'name']
        get_latest_by = '-create_date'

    def __str__(self):
        return "Configuration: [{} - {} -> {}]".format(self.name, self.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                                                       self.spark)