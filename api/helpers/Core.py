import logging

from django.shortcuts import get_object_or_404

from api.views.errors import Http400
from api.models import Device, BrewPi, Configuration

logger = logging.getLogger(__name__)


def check_parameter(parameter, values, field_name):
    if parameter not in values:
        message = "Provided value for '{}' is not valid".format(field_name)
        logger.info("BAD REQUEST: " + message)
        raise Http400(message)

    return None


def get_and_check_brewpi_to_device(device_id, actuator_id):
    device = get_object_or_404(Device, pk=actuator_id)
    brewpi = get_object_or_404(BrewPi, device_id=device_id)

    if device.brewpi.device_id != brewpi.device_id:
        raise Http400("Device not assigned to given BrewPi")

    return device, brewpi


def prepare_configuration_dic(configuration):
    temp_sensor = configuration.get_temp_sensor()
    heat_actuator = configuration.get_heat_actuator()
    cool_actuator = configuration.get_cool_actuator()
    fan_actuator = configuration.get_fan_actuator()

    phases = []
    for phase in configuration.phases.all():
        phases.append({
            "start_date": phase.start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "heat_pwm": phase.heat_pwm,
            "fan_pwm": phase.fan_pwm,
            "p": phase.p,
            "i": phase.i,
            "d": phase.d,
            "done": phase.done
        })

    config_dic = {
        "pk": configuration.pk,
        "name": configuration.name,
        "create_date": configuration.create_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "type": "Brew" if configuration.type == Configuration.CONFIG_TYPE_BREW else "Fermentation",
        "brewpi": configuration.brewpi.pk,
        "temp_sensor": temp_sensor.get_function_display(),
        "heat_actuator": heat_actuator.get_function_display(),
        "cool_actuator": cool_actuator.get_function_display(),
        "fan_actuator": fan_actuator.get_function_display(),
        "function": {
            device.get_function_display(): device.id for device in configuration.get_devices()
            },
        "phases": phases
    }

    return config_dic
