from datetime import datetime
import dateutil
import json
import logging

from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse
from django.utils.timezone import utc

from django.views.decorators.http import require_http_methods
from api.helpers import ApiResponse

from api.models import BrewPiSpark, Configuration, Device, TemperaturePhase
from api.services.spark_connector import SparkConnector
from api.tasks import logs_phase
from api.views.errors import Http400


logger = logging.getLogger(__name__)

def list_or_create(request, device_id):
    if request.method == 'PUT':
        return create(request, device_id)
    else:
        return list_configs(request, device_id)


def get_or_update(request, device_id, config_id):
    if request.method == 'POST':
        return update(request, device_id, config_id)
    else:
        return get_config(request, device_id, config_id)


def list_configs(request, device_id):
    logger.info("Get configurations for spark {}".format(device_id))
    pretty = request.GET.get("pretty", "True")

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)
    configurations = get_list_or_404(Configuration, spark=spark)

    configs_arr = []
    for configuration in configurations:
        configs_arr.append(prepare_config_dic(configuration))

    return ApiResponse.json(configs_arr, pretty, False)


def get_config(request, device_id, config_id):
    logger.info("Get configuration for spark {} and configuration id {}".format(device_id, config_id))
    pretty = request.GET.get("pretty", "True")

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)
    configuration = get_object_or_404(Configuration, id=config_id, spark=spark)

    config_dic = prepare_config_dic(configuration)

    return ApiResponse.json(config_dic, pretty, False)


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

    tries = 0
    success = False
    while tries < 5:
        success = SparkConnector.send_config(spark, configuration)
        if success:
            break
        tries += 1

    if success:
        return HttpResponse('{{"Status":"OK","ConfigId":"{}"}}\n'.format(configuration.id),
                            content_type="application/json")
    else:
        delete(None, device_id, configuration.pk)
        return HttpResponse('{{"Status":"Error","Message":"Spark could not be updated, try again."}}\n',
                            content_type="application/json")



def update(request, device_id, config_id):

    # allow name change
    # allow temp_sensor change
    # allow heat_actuator change
    # allow function change, fail if temp_sensor or heat_actuator is not part of function
    # allow temp_phases change

    return HttpResponse('{{"Status":"OK","ConfigId":"{}"}}\n'.format(config_id),
                        content_type="application/json")


@require_http_methods(["DELETE"])
def delete(request, device_id, config_id):
    logger.info("Delete configuration {}".format(config_id))

    spark = get_object_or_404(BrewPiSpark, device_id=device_id)
    configuration = get_object_or_404(Configuration, pk=config_id)

    tries = 0
    success = False
    while tries < 5:
        success = SparkConnector.delete_config(spark, configuration)
        if success:
            break
        tries += 1

    if success:
        Device.objects.filter(configuration=configuration).update(configuration=None,function=0)
        configuration.delete()
        return ApiResponse.ok()

    else:
        return ApiResponse.bad_request("Spark could not be updated, try again.")


@require_http_methods(["POST"])
def update_phase(request, device_id, config_id):
    logger.info("Log phase report to database")

    logs_phase.log_phase_data.delay(device_id, config_id, request.body)

    return ApiResponse.ok()


def convert_json_data(json_data):
    try:
        return json.loads(json_data)

    except ValueError:
        return None


def prepare_config_dic(configuration):
    temp_sensor = configuration.get_temp_sensor()
    heat_actuator = configuration.get_heat_actuator()

    temp_phases = []
    for phase in configuration.phases.all():
        temp_phases.append({
            "start_date": phase.start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "duration": phase.duration,
            "temperature": phase.temperature,
            "done": phase.done
        })

    config_dic = {
        "name": configuration.name,
        "type": "Brew" if configuration.type == Configuration.CONFIG_TYPE_BREW else "Fermentation",
        "temp_sensor": temp_sensor.get_function_display(),
        "heat_actuator": heat_actuator.get_function_display(),
        "function": {
            device.get_function_display(): device.id for device in configuration.get_devices()
        },
        "temp_phases": temp_phases
    }

    return config_dic


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

        duration = 0
        temperature = temp_phase_dic.get("temperature")
        done = temp_phase_dic.get("done")

        if config.type == Configuration.CONFIG_TYPE_BREW:
            start_date = datetime.fromtimestamp(0).replace(tzinfo=utc)
            duration = temp_phase_dic.get("duration")

            if duration <= 0:
                raise Http400("A Brew Configuration needs to have a duration")

            if previous_temperature > temperature:
                raise Http400("A Brew Configuration needs a raising temperature")

        elif config.type == Configuration.CONFIG_TYPE_FERMENTATION:
            # I think it needs to be converted into UTC
            start_date = dateutil.parser.parse(temp_phase_dic.get("start_date"))
            duration = 0

            # here it needs to be compared to UTC.Now
            if start_date <= datetime.now():
                raise Http400("A Fermentation Configuration needs to have a start date in the future")

            if start_date <= previous_start_date:
                raise Http400("A Fermentation Configuration phase needs to have a start date later than previous one")

        else:
            raise Http400("Invalid configuration type")

        if not previous_done and done:
            raise Http400("A Configuration can't set a later phase as done")

        temp_phase = TemperaturePhase.create(config, order, start_date, duration, temperature, done)
        temp_phase.save()

        previous_start_date = start_date
        previous_temperature = temperature
        previous_done = done
        order += 1

