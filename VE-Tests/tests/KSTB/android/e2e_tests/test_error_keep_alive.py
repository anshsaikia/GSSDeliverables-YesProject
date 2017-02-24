__author__ = 'rahulku3'

import requests
import logging
#import socket
import pytest

#from time import sleep

from tests_framework.error_mock_server.error_response_server import *

from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KSTB.error import *

''' Global constants '''
TIMEOUT = 2
VERIFIED = False
KEEPALIVE_TIMEOUT = 20
TUNING_ERROR_TIMEOUT = 30
FIRST_LAUNCH_TIMEOUT = 10

DEFAULT_PAYLOAD_POST = {"jsonrpc": "2.0", "method": "configureApplicationForErrorTesting", "params": ["pref_app_server_base_url", "https://sgw.veop.phx.cisco.com", "sessionSetup"], "id" : 1}
HEADERS = {'content-type': 'application/json'}


def getMockServerIP():
    """
    Allow to retrieve the local IP address of the CTAP mock server.
    This server is used to send a mocked keep alive response.
    :return: the mock server IP address
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def update_url( ve_test, payload):
    """
    Update the keep-alive URL to force a specific response from the mock server.
    :param ve_test: the current test instance
    :param payload: the URL payload to post
    :return: The test failed if the HTTP response status is not 200 (OK)
    """
    url = "http://" + ve_test.configuration["device"]["ip"] + "/milestones"
    response = requests.post(url = url, data=json.dumps(payload), headers=HEADERS)
    ve_test.log_assert( response.status_code == 200 , " ******************** Failed to Update the URL ******************** ")


def restore_url(ve_test, actual_app_server_base_url):
    """
    Force to restore the keep-alive URL
    :param ve_test: the current test instance
    :param actual_app_server_base_url: the keep-alive URL to restore
    """
    payload = DEFAULT_PAYLOAD_POST
    payload["params"][1] = actual_app_server_base_url
    update_url(ve_test,payload)


def set_keep_alive_url(ve_test, ip, url_string):
    """
    Force the keep-alive URL to be the mocked server with a specific identifier
    corresponding to the response to send
    :param ve_test: the current test instance
    :param ip: the ip address of the CTAP mock server
    :param url_string: The response identifier
    """
    payload = DEFAULT_PAYLOAD_POST
    payload["params"][1] = "http://" + ip+ ":8080/" + url_string
    payload["params"][2] = "keepAlive"
    update_url(ve_test,payload)


def check_error_keep_alive(ve_test, error_text, error_code, url_string, ip):
    """
    Allow to check if the expected error is displayed for the given URL
    :param ve_test: the current test instance
    :param error_text: the expected error text
    :param error_code: the expected error code as a string
    :param url_string: the given response identifier to test
    :param ip: the local ip adress
    :return: True only if the error screen is displayed with expected error text and error code
    """
    device_details = ve_test.milestones.getDeviceDetails()
    # wait enough to have a keep alive response
    playback_status = ve_test.milestones.getPlaybackStatus()
    if "sso" in playback_status and "sessionKeepAlivePeriod" in playback_status["sso"]:
        period = int(playback_status["sso"]["sessionKeepAlivePeriod"])/1000
        logging.info("Keep Alive Period:"+str(period))
    else:
        logging.info("Keep Alive Period not found:"+str(playback_status))
        period = 30

    actual_app_server_base_url = device_details['preferences']["pref_app_server_base_url"]
    set_keep_alive_url(ve_test, ip, url_string)
    ve_test.wait(period+15)
    is_error = ve_test.is_notification_error(msg_title=ERROR_TITLE , msg_text=error_text, msg_code=error_code)
    restore_url(ve_test, actual_app_server_base_url)
    return is_error

'''
 The following test is not working due to CTAP issue with the video zapping unexpectedly stopped after few tests.
  So it is commented for the moment , and split with one test for each error case.
'''
'''
def test_keep_alive():
    """
    Start the CTAP mock server
    Start the application on the main hub
    Go to the full screen
    For each error to check :
        modify the keep-alive URL to receive a specific error response
        check the error screen is displayed with the correct text and error code
    :return: The test failed if one or more error have not been correctly displayed
    """
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApiKSTB("error:keep Alive")
    ve_test.begin()
    ve_test.wait_for_screen(30,"main_hub")
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(2);

    error_context_error_msg = {
        "ERR_SM_KEEPALIVE_ANONYMOUS_IP":E_STREAMING_PROXY_OR_VPN_ERROR_MSG,
        "ERR_SM_KEEPALIVE_GEO_RESTRICTION":E_STREAMING_GEO_LOCATION_ERROR_MSG,
        "ERR_SM_KEEPALIVE_OFFNET":E_STREAMING_OFF_NET_ERROR_MSG,
        "ERR_SM_KEEPALIVE_BLACKLIST":E_STREAMING_HOT_SPOT_ERROR_MSG,
        "ERR_SM_KEEPALIVE_NETWORK_TYPE":E_STREAMING_NET_TYPE_ERROR_MSG,
        "ERR_SM_KEEPALIVE_OUT_OF_HOME_ERROR":E_STREAMING_OUT_OF_HOME_ERROR_MSG,
        "ERR_SM_KEEPALIVE_GENERIC_ERROR":E_STREAMING_UNKNOWN_ERROR_MSG,
    }

    error_context_error_code = {
        "ERR_SM_KEEPALIVE_ANONYMOUS_IP":E_STREAMING_PROXY_OR_VPN_ERROR_CODE,
        "ERR_SM_KEEPALIVE_GEO_RESTRICTION":E_STREAMING_GEO_LOCATION_ERROR_CODE,
        "ERR_SM_KEEPALIVE_OFFNET":E_STREAMING_OFF_NET_ERROR_CODE,
        "ERR_SM_KEEPALIVE_BLACKLIST":E_STREAMING_HOT_SPOT_ERROR_CODE,
        "ERR_SM_KEEPALIVE_NETWORK_TYPE":E_STREAMING_NET_TYPE_ERROR_CODE,
        "ERR_SM_KEEPALIVE_OUT_OF_HOME_ERROR":E_STREAMING_OUT_OF_HOME_ERROR_CODE,
        "ERR_SM_KEEPALIVE_GENERIC_ERROR":E_STREAMING_UNKNOWN_ERROR_CODE,
    }

    flag = {}
    count = 0
    for key in error_context_error_code:
        status = check_error_keep_alive(ve_test,error_context_error_msg[key],error_context_error_code[key],key,ip)
        # Store the key in error
        if not status:
            flag[count] = key
            count += 1
        # Re-zap on the first channel to restart the keep-alive mechanism
        ve_test.appium.key_event("KEYCODE_1")
        ve_test.wait(5);
    ve_test.log_assert(len(flag) == 0,"The " +len(flag)+ "following error cases failed : " + str(flag))
    mock_server.stop()
    ve_test.end()
'''

# ERR_SM_KEEPALIVE_ANONYMOUS_IP
@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
def test_keep_alive_anonymous_ip():
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApi("error:keep_alive_anonymous_ip")
    ve_test.begin()
    ve_test.wait_for_screen(30,"main_hub")
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(2)
    status = check_error_keep_alive(ve_test,E_STREAMING_PROXY_OR_VPN_ERROR_MSG,E_STREAMING_PROXY_OR_VPN_ERROR_CODE,"ERR_SM_KEEPALIVE_ANONYMOUS_IP",ip)
    ve_test.log_assert(status,"Expected message '"+E_STREAMING_PROXY_OR_VPN_ERROR_MSG+"' with code '"+E_STREAMING_PROXY_OR_VPN_ERROR_CODE+"'")
    mock_server.stop()
    ve_test.end()

# ERR_SM_KEEPALIVE_GEO_RESTRICTION
@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
def test_keep_alive_geo_restriction():
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApi("error:keep_alive_geo_restriction")
    ve_test.begin()
    ve_test.wait_for_screen(30,"main_hub")
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(2)
    status = check_error_keep_alive(ve_test,E_STREAMING_GEO_LOCATION_ERROR_MSG,E_STREAMING_GEO_LOCATION_ERROR_CODE,"ERR_SM_KEEPALIVE_GEO_RESTRICTION",ip)
    ve_test.log_assert(status,"Expected message '"+E_STREAMING_GEO_LOCATION_ERROR_MSG+"' with code '"+E_STREAMING_GEO_LOCATION_ERROR_CODE+"'")
    mock_server.stop()
    ve_test.end()


# ERR_SM_KEEPALIVE_OFFNET
@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
def test_keep_alive_offnet():
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApi("error:keep_alive_offnet")
    ve_test.begin()
    ve_test.wait_for_screen(30,"main_hub")
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(2)
    status = check_error_keep_alive(ve_test,E_STREAMING_OFF_NET_ERROR_MSG,E_STREAMING_OFF_NET_ERROR_CODE,"ERR_SM_KEEPALIVE_OFFNET",ip)
    ve_test.log_assert(status,"Expected message '"+E_STREAMING_OFF_NET_ERROR_MSG+"' with code '"+E_STREAMING_OFF_NET_ERROR_CODE+"'")
    mock_server.stop()
    ve_test.end()


# ERR_SM_KEEPALIVE_BLACKLIST
@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
def test_keep_alive_blacklist():
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApi("error:keep_alive_blacklist")
    ve_test.begin()
    ve_test.wait_for_screen(30,"main_hub")
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(2)
    status = check_error_keep_alive(ve_test,E_STREAMING_HOT_SPOT_ERROR_MSG,E_STREAMING_HOT_SPOT_ERROR_CODE,"ERR_SM_KEEPALIVE_BLACKLIST",ip)
    ve_test.log_assert(status,"Expected message '"+E_STREAMING_HOT_SPOT_ERROR_MSG+"' with code '"+E_STREAMING_HOT_SPOT_ERROR_CODE+"'")
    mock_server.stop()
    ve_test.end()

# ERR_SM_KEEPALIVE_NETWORK_TYPE
@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
def test_keep_alive_network_type():
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApi("error:keep_alive_network_type")
    ve_test.begin()
    ve_test.wait_for_screen(30,"main_hub")
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(2)
    status = check_error_keep_alive(ve_test,E_STREAMING_NET_TYPE_ERROR_MSG,E_STREAMING_NET_TYPE_ERROR_CODE,"ERR_SM_KEEPALIVE_NETWORK_TYPE",ip)
    ve_test.log_assert(status,"Expected message '"+E_STREAMING_NET_TYPE_ERROR_MSG+"' with code '"+E_STREAMING_NET_TYPE_ERROR_CODE+"'")
    mock_server.stop()
    ve_test.end()

# ERR_SM_KEEPALIVE_OUT_OF_HOME_ERROR
@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
def test_keep_alive_out_of_home():
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApi("error:keep_alive_out_of_home")
    ve_test.begin()
    ve_test.wait_for_screen(30,"main_hub")
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(2)
    status = check_error_keep_alive(ve_test,E_STREAMING_OUT_OF_HOME_ERROR_MSG,E_STREAMING_OUT_OF_HOME_ERROR_CODE,"ERR_SM_KEEPALIVE_OUT_OF_HOME_ERROR",ip)
    ve_test.log_assert(status,"Expected message '"+E_STREAMING_OUT_OF_HOME_ERROR_MSG+"' with code '"+E_STREAMING_OUT_OF_HOME_ERROR_CODE+"'")
    mock_server.stop()
    ve_test.end()

# ERR_SM_KEEPALIVE_GENERIC_ERROR
@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
def test_keep_alive_generic_error():
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApi("error:keep_alive_generic_error")
    ve_test.begin()
    ve_test.wait_for_screen(30,"main_hub")
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(2)
    status = check_error_keep_alive(ve_test,E_STREAMING_UNKNOWN_ERROR_MSG,E_STREAMING_UNKNOWN_ERROR_CODE,"ERR_SM_KEEPALIVE_GENERIC_ERROR",ip)
    ve_test.log_assert(status,"Expected message '"+E_STREAMING_UNKNOWN_ERROR_MSG+"' with code '"+E_STREAMING_UNKNOWN_ERROR_CODE+"'")
    mock_server.stop()
    ve_test.end()
