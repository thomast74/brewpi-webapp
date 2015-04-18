from __future__ import absolute_import
from netifaces import interfaces, ifaddresses, AF_INET
import logging
import socket
import time

from celery import shared_task

from api.models.brew_pi_spark import BrewPiSpark
from api.services.spark_connector import Connector

from django.utils import timezone


logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def check_if_status_update_required(device_id, local_port):
    logger.debug("Received status message check task for {}".format(device_id))

    spark = BrewPiSpark.objects.get(device_id=device_id)
    local_ip = get_local_ip()
    datetime = int(time.mktime(timezone.now().timetuple()))

    logger.debug("Spark Web Address: {}   Local Ip: {}".format(spark.web_address, local_ip))
    logger.debug("Spark Web Port: {}   Local Port: {}".format(spark.web_port, local_port))
    logger.debug("Spark Time: {}   localtime: {}".format(spark.spark_time, datetime))

    if spark.web_address != local_ip or spark.web_port != int(local_port) or \
                    spark.spark_time < (datetime - 10) or spark.spark_time > datetime:
        Connector().send_spark_info(spark, local_ip, local_port)

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