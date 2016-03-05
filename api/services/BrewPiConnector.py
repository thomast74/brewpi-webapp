from __builtin__ import staticmethod
from _socket import SHUT_RDWR
import logging
import socket
import time

from django.conf import settings
from django.utils import timezone
from api.helpers.Exceptions import BrewPiException
from api.models import Phase

logger = logging.getLogger(__name__)


class BrewPiConnector:
    def __init__(self):
        return

    @staticmethod
    def send_brewpi_info(brewpi, local_ip, local_port):
        logger.info("Send device info to BrewPi {}".format(brewpi))
        datetime = int(time.mktime(timezone.now().timetuple()))

        sock = BrewPiConnector.__start_connection(brewpi.ip_address)

        try:
            message = "s{{name:{},oinkweb:{},oinkwebport:{},datetime:{}}}".format(brewpi.name, local_ip, local_port,
                                                                                  datetime)
            logger.debug("Send Message: {}".format(message))
            sock.sendall(message)

            time.sleep(0.02)
            response = sock.recv(2)
            logger.info("Response: {}".format(response))

        except socket.timeout:
            raise BrewPiException("Connection to BrewPi timed out")
        finally:
            sock.shutdown(SHUT_RDWR)
            sock.close()

        return True if response == "Ok" else False

    @staticmethod
    def send_reset(brewpi):
        logger.info("Reset BrewPi {}".format(brewpi))

        sock = BrewPiConnector.__start_connection(brewpi.ip_address, 1)

        try:
            logger.debug("Send Message: r")
            sock.sendall("r")

            time.sleep(0.02)
            response = sock.recv(2)
            logger.info("Response: {}".format(response))

        except socket.timeout:
            logger.debug("Connection to BrewPi timed out")
        finally:
            sock.close()

        return True if response == "Ok" else False

    @staticmethod
    def send_device_offset(device):
        logger.info("Send device offset to BrewPi {} for device {}".format(device.brewpi, device))

        sock = BrewPiConnector.__start_connection(device.brewpi.ip_address)

        try:
            message = "o{{pin_nr:{},hw_address:{},offset:{}}}".format(device.pin_nr, device.hw_address,
                                                                      int(device.offset * 10000))
            logger.debug("Send Message: " + message)
            sock.send(message)

            time.sleep(0.02)
            response = sock.recv(2)
            logger.debug("Response: {}".format(response))

        except socket.timeout:
            raise BrewPiException("Connection to BrewPi timed out")
        finally:
            sock.close()

        return response

    @staticmethod
    def send_configuration(brewpi, configuration):
        logger.info("Send configuration {} to BrewPi {}".format(configuration.pk, brewpi))

        sock = BrewPiConnector.__start_connection(brewpi.ip_address)

        try:
            temp_sensor = configuration.get_temp_sensor()
            heat_actuator = configuration.get_heat_actuator()
            cool_actuator = configuration.get_cool_actuator()
            fan_actuator = configuration.get_fan_actuator()

            temp_sensor_str = "{};{}".format(temp_sensor.pin_nr, temp_sensor.hw_address)
            heat_actuator_str = "{};{}".format(heat_actuator.pin_nr, heat_actuator.hw_address)
            cool_actuator_str = "0;0" if cool_actuator is None else "{};{}".format(cool_actuator.pin_nr,
                                                                                   cool_actuator.hw_address)
            fan_actuator_str = "0;0" if fan_actuator is None else "{};{}".format(fan_actuator.pin_nr,
                                                                                 fan_actuator.hw_address)

            phase = Phase.objects.filter(configuration=configuration, done=False)[0]

            sock.send("p")
            time.sleep(0.015)
            msg = '{{"config_id":{},"name":{},"config_type":{},"temp_sensor":"{}","heat_actuator":"{}",' \
                  '"cool_actuator":"{}","fan_actuator":"{}","temperature":{},"heat_pwm":{},"fan_pwm":{},' \
                  '"heating_period":{},"cooling_on_period":{},"cooling_off_period":{},' \
                  '"p":{},"i":{},"d":[]}}'.format(configuration.id, configuration.name, configuration.type,
                                                  temp_sensor_str, heat_actuator_str, cool_actuator_str,
                                                  fan_actuator_str,
                                                  int(phase.temperature*10000), int(phase.heat_pwm*10000),
                                                  int(phase.fan_pwm*10000),
                                                  phase.heating_period, phase.cooling_on_period,
                                                  phase.cooling_off_period, int(phase.p*10000), int(phase.i*10000),
                                                  int(phase.d*10000))
            logger.debug("Send Message: p" + msg)

            sock.send(msg)

            time.sleep(0.02)
            response = sock.recv(2)
            logger.debug("Response: {}".format(response))

        except socket.timeout:
            raise BrewPiException("Connection to BrewPi timed out")
        finally:
            sock.close()

        return True if response == "Ok" else False

    @staticmethod
    def delete_configuration(brewpi, configuration):
        logger.info("Delete configuration {} from BrewPi {}".format(configuration, brewpi))

        sock = BrewPiConnector.__start_connection(brewpi.ip_address)

        try:
            message = 'q{{"config_id":{}}}'.format(configuration.id)
            logger.debug("Send Message: " + message)

            sock.send(message)

            time.sleep(0.02)
            response = sock.recv(2)
            logger.debug("Response: {}".format(response))

        except socket.timeout:
            raise BrewPiException("Connection to BrewPi timed out")
        finally:
            sock.close()

        return True if response == "Ok" else False

    @staticmethod
    def __start_connection(ip_address, timeout=30):
        logger.debug("Start connection to BrewPi: {}".format(ip_address))
        try:
            logger.debug("Create socket for: {}:{}".format(str(ip_address), int(settings.BREWPI_PORT)))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)

            logger.debug("Socket connecting")
            server_address = (str(ip_address), int(settings.BREWPI_PORT))
            sock.connect(server_address)
        except:
            logger.error("Connection to BrewPi not possible")
            raise BrewPiException("Connection to BrewPi not possible")

        return sock
