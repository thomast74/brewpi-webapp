from _socket import SHUT_RDWR
import logging
import socket
import time

from django.conf import settings
from django.utils import timezone


logger = logging.getLogger(__name__)


class SparkConnector:
    def __init__(self):
        return

    @staticmethod
    def send_spark_info(spark, local_ip, local_port):
        datetime = int(time.mktime(timezone.now().timetuple()))
        logger.info(
            "Send device info [name:{},tempType:{},oinkweb:{},oinkwebport:{},datetime:{}] to {}".format(spark.name,
                                                                                                        settings.TEMP_TYPE,
                                                                                                        local_ip,
                                                                                                        local_port,
                                                                                                        datetime,
                                                                                                        spark))
        try:
            sock = SparkConnector.__start_connection(spark.ip_address)
        except:
            logger.error("Connection to Spark not possible")
            raise SparkException("Connection to Spark not possible")

        try:
            message = "s{{name:{},tempType:{},oinkweb:{},oinkwebport:{},datetime:{}}}".format(spark.name,
                                                                                              settings.TEMP_TYPE,
                                                                                              local_ip, local_port,
                                                                                              datetime)
            logger.debug("Send data: {}".format(message))
            sock.sendall(message)
            data = sock.recv(1024)
            logger.info("Response: {}".format(data))
        except socket.timeout:
            raise SparkException("Connection to Spark times out")
        finally:
            sock.shutdown(SHUT_RDWR)
            sock.close()
        return

    @staticmethod
    def reset_spark(spark):
        logger.info("Reset spark {}".format(spark))

        try:
            sock = SparkConnector.__start_connection(spark.ip_address)
        except:
            logger.error("Connection to Spark not possible")
            raise SparkException("Connection to Spark not possible")

        try:
            logger.debug("{} Message: r".format(spark.name))
            sock.sendall("r")
            data = sock.recv(1024)
            logger.info("Response: {}".format(data))
        except socket.timeout:
            raise SparkException("Connection to Spark times out")
        finally:
            sock.close()
        return

    @staticmethod
    def set_spark_name(spark, name):
        logger.info("Change name for {} to {}".format(spark, name))

        try:
            sock = SparkConnector.__start_connection(spark.ip_address)
        except:
            logger.error("Connection to Spark not possible")
            raise SparkException("Connection to Spark not possible")

        try:
            message = "s{{name:{}}}".format(name)
            logger.debug("Send data: {}".format(message))
            sock.sendall(message)
            data = sock.recv(1024)
            logger.info("Response: {}".format(data))
        except socket.timeout:
            raise SparkException("Connection to Spark times out")
        finally:
            sock.close()
        return

    @staticmethod
    def set_spark_mode(spark, device_mode):
        logger.info("Change mode for {} to {}".format(spark, device_mode))

        try:
            sock = SparkConnector.__start_connection(spark.ip_address)
        except:
            logger.error("Connection to Spark not possible")
            raise SparkException("Connection to Spark not possible")

        try:
            message = "m{{mode:{}}}".format(device_mode)

            logger.debug("{} Message: {}".format(spark.name, message))
            sock.sendall(message)
            data = sock.recv(1024)
            logger.info("Response: {}".format(data))
        except socket.timeout:
            raise SparkException("Connection to Spark times out")
        finally:
            sock.close()
        return

    @staticmethod
    def request_device_list(spark):
        logger.info("Request a list of all devices available on {}".format(spark))

        try:
            sock = SparkConnector.__start_connection(spark.ip_address)
        except:
            logger.error("Connection to Spark not possible")
            raise SparkException("Connection to Spark not possible")

        try:
            logger.debug("{} Message: d".format(spark.name))
            sock.sendall("d")

            response = SparkConnector.receive_devices_json(sock)
        except socket.timeout:
            raise SparkException("Connection to Spark times out")

        return response

    @staticmethod
    def request_device(device):
        logger.info("Request device {} from {}".format(device.pk, device.spark))

        try:
            sock = SparkConnector.__start_connection(device.spark.ip_address)
        except:
            logger.error("Connection to Spark not possible")
            raise SparkException("Connection to Spark not possible")

        try:
            message = "a{{pin_nr:{},hw_address:{},is_invert:{}}}".format(device.pin_nr, device.hw_address,
                                                                         "1" if device.is_invert else "0")
            logger.debug("Send Message: " + message)
            sock.sendall(message)
        except socket.timeout:
            raise SparkException("Connection to Spark times out")

        return SparkConnector.receive_devices_json(sock)

    @staticmethod
    def update_spark_firmware(spark):
        logger.info("Update firmware on {}".format(spark))

        try:
            sock = SparkConnector.__start_connection(spark.ip_address)
        except:
            logger.error("Connection to Spark not possible")
            raise SparkException("Connection to Spark not possible")

        try:
            with open('/home/thomast74/Projects/oinkbrew_firmware/target/oinkbrew.bin', 'rb') as firmware_file:
                logger.debug("Send Message")
                sock.send("f{}")

                response = sock.recv(1)
                logger.debug("Response: {}".format(response))

                if response == "!":
                    logger.debug("Now lets send the file")
                    total_sent = 0
                    data = firmware_file.read(4096)
                    while len(data):
                        i = sock.send(data)
                        total_sent += i
                        response = sock.recv(1)
                        logger.debug("Response: {} -> {}".format(response, total_sent))

                        if response == "!":
                            data = firmware_file.read(4096)
                            time.sleep(0.2)
                        else:
                            data = ""

                    firmware_file.close()
        except socket.timeout:
            raise SparkException("Connection to Spark times out")
        finally:
            sock.close()
        return

    @staticmethod
    def device_toggle(device, value):
        logger.info("Toggle actuator on spark {} at pin {}".format(device.spark, device.pin_nr))

        response = "Error"

        try:
            sock = SparkConnector.__start_connection(device.spark.ip_address)
        except:
            logger.error("Connection to Spark not possible")
            raise SparkException("Connection to Spark not possible")

        try:
            message = "t{{pin_nr:{},is_invert:{},value:{}}}".format(device.pin_nr, "1" if device.is_invert else "0",
                                                                    value)
            logger.debug("Send Message: " + message)
            sock.send(message)

            i = 0
            expected_result = False

            while not expected_result and i < 10:
                time.sleep(0.1)
                response = sock.recv(128)

                if response != "":
                    expected_result = True

                i += 1
        except socket.timeout:
            raise SparkException("Connection to Spark times out")
        finally:
            sock.close()

        logger.info("Response: {}".format(response))

        return response

    @staticmethod
    def set_device_offset(device):
        logger.info("Set device offset on spark {} for device {}".format(device.spark, device))

        try:
            sock = SparkConnector.__start_connection(device.spark.ip_address)
        except:
            logger.error("Connection to Spark not possible")
            raise SparkException("Connection to Spark not possible")

        try:
            message = "o{{pin_nr:{},hw_address:{},offset:{}}}".format(device.pin_nr, device.hw_address,
                                                                      device.offset * 10000)
            logger.debug("Send Message: " + message)
            sock.send(message)
            sock.recv(1)
        except socket.timeout:
            raise SparkException("Connection to Spark times out")
        finally:
            sock.close()

    @staticmethod
    def device_delete(device):
        logger.info("Delete device on spark {} at pin_nr {} and hw_address".format(device.spark, device.pin_nr,
                                                                                   device.hw_address))

        response = "Error"

        try:
            sock = SparkConnector.__start_connection(device.spark.ip_address)
        except:
            logger.error("Connection to Spark not possible")
            raise SparkException("Connection to Spark not possible")

        try:
            message = "e{{pin_nr:{},hw_address:{}}}".format(device.pin_nr, device.hw_address)
            logger.debug("Send Message: " + message)
            sock.send(message)

            i = 0
            expected_result = False

            while not expected_result and i < 10:
                time.sleep(0.1)
                response = sock.recv(128)

                if response != "":
                    expected_result = True

                i += 1
        except socket.timeout:
            raise SparkException("Connection to Spark times out")
        finally:
            sock.close()

        logger.info("Response: {}".format(response))

        return response

    @staticmethod
    def __start_connection(ip_address):
        logger.debug("Start connection to spark")
        logger.debug("Create socket for: {}:{}".format(str(ip_address), int(settings.SPARK_PORT)))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)

        logger.debug("Socket connecting")
        server_address = (str(ip_address), int(settings.SPARK_PORT))
        sock.connect(server_address)

        return sock

    @staticmethod
    def receive_devices_json(sock):
        i = 0
        json = ""
        expected_result = False

        try:
            while not expected_result and i < 50:
                time.sleep(0.05)
                c = sock.recv(128)
                logger.debug(c)

                if len(c) == 0 or c[len(c) - 1] == '\x06':
                    if len(c) > 1:
                        json += c[0:-1]
                    expected_result = True
                else:
                    json += c

                i += 1

            logger.info("Response: \n{}".format(json))
        finally:
            sock.close()

        return json


class SparkException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)