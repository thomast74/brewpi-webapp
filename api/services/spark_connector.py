from django.conf import settings

import logging
import socket

logger = logging.getLogger(__name__)


def send_device_info(spark, local_ip):

    logger.info("Send device info [name:{},config:{},tempType:{}] to {}".format(spark.name, spark.device_config, settings.TEMP_TYPE, spark))
    sock = start_connection(spark.ip_address)

    try:
        message = "d{{name:{},config:{},tempType:{},oinkweb:{}}}".format(spark.name, spark.device_config, settings.TEMP_TYPE, local_ip)
        logger.debug("Send data: {}".format(message))
        sock.sendall(message)
        data = sock.recv(1024)
        logger.info("Response: {}".format(data))
    finally:
        sock.close()
    return


def reset_device(spark):
    logger.info("Reset spark {}".format(spark))
    sock = start_connection(spark.ip_address)

    try:
        logger.debug("{} Message: r".format(spark.name))
        sock.sendall("r")
        data = sock.recv(1024)
        logger.info("Response: {}".format(data))
    finally:
        sock.close()
    return


def set_mode(spark, device_mode):
    logger.info("Change mode for {} to {}".format(spark, device_mode))
    sock = start_connection(spark.ip_address)

    try:
        message = "m{{mode:{}}}".format(device_mode);

        logger.debug("{} Message: {}".format(spark.name, message))
        sock.sendall(message)
        data = sock.recv(1024)
        logger.info("Response: {}".format(data))
    finally:
        sock.close()
    return


def start_connection(ip_address):
    logger.debug("Start connection to spark")
    logger.debug("Create socket for: {}:{}".format(str(ip_address), int(settings.SPARK_PORT)))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (str(ip_address), int(settings.SPARK_PORT))

    logger.debug("Socket connect")
    sock.connect(server_address)

    return sock
