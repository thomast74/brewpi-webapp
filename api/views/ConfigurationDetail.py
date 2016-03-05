import json
import logging
import sys

from django.db import transaction
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.utils import timezone

from api.helpers.Core import prepare_configuration_dic
from api.helpers.Responses import ApiResponse
from api.models import BrewPi, Configuration, Device, Phase
from api.services.BrewPiConnector import BrewPiConnector
from api.views.errors import Http400

logger = logging.getLogger(__name__)


class ConfigurationDetail(View):

    def get(self, request, *args, **kwargs):
        device_id = kwargs['device_id']
        config_id = kwargs['config_id']
        pretty = request.GET.get("pretty", "True")

        logger.info("Get all configurations for BrewPi {}".format(device_id))

        brewpi = get_object_or_404(BrewPi, device_id=device_id)
        configuration = get_object_or_404(Configuration, pk=config_id, brewpi=brewpi)

        config_dic = prepare_configuration_dic(configuration)

        return ApiResponse.json(config_dic, pretty, False)

    @transaction.non_atomic_requests
    def put(self, request, *args, **kwargs):
        device_id = kwargs['device_id']
        config_id = kwargs['config_id']
        logger.info("Update configuration {} received for BrewPi {}".format(config_id, device_id))

        brewpi = get_object_or_404(BrewPi, device_id=device_id)
        configuration = get_object_or_404(Configuration, pk=config_id)

        config_dic = ConfigurationDetail.convert_json_data(request.body)

        try:
            name = config_dic.get("name")
            if "name" not in config_dic or len(name) == 0:
                raise Http400("A name must be given")
            configuration.name = name

            ConfigurationDetail.assign_device_function(brewpi, configuration, config_dic, True)
            configuration.temp_sensor_id = ConfigurationDetail.get_sensor_or_actuator("temp_sensor", False,
                                                                                      configuration, config_dic)
            configuration.heat_actuator_id = ConfigurationDetail.get_sensor_or_actuator("heat_actuator", False,
                                                                                        configuration, config_dic)

            if configuration.type == Configuration.CONFIG_TYPE_FERMENTATION:
                configuration.fan_actuator_id = ConfigurationDetail.get_sensor_or_actuator("fan_actuator", False,
                                                                                           configuration, config_dic)
                configuration.cool_actuator_id = ConfigurationDetail.get_sensor_or_actuator("cool_actuator", False,
                                                                                            configuration, config_dic)
            else:
                configuration.fan_actuator_id = None
                configuration.cool_actuator_id = None

            configuration.save()
            ConfigurationDetail.store_phase(configuration, config_dic.get("phase"))

            tries = 0
            success = False
            while tries < 5:
                success = BrewPiConnector.send_configuration(brewpi, configuration)
                if success:
                    break
                tries += 1

            if success:
                transaction.commit()
                return ApiResponse.message('"ConfigId":"{}"'.format(configuration.pk))
            else:
                transaction.rollback()
                return ApiResponse.bad_request("BrewPi could not be updated")
        except:
            transaction.rollback()
            return ApiResponse.bad_request(sys.exc_info()[1])

    def delete(self, request, *args, **kwargs):
        device_id = kwargs['device_id']
        config_id = kwargs['config_id']

        logger.info("Received delete configuration {} request".format(config_id))

        success = self.delete_configuration(device_id, config_id)

        if success:
            return ApiResponse.ok()
        else:
            return ApiResponse.bad_request("Could not delete configuration {} from BrewPi {}".format(config_id,
                                                                                                     device_id))

    @staticmethod
    def delete_configuration(device_id, config_id):

        brewpi = get_object_or_404(BrewPi, device_id=device_id)
        configuration = get_object_or_404(Configuration, pk=config_id)

        tries = 0
        success = False
        while tries < 5:
            success = BrewPiConnector.delete_configuration(brewpi, configuration)
            if success:
                break

        if success:
            Device.objects.filter(configuration=configuration).update(configuration=None, function=0)
            configuration.delete()

        return success

    @staticmethod
    def convert_json_data(json_data):
        try:
            return json.loads(json_data)

        except ValueError:
            return None

    @staticmethod
    def create_configuration(brewpi, config_dic):
        name = config_dic.get("name")
        if "name" not in config_dic or len(name) == 0:
            raise Http400("A name must be given")

        config_type = Configuration.get_config_type(config_dic.get("type"))
        if "type" not in config_dic or config_type == Configuration.CONFIG_TYPE_NONE:
            raise Http400("Type must be given and must be either Brew or Fermentation")

        config = Configuration.create(config_dic.get("name"), config_type, brewpi)
        config.save()

        return config

    @staticmethod
    def assign_device_function(brewpi, config, config_dic, is_update):
        logger.debug("Assign device functions")

        function_dic = config_dic.get("function")

        for function in function_dic:
            device_id = function_dic.get(function)
            device = get_object_or_404(Device, pk=device_id)
            if device.brewpi != brewpi:
                raise Http400("Device {}:{} does not belong to provided BrewPi {}".format(function, device_id, brewpi))

            if not is_update and device.configuration is not None:
                raise Http400("Device {}:{} is already assigned to configuration {}".format(function, device_id,
                                                                                            device.configuration))

            function_id = Device.get_function(function)
            if function_id == Device.DEVICE_FUNCTION_NONE:
                raise Http400("Device {}:{} is assigned to an unknown function".format(function, device_id))

            if Device.objects.filter(configuration=config, function=function_id).exclude(pk=device_id).exists():
                raise Http400(
                    "Device {}:{} can't be assigned to function because configuration already has such a device".format(
                        function, device_id))

            device.configuration = config
            device.function = function_id
            device.save()

    @staticmethod
    def get_sensor_or_actuator(name, temp_sensor, config, config_dic):
        logger.debug("Set {} Sensor/Actuator".format(name))

        temp_sensor_function = Device.get_function(config_dic.get(name))
        if temp_sensor_function == Device.DEVICE_FUNCTION_NONE:
            raise Http400("Sensor/Actuator {} can't be found".format(temp_sensor_function))

        device = get_object_or_404(Device, configuration=config, function=temp_sensor_function)
        if temp_sensor and device.device_type != Device.DEVICE_TYPE_ONEWIRE_TEMP:
            raise Http400("Sensor {} must be a temperature sensor".format(temp_sensor_function))

        return device.id

    @staticmethod
    def store_phase(configuration, phase_dic):
        """
          "phase": {
            "temperature": ,
            "heat_pwm": ,
            "fan_pwm": ,
            "heating_period": ,
            "cooling_on_period": ,
            "cooling_off_period": ,
            "p": ,
            "i": ,
            "d":
          }
        """
        Phase.objects.filter(configuration=configuration, done=False).update(done=True)

        temperature = phase_dic.get("temperature", 0)
        heat_pwm = phase_dic("heat_pwm", 0)

        if temperature <= 0 and heat_pwm <= 0:
            raise Http400("Either a temperature or heat PWM value need to be provided")

        if temperature == 0 and (heat_pwm < 0 or heat_pwm > 100):
            raise Http400("Heat PWM must be between 0 and 100")

        phase = Phase.create(configuration, timezone.now(), temperature, heat_pwm, phase_dic.get("fan_pwm", 200),
                             phase_dic.get("heating_period", 4000), phase_dic.get("cooling_on_period", 600000),
                             phase_dic.get("cooling_off_period", 180000), phase_dic.get("p", 0),
                             phase_dic.get("i", 0), phase_dic.get("d", 0), False)
        phase.save()
