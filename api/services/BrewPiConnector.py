from __builtin__ import staticmethod
import logging
import socket
import time

import sys
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

        try:
            sock = BrewPiConnector.__start_connection(brewpi.ip_address)

            message = "s{{name:{},oinkweb:{},oinkwebport:{},datetime:{}}}".format(brewpi.name, local_ip, local_port,
                                                                                  datetime)

            logger.debug("Send Message: {}".format(message))
            sock.sendall(message)
            response = sock.recv(1024)
            sock.close()

        except socket.timeout as e:
            response = e.message
            logger.error("Time Out: {}", response)
        except socket.error as e:
            response = e.message
            logger.error("Socket Error: {}", response)
        except Exception as e:
            response = str(e)
            logger.error("General Error: {}", response)

        logger.info("Response: {}".format(response))
        return True if response[:2] == "Ok" else False, response

    @staticmethod
    def send_reset(brewpi):
        logger.info("Reset BrewPi {}".format(brewpi))

        try:
            sock = BrewPiConnector.__start_connection(brewpi.ip_address, 1)

            logger.debug("Send Message: r")
            sock.sendall("r")
            response = sock.recv(2)

            sock.close()

        except socket.timeout as e:
            response = e.message
            logger.debug("Time Out: {}", response)
        except socket.error as e:
            response = e.message
            logger.debug("Socket Error: {}", response)
        except Exception as e:
            response = str(e)
            logger.error("General Error: {}", response)

        logger.info("Response: {}".format(response))
        return True if response[:2] == "Ok" else False, response

    @staticmethod
    def send_device_offset(device):
        logger.info("Send device offset to BrewPi {} for device {}".format(device.brewpi, device))

        try:
            sock = BrewPiConnector.__start_connection(device.brewpi.ip_address)

            message = "o{{pin_nr:{},hw_address:{},offset:{}}}".format(device.pin_nr, device.hw_address,
                                                                      int(device.offset * 10000))

            logger.debug("Send Message: " + message)
            sock.sendall(message)
            response = sock.recv(1024)

            sock.close()

        except socket.timeout as e:
            response = e.message
            logger.error("TimeOut: {}", response)
        except socket.error as e:
            response = e.message
            logger.error("Socket Error: {}", response)
        except Exception as e:
            response = str(e)
            logger.error("General Error: {}", response)

        logger.info("Response: {}".format(response))
        return True if response[:2] == "Ok" else False, response

    @staticmethod
    def send_configuration(brewpi, configuration):
        logger.info("Send configuration {} to BrewPi {}".format(configuration.pk, brewpi))

        try:
            sock = BrewPiConnector.__start_connection(brewpi.ip_address)

            temp_sensor = configuration.get_temp_sensor()
            heat_actuator = configuration.get_heat_actuator()
            cool_actuator = configuration.get_cool_actuator()
            fan_actuator = configuration.get_fan_actuator()
            pump_1_actuator = configuration.get_pump_1_actuator()
            pump_2_actuator = configuration.get_pump_2_actuator()

            temp_sensor_str = "{};{}".format(temp_sensor.pin_nr, temp_sensor.hw_address)
            heat_actuator_str = "{};{}".format(heat_actuator.pin_nr, heat_actuator.hw_address)
            cool_actuator_str = "0;0000000000000000" if cool_actuator is None else "{};{}".format(cool_actuator.pin_nr,
                                                                                          cool_actuator.hw_address)
            fan_actuator_str = "0;0000000000000000" if fan_actuator is None else "{};{}".format(fan_actuator.pin_nr,
                                                                                        fan_actuator.hw_address)
            pump_1_actuator_str = "0;0000000000000000" \
                if pump_1_actuator is None else "{};{}".format(pump_1_actuator.pin_nr, pump_1_actuator.hw_address)
            pump_2_actuator_str = "0;0000000000000000" \
                if pump_2_actuator is None else "{};{}".format(pump_2_actuator.pin_nr, pump_2_actuator.hw_address)

            phase = Phase.objects.filter(configuration=configuration, done=False)[0]

            msg = 'p{{"config_id":{},"name":{},"config_type":{},"temp_sensor":"{}","heat_actuator":"{}",' \
                  '"cool_actuator":"{}","fan_actuator":"{}","pump_1_actuator":"{}","pump_2_actuator":"{}",' \
                  '"temperature":{},"heat_pwm":{},"fan_pwm":{},"pump_1_pwm":{},"pump_2_pwm":{},' \
                  '"heating_period":{},"cooling_period":{},"cooling_on_time":{},"cooling_off_time":{},' \
                  '"p":{},"i":{},"d":{}}}'.format(configuration.id, configuration.name, configuration.type,
                                                  temp_sensor_str, heat_actuator_str, cool_actuator_str,
                                                  fan_actuator_str, pump_1_actuator_str, pump_2_actuator_str,
                                                  int(phase.temperature * 10000), int(phase.heat_pwm * 10000),
                                                  int(phase.fan_pwm * 10000), int(phase.pump_1_pwm * 10000),
                                                  int(phase.pump_2_pwm * 10000), phase.heating_period,
                                                  phase.cooling_period, phase.cooling_on_time,
                                                  phase.cooling_off_time, int(phase.p * 10000), int(phase.i * 10000),
                                                  int(phase.d * 10000))
            logger.debug("Send Message: " + msg)
            sock.sendall(msg)
            response = sock.recv(1024)

            sock.close()

        except socket.timeout as et:
            response = et.message
            logger.error("Time Out: {}", response)
        except socket.error as ee:
            response = ee.message
            logger.error("Socket Error: {}", response)
        except Exception as e:
            response = str(e)
            logger.error("General Error: {}", response)

        logger.info("Response: {}".format(response))
        return True if response[:2] == "Ok" else False, response

    @staticmethod
    def delete_configuration(brewpi, configuration):
        logger.info("Delete configuration {} from BrewPi {}".format(configuration, brewpi))

        try:
            sock = BrewPiConnector.__start_connection(brewpi.ip_address)

            message = 'q{{"config_id":{}}}'.format(configuration.id)

            logger.debug("Send Message: " + message)
            sock.sendall(message)
            response = sock.recv(1024)

            sock.close()

        except socket.timeout as e:
            response = e.message
            logger.error("Time Out: {}", response)
        except socket.error as e:
            response = e.message
            logger.error("Socket Error: {}", response)
        except Exception as e:
            response = str(e)
            logger.error("General Error: {}", response)

        logger.info("Response: {}".format(response))
        return True if response[:2] == "Ok" else False, response

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
