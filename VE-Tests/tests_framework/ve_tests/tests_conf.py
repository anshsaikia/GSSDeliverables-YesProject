__author__ = 'bwarshaw'

import os
import logging
from configparser import ConfigParser
from enum import Enum

class DeviceType(Enum):
    PC = "PC"
    TABLET = "TABLET"
    PHABLET = "PHABLET"
    SMARTPHONE = "SMARTPHONE"
    STB = "STB"

CONFIGURATION_FILE_NAME = "CI_Environment.ini"

def set_device_type(test):
    if test.project_type != "KSTB":
        device_details = test.milestones.getDeviceDetails()
        if "device-type" in device_details:
            device_type = device_details["device-type"].upper()
            for retry in range(0,30):
                if device_type != "UNKNOWN":
                    break
                test.wait(1)
                device_details = test.milestones.getDeviceDetails(update=True)
                test.log_assert("device-type" in device_details, "Cannot find device type in device details")
                device_type = device_details["device-type"].upper()
            test.log_assert(device_type == DeviceType.TABLET.value or device_type == DeviceType.PHABLET.value or device_type == DeviceType.SMARTPHONE.value,"Undefined device type: %s"%device_details["device-type"])
            if device_type == DeviceType.TABLET.value:
                test.device_type = DeviceType.TABLET
            elif device_type == DeviceType.PHABLET.value:
                test.device_type = DeviceType.PHABLET
                test.screens.main_hub.MAIN_HUB_TOTAL_CHANNEL_COUNT = 6
                test.screens.main_hub.MAIN_HUB_SHOWED_CHANNEL_COUNT = 2
            elif device_type == DeviceType.SMARTPHONE.value:
                test.device_type = DeviceType.SMARTPHONE
                test.screens.main_hub.MAIN_HUB_TOTAL_CHANNEL_COUNT = 6
                test.screens.main_hub.MAIN_HUB_SHOWED_CHANNEL_COUNT = 2
        else:
            test.device_type = DeviceType.TABLET
    else:
        # The device_type is not yet implemented in the KSTB application.
        test.device_type = DeviceType.STB
    logging.info('Device Type is: %s'%test.device_type)

def configuration(test):

    assert os.path.isfile(CONFIGURATION_FILE_NAME), "%s file is not found, verify its located in the path where you run the test from" % CONFIGURATION_FILE_NAME

    logging.info('start read configurations')
    config_parser = ConfigParser()
    config_parser.optionxform = str
    config_parser.read(CONFIGURATION_FILE_NAME)
    configurations = {}
    for section in config_parser.sections():
        fixed_name = section
        if section == "CLIENT_VARS": fixed_name = "device"
        if section == "APPIUM_VARS": fixed_name = "appium"
        if section == "HE_VARS": fixed_name = "he"
        if section == "NETWORK_VARS": fixed_name = "network"
        configurations[fixed_name] = {}
        for key in config_parser.options(section):
            configurations[fixed_name][key] = config_parser.get(section, key)

    if 'general' in configurations:
        if 'he' in configurations['general'] and configurations['general']['he'] and configurations[configurations['general']['he']]:
            configurations['he'] = configurations[configurations['general']['he']]

    return configurations
