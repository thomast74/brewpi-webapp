import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from api.models import Device

logger = logging.getLogger(__name__)


class DeviceSerializer:

    def __init__(self):
        pass

    @staticmethod
    def from_json(brewpi, device_json):
        logger.debug("Convert json devices into Device objects")
        try:
            logger.debug("Received: " + device_json)
            device_dic = json.loads(device_json)
        except ValueError:
            return None

        try:
            if device_dic.get('device_type') == Device.DEVICE_TYPE_ONEWIRE_TEMP:
                device = Device.objects.get(pin_nr=device_dic.get('pin_nr'),
                                            hw_address=device_dic.get("hw_address"))
            else:
                device = Device.objects.get(pin_nr=device_dic.get('pin_nr'),
                                            hw_address=device_dic.get("hw_address"),
                                            brewpi=brewpi)

            device.brewpi = brewpi
            device.device_type = device_dic.get('device_type', device.device_type)
            device.function = device_dic.get('function', device.function)
            device.value = device_dic.get('value', device.value)
            device.offset_from_brewpi = device_dic.get('offset_from_brewpi', device.offset_from_brewpi)
            device.is_deactivate = device_dic.get('is_deactivate', device.is_deactivate)
            device.last_update = timezone.now()
            device.save()

            logger.debug(device.__str__())

        except ObjectDoesNotExist:
            device = Device.create(brewpi, device_dic.get('device_type'), device_dic.get('function', 0),
                                   device_dic.get('value'), device_dic.get('pin_nr'), device_dic.get('hw_address'),
                                   device_dic.get('offset_from_brewpi'), device_dic.get('is_deactivate', False))
            device.save()

            logger.debug(device.__str__())

        return device
