from django.conf import settings

import logging
import os
import socket
import time


logger = logging.getLogger(__name__)


class Connector:
    def send_device_info(self, spark, local_ip):

        logger.info("Send device info [name:{},config:{},tempType:{}] to {}".format(spark.name, spark.device_config,
                                                                                    settings.TEMP_TYPE, spark))
        sock = self.__start_connection(spark.ip_address)

        try:
            message = "d{{name:{},config:{},tempType:{},oinkweb:{}}}".format(spark.name, spark.device_config,
                                                                             settings.TEMP_TYPE, local_ip)
            logger.debug("Send data: {}".format(message))
            sock.sendall(message)
            data = sock.recv(1024)
            logger.info("Response: {}".format(data))
        finally:
            sock.close()
        return


    def reset_device(self, spark):
        logger.info("Reset spark {}".format(spark))
        sock = self.__start_connection(spark.ip_address)

        try:
            logger.debug("{} Message: r".format(spark.name))
            sock.sendall("r")
            data = sock.recv(1024)
            logger.info("Response: {}".format(data))
        finally:
            sock.close()
        return


    def set_name(self, spark, name):
        logger.info("Change name for {} to {}".format(spark, name))
        sock = self.__start_connection(spark.ip_address)

        try:
            message = "d{{name:{}}}".format(name)
            logger.debug("Send data: {}".format(message))
            sock.sendall(message)
            data = sock.recv(1024)
            logger.info("Response: {}".format(data))
        finally:
            sock.close()
        return


    def set_mode(self, spark, device_mode):
        logger.info("Change mode for {} to {}".format(spark, device_mode))
        sock = self.__start_connection(spark.ip_address)

        try:
            message = "m{{mode:{}}}".format(device_mode);

            logger.debug("{} Message: {}".format(spark.name, message))
            sock.sendall(message)
            data = sock.recv(1024)
            logger.info("Response: {}".format(data))
        finally:
            sock.close()
        return


    def update_firmware(self, spark):
        logger.info("Update firmware on {}".format(spark))
        sock = self.__start_connection(spark.ip_address)

        try:
            with open('/home/thomast74/Projects/oinkbrew_firmware/target/oinkbrew.bin', 'rb') as file:
                logger.debug("Send Message")
                sock.send("f{}")

                response = sock.recv(1)
                logger.debug("Response: {}".format(response))

                if response == "!":
                    logger.debug("Now lets send the file")
                    response = ""
                    totalsent = 0
                    data = file.read(4096)
                    while len(data):
                        i = sock.send(data)
                        totalsent = totalsent + i
                        response = sock.recv(1)
                        logger.debug("Response: {} -> {}".format(response, totalsent))

                        if response == "!":
                            data = file.read(4096)
                            time.sleep(0.2)
                        else:
                            data = ""

                    file.close()

        finally:
            sock.close()
        return


    def __start_connection(self, ip_address):
        logger.debug("Start connection to spark")
        logger.debug("Create socket for: {}:{}".format(str(ip_address), int(settings.SPARK_PORT)))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)

        logger.debug("Socket connecting")
        server_address = (str(ip_address), int(settings.SPARK_PORT))
        sock.connect(server_address)

        return sock
