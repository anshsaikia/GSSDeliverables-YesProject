'''
Created on Apr 21, 2015

@author: bwarshaw
'''

import ConfigParser, sys, os
from optparse import OptionParser

def usage(reason):
    if reason:
        print reason
    print "Usage: create_ini_file.py <device id> <default ini> <target new ini path> <device host> <appium port> <lab> <project> <screenShot_directory>"
    assert 0

CONFIGURATION_FILE_NAME = "CI_Environment.ini"

def check_arguments():
    if len(sys.argv) < 7:
        usage("Wrong arguments")
        
    if not os.path.isfile(sys.argv[2]):
        usage("Second argv must be default ini file")
        
    if not os.path.isdir(sys.argv[3]):
        usage("Third argv must be the target ini file path")

    if ":" in sys.argv[4]:
        usage("client host ip has to be host only")
        
if __name__ == '__main__':
    check_arguments()

    optionParser = OptionParser()
    optionParser.add_option("--in_home_router_ip")
    optionParser.add_option("--in_home_router_passwd")
    optionParser.add_option("--in_home_router_ssid")
    optionParser.add_option("--in_home_router_stb_ssh_port")
    optionParser.add_option("--in_home_router_appium_port")
    optionParser.add_option("--out_home_router_ip")
    optionParser.add_option("--out_home_router_passwd")
    optionParser.add_option("--out_home_router_ssid")
    optionParser.add_option("--out_home_router_appium_port")

    (named_args, positional_args) = optionParser.parse_args()

    device_id = positional_args[0]
    default_ini_file = positional_args[1]
    target_new_ini_path = positional_args[2]
    client_host_ip = positional_args[3]
    appium_port = positional_args[4]
    lab = positional_args[5]

    if lab == 'cloudberry':
		lab = 'veop'

    screenShot_directory = None
    project = None
    if len(positional_args) > 6:
        project = positional_args[6]
    if len(positional_args) > 7:
        screenShot_directory = positional_args[7]

    configParser = ConfigParser.ConfigParser()
    configParser.optionxform = str
    configParser.read(default_ini_file)

    "Add HE_VARS"
    if 'HE_VARS' not in configParser.sections():
        configParser.add_section('HE_VARS')
    configParser.set('HE_VARS', 'lab', lab)

    "Add CLIENT_VARS"
    if 'CLIENT_VARS' not in configParser.sections():
        configParser.add_section('CLIENT_VARS')
    configParser.set('CLIENT_VARS', 'deviceId', device_id)
    if configParser.get("APPIUM_VARS", "platformName") == 'iOS':
        client_port = "8080"
    else:
        if project is not None and project == 'KD':
            client_port = "5050"
        else:
            client_port = "8080"

    configParser.set('CLIENT_VARS', 'ip', client_host_ip + ":" + client_port)

    "Add APPIUM_VARS"
    if configParser.get("APPIUM_VARS", "platformName") != 'iOS':
        if 'APPIUM_VARS' not in configParser.sections():
            configParser.add_section('APPIUM_VARS')
        configParser.set('APPIUM_VARS', 'ip', configParser.get("APPIUM_VARS", "ip").split(":")[0] + ":" + appium_port)
        if project is not None and project == 'K' or project == 'KV2':
            configParser.set('APPIUM_VARS', 'appPackage', 'com.cisco.videoeverywhere3.nexplayer')

    "Add general section"
    if 'general' not in configParser.sections():
        configParser.add_section('general')
    if project is not None:
        configParser.set('general', 'project', project)
    if screenShot_directory is not None:
        configParser.set('general', 'screenshotDir', screenShot_directory)

    "Add NETWORK_VARS"
    if 'NETWORK_VARS' not in configParser.sections():
        configParser.add_section('NETWORK_VARS')
    configParser.set('NETWORK_VARS', 'in_home_router_ip', named_args.in_home_router_ip)
    configParser.set('NETWORK_VARS', 'in_home_router_passwd', named_args.in_home_router_passwd)
    configParser.set('NETWORK_VARS', 'in_home_router_ssid', named_args.in_home_router_ssid)
    configParser.set('NETWORK_VARS', 'in_home_router_stb_ssh_port', named_args.in_home_router_stb_ssh_port)
    configParser.set('NETWORK_VARS', 'in_home_router_appium_port', named_args.in_home_router_appium_port)
    configParser.set('NETWORK_VARS', 'out_home_router_ip', named_args.out_home_router_ip)
    configParser.set('NETWORK_VARS', 'out_home_router_passwd', named_args.out_home_router_passwd)
    configParser.set('NETWORK_VARS', 'out_home_router_ssid', named_args.out_home_router_ssid)
    configParser.set('NETWORK_VARS', 'out_home_router_appium_port', named_args.out_home_router_appium_port)

    new_ini_file = open(target_new_ini_path + CONFIGURATION_FILE_NAME, 'w')
    configParser.write(new_ini_file)
    new_ini_file.close()
