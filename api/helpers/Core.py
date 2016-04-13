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
    pump_1_actuator = configuration.get_pump_1_actuator()
    pump_2_actuator = configuration.get_pump_2_actuator()

    phases = []
    for phase in configuration.phases.all():
        phases.append({
            "start_date": phase.start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "temperature": phase.temperature,
            "heat_pwm": phase.heat_pwm,
            "fan_pwm": phase.fan_pwm,
            "pump_1_pwm": phase.pump_1_pwm,
            "pump_2_pwm": phase.pump_2_pwm,
            "heating_period": phase.heating_period,
            "cooling_period": phase.cooling_period,
            "cooling_on_time": phase.cooling_on_time,
            "cooling_off_time": phase.cooling_off_time,
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
        "fan_actuator": "" if fan_actuator is None else fan_actuator.get_function_display(),
        "cool_actuator": "" if cool_actuator is None else cool_actuator.get_function_display(),
        "heat_actuator": "" if heat_actuator is None else heat_actuator.get_function_display(),
        "pump_1_actuator": "" if pump_1_actuator is None else pump_1_actuator.get_function_display(),
        "pump_2_actuator": "" if pump_2_actuator is None else pump_2_actuator.get_function_display(),
        "temp_sensor": "" if temp_sensor is None else temp_sensor.get_function_display(),
        "function": {
            device.get_function_display(): device.id for device in configuration.get_devices()
            },
        "phases": phases
    }

    return config_dic
