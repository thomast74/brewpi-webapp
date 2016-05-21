import json
import logging
import time

from django.views.generic import View
from django.shortcuts import get_object_or_404

from api.helpers.Responses import ApiResponse
from api.models import Device, BrewPi, Configuration
from api.services.BrewPiConnector import BrewPiConnector
from api.tasks import SensorCalibration
from api.views.errors import Http400

logger = logging.getLogger(__name__)


class DeviceCommand(View):

    def put(self, request, *args, **kwargs):
        device_id = kwargs['device_id']
        internal_device_id = kwargs['id']
        name = request.PUT.get("name", "");

        logger.info("Change name of device on {} with id {} to name", device_id, internal_device_id, name)

        device = get_object_or_404(Device, pk=internal_device_id)

        device.name = name
        device.save

        return ApiResponse.ok()

    def post(self, request, *args, **kwargs):
        device_id = kwargs['device_id']
        command = kwargs['command']

        logger.info("Execute device command {} on BrewPi {}: {}".format(command, device_id, request.body))

        if command == "offset":
            self.send_offset(device_id)

            return ApiResponse.ok()

        elif command == "calibration":
            self.start_calibration(request, device_id)

            return ApiResponse.ok()

        return ApiResponse.bad_request("Command '{}' unknown".format(command))

    def send_offset(self, device_id):
        logger.info("Send offset to all temperature devices on BrewPi {}".format(device_id))

        brewpi = get_object_or_404(BrewPi, device_id=device_id)
        devices = Device.objects.filter(brewpi=brewpi, device_type=Device.DEVICE_TYPE_ONEWIRE_TEMP)

        all_sent = True
        for device in devices:
            if device.offset == 0.0:
                continue

            logger.info("Send offset for device {}/{}: {}".format(device.pin_nr, device.hw_address, device.offset))
            tries = 0
            success = False
            while tries < 5:
                success, response = BrewPiConnector.send_device_offset(device)
                if success:
                    break
                time.sleep(0.2)
                tries += 1

            if not success:
                logger.error("Device {}/{} offset could not be sent: [{}]".format(device.pin_nr,
                                                                                  device.hw_address,
                                                                                  response))
                all_sent = False

        return ApiResponse.ok() if all_sent else ApiResponse.bad_request("At least one device offset was not sent")

    def start_calibration(self, request, device_id):
        logger.info("Start a calibration session on BrewPi {}".format(device_id))

        brewpi = get_object_or_404(BrewPi, device_id=device_id)

        device_ids = self.get_actuator_ids(request.body)
        sensors = Device.objects.filter(pk__in=device_ids, brewpi=brewpi)

        self.check_if_calibration_is_possible(brewpi, sensors)
        self.configure_sensors_for_calibration(brewpi, sensors)
        SensorCalibration.calculate_offset.apply_async((brewpi, sensors), countdown=200)

        return ApiResponse.ok()

    def get_actuator_ids(self, json_string):
        logger.debug("Convert json actuator list into array")
        try:
            logger.debug("Received: " + json_string)
            json_dic = json.loads(json_string)

            return json_dic.get("sensors")

        except ValueError:
            raise Http400("POST does not contain a valid json string")

    def check_if_calibration_is_possible(self, brewpi, devices):
        if len(devices) == 0:
            logger.debug("No devices to calibrate")
            raise Http400("No sensors to calibrate")

        if not all(device.device_type == Device.DEVICE_TYPE_ONEWIRE_TEMP for device in devices):
            logger.debug("Not all sensors are temperature sensors")
            raise Http400("Not all sensors are temperature sensors")

        if not all(device.configuration is None for device in devices):
            logger.debug("Some temperature sensors are assigned to a configuration")
            raise Http400("Some temperature sensors are assigned to a configuration")

        configs = Configuration.objects.filter(brewpi=brewpi, name="Calibration")
        if configs.count() > 0:
            logger.debug("BrewPi already calibrates sensors")
            raise Http400("BrewPi already calibrates sensors")

    def configure_sensors_for_calibration(self, brewpi, devices):

        config = Configuration.create(name="Calibration",
                                      type_id=Configuration.CONFIG_TYPE_CALIBRATION,
                                      brewpi=brewpi)
        config.save()

        for device in devices:
            device.offset = 0
            device.offset_result = ""
            device.configuration = config

            tries = 0
            success = False
            while tries < 5:
                success, response = BrewPiConnector.send_device_offset(device)
                if success:
                    break
                time.sleep(0.2)
                tries += 1

            if not success:
                logger.error("Device {}/{} offset could not be sent: [{}]".format(device.pin_nr,
                                                                                  device.hw_address,
                                                                                  response))

            device.save()
