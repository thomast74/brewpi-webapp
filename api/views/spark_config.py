from datetime import datetime
import dateutil
import json
import logging

from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from django.views.decorators.http import require_http_methods
from api.helpers import ApiResponse

from api.models import BrewPiSpark, Configuration, Device, TemperaturePhase
from api.services.spark_connector import SparkConnector
from api.views.errors import Http400


logger = logging.getLogger(__name__)


@require_http_methods(["PUT"])
def create(request, device_id):
    logger.info("New configuration received for spark {}".format(device_id))

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)
    config_dic = convert_json_data(request.body)

    configuration = create_configuration(spark, config_dic)

    assign_device_function(spark, configuration, config_dic)

    set_temp_sensor(configuration, config_dic)
    set_heat_actuator(configuration, config_dic)
    configuration.save()

    store_temp_phases(configuration, config_dic.get("temp_phases"))

    SparkConnector.send_config(spark, configuration)

    return HttpResponse('{{"Status":"OK","ConfigId":"{}"}}\n'.format(configuration.id),
                        content_type="application/json")


@require_http_methods(["POST"])
def update(request, config_id):
    return HttpResponse('{{"Status":"OK","ConfigId":"{}"}}\n'.format(config_id),
                        content_type="application/json")


@require_http_methods(["DELETE"])
def delete(request, device_id, config_id):
    logger.info("Delete configuration {}".format(config_id))

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)
    configuration = get_object_or_404(Configuration, pk=config_id)

    #SparkConnector.delete_config(spark, configuration)

    Device.objects.filter(configuration=configuration).update(configuration=None,function=0)
    configuration.delete()

    return ApiResponse.ok()


def convert_json_data(json_data):
    try:
        return json.loads(json_data)

    except ValueError:
        return None


def create_configuration(spark, config_dic):
    name = config_dic.get("name")
    if "name" not in config_dic or len(name) == 0:
        raise Http400("A name must be given")

    config_type = Configuration.get_config_type(config_dic.get("type"))
    if "type" not in config_dic or config_type == Configuration.CONFIG_TYPE_NONE:
        raise Http400("Type must be given and can be either Brew or Fermentation")

    config = Configuration.create(config_dic.get("name"), config_type, spark)
    config.save()

    return config


def assign_device_function(spark, config, config_dic):
    logger.debug("Assign device functions")

    function_dic = config_dic.get("function")

    for function in function_dic:
        device_id = function_dic.get(function)
        device = get_object_or_404(Device, pk=device_id)
        if device.spark != spark:
            raise Http400("Device {}:{} does not belong to provided Spark".format(function, device_id, spark))

        if device.configuration is not None:
            raise Http400("Device {}:{} is already assigned to a configuration {}".format(function, device_id,
                                                                                          device.configuration))

        function_id = Device.get_function(function)
        if function_id == Device.DEVICE_FUNCTION_NONE:
            raise Http400("Device {}:{} is assigned to an unkown function".format(function, device_id))

        if Device.objects.filter(configuration=config, function=function_id).exclude(pk=device_id).exists():
            raise Http400(
                "Device {}:{} can't be assigned to function because configuration already has such a device".format(
                    function, device_id))

        device.configuration = config
        device.function = function_id
        device.save()


def set_temp_sensor(config, config_dic):
    logger.debug("Set Temp Sensor")

    temp_sensor_function = Device.get_function(config_dic.get("temp_sensor"))
    if temp_sensor_function == Device.DEVICE_FUNCTION_NONE:
        raise Http400("Temp Sensor {} can't be found".format(temp_sensor_function))

    device = get_object_or_404(Device, configuration=config, function=temp_sensor_function)
    if device.device_type != Device.DEVICE_TYPE_ONEWIRE_TEMP:
        raise Http400("Temp Sensor {} must be a temperature sensor".format(temp_sensor_function))

    config.temp_sensor_id = device.id


def set_heat_actuator(config, config_dic):
    logger.debug("Set Heat Actuator")

    heat_actuator_function = Device.get_function(config_dic.get("heat_actuator"))
    if heat_actuator_function == Device.DEVICE_FUNCTION_NONE:
        raise Http400("Heat actuator {} can't be found".format(heat_actuator_function))

    device = get_object_or_404(Device, configuration=config, function=heat_actuator_function)
    if device.device_type != Device.DEVICE_TYPE_ACTUATOR_PIN and device.device_type != Device.DEVICE_TYPE_ACTUATOR_PWM:
        raise Http400("Heat actuator {} must be a Pin or PWM Actuator".format(heat_actuator_function))

    config.heat_actuator_id = device.id


def store_temp_phases(config, temp_phases_arr):
    logger.debug("Store temp phases")

    order = 1
    previous_start_date = datetime.now()
    previous_temperature = 0
    previous_done = True

    for temp_phase_dic in temp_phases_arr:
        if config.type == Configuration.CONFIG_TYPE_BREW:
            start_date = datetime.fromordinal(1)
            duration = temp_phase_dic.get("duration")

            if duration <= 0:
                raise Http400("A Brew Configuration needs to have a duration")

            if previous_temperature > temperature:
                raise Http400("A Brew Configuration needs a raising temperature")

        elif config.type == Configuration.CONFIG_TYPE_FERMENTATION:
            start_date = dateutil.parser.parse(temp_phase_dic.get("start_date"))
            duration = 0

            if start_date <= datetime.now():
                raise Http400("A Fermentation Configuration needs to have a start date in the future")

            if start_date <= previous_start_date:
                raise Http400("A Fermentation Configuration phase needs to have a start date later than previous one")

        else:
            raise Http400("Invalid configuration type")

        temperature = temp_phase_dic.get("temperature")
        done = temp_phase_dic.get("done")

        if not previous_done and done:
            raise Http400("A Configuration can't set a later phase as done")


        temp_phase = TemperaturePhase.create(config, order, start_date, duration, temperature, done)
        temp_phase.save()

        previous_start_date = start_date
        previous_temperature = temperature
        previous_done = done
        order += 1

