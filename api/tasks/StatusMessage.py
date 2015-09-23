from __future__ import absolute_import
from netifaces import interfaces, ifaddresses, AF_INET
import logging
import socket
import time

from celery import shared_task

from api.models.BrewPi import BrewPi
from api.services.BrewPiConnector import BrewPiConnector

from django.utils import timezone


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

    BrewPiConnector().send_brewpi_info(brewpi, local_ip, local_port)

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
