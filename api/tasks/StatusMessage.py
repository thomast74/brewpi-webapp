from __future__ import absolute_import

import logging
import socket
import time

from celery import shared_task

from api.models import Device
from api.models.BrewPi import BrewPi
from api.services.BrewPiConnector import BrewPiConnector

from django.utils import timezone

from netifaces import interfaces, ifaddresses, AF_INET


logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def check_if_status_update_required(device_id, local_port):
    logger.debug("Received status message check task for {}".format(device_id))

    brewpi = BrewPi.objects.get(device_id=device_id)
    local_ip = get_local_ip()
    datetime = int(time.mktime(timezone.now().timetuple()))

    logger.debug("BrewPi Web Address: {}   Local Ip: {}".format(brewpi.web_address, local_ip))
    logger.debug("BrewPi Web Port: {}   Local Port: {}".format(brewpi.web_port, local_port))
    logger.debug("BrewPi Time: {}   localtime: {}".format(brewpi.brewpi_time, datetime))

    tries = 0
    success = False
    while tries < 5:
        success, response = BrewPiConnector().send_brewpi_info(brewpi, local_ip, local_port)
        if success:
            break
        time.sleep(0.2)
        tries += 1

    if success:
        send_offset.apply_async(args=[brewpi], countdown=20)
    else:
        logger.error("BrewPi info could not be send to BrewPi {}: [{}]".format(device_id, response))

    return "Ok"


@shared_task(ignore_result=True)
def send_offset(brewpi):

    devices = Device.objects.filter(brewpi=brewpi, device_type=Device.DEVICE_TYPE_ONEWIRE_TEMP)

    for device in devices:
        if device.offset == 0.0:
            continue

        logger.info("Send offset for device {}/{}: {}".format(device.pin_nr, device.hw_address, device.offset))
        tries = 0
        success = False
        while tries < 5:
            success, response = BrewPiConnector().send_device_offset(device)
            if success:
                break
            time.sleep(0.2)
            tries += 1

        if not success:
            logger.error("Device {}/{} offset could not be sent: [{}]".format(device.pin_nr,
                                                                              device.hw_address,
                                                                              response))

    return "Ok"


def get_local_ip():
    for interface in interfaces():
        if interface.startswith("eth") or interface.startswith("wlan"):
            try:
                for link in ifaddresses(interface)[AF_INET]:
                    logger.debug("local_ip: {} -> {}".format(interface, link['addr']))
                    return link['addr']
            except:
                logger.debug("Interface {} has no ip address".format(interface))

    return socket.gethostbyname(socket.gethostname())
