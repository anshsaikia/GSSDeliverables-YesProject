__author__ = 'rahulku3'

import requests
import pytest


from tests_framework.error_mock_server.error_response_server import *
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KSTB.error import *

''' Global constants '''
TIMEOUT = 2
VERIFIED = False
KEEPALIVE_TIMEOUT = 20
TUNING_ERROR_TIMEOUT = 30
FIRST_LAUNCH_TIMEOUT = 10



DEFAULT_PAYLOAD_POST = {"jsonrpc": "2.0", "method": "configureApplicationForErrorTesting", "params": ["pref_app_server_base_url","https://sgw.veop.phx.cisco.com","sessionSetup"], "id" : 1}
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
    Update the playback error creation URL to force a specific response from the mock server.
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



def check_error_playback(ve_test, error_text, error_code, url_string, ip):
    """
    Allow to check if the expected error is displayed for the given URL
    :param ve_test: the current test instance
    :param error_code_string: the expected error as a string
    :param url_string: the given response identifier to test
    :param ip: the local ip adress
    :return: True only if the error screen is displayed with expected error code
    """
    device_details = ve_test.milestones.getDeviceDetails()
    actual_app_server_base_url = device_details['preferences']["pref_app_server_base_url"]
#    print("TOTO %s" %device_details['preferences']["pref_app_server_base_url"])
    
    payload = DEFAULT_PAYLOAD_POST
    payload["params"][1] = "http://" + ip+ ":8080/" + url_string
    payload["params"][2] = "sessionSetup"

    milestones = ve_test.milestones

    update_url(ve_test,payload)

    ve_test.wait(10)
    ve_test.appium.key_event("KEYCODE_DPAD_DOWN")
    ve_test.wait(10)

    is_error = ve_test.is_notification_error(msg_title=ERROR_TITLE , msg_text=error_text, msg_code=error_code)
    ve_test.screens.playback.verify_streaming_stopped()

    restore_url(ve_test, actual_app_server_base_url)
    return is_error

# verification screeply in dummy for playback error creation
@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.dummy
def test_playback_error_dummy():
    ve_test = VeTestApi("test_playback_error_dummy")
    milestones = ve_test.milestones
    ve_test.begin(screen=ve_test.screens.fullscreen)
    ve_test.wait(2)
    # via timelime select channel 2
    ve_test.appium.long_key_event("KEYCODE_DPAD_LEFT")
    ve_test.wait(2)
    ve_test.appium.key_event("KEYCODE_DPAD_DOWN")
    ve_test.wait(2)
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(2)

    # verification message
    title = "Error"
    msg_txt = "create streaming session had failed"
    msg_code = "0002"
    ve_test.check_notification_screen('shown',title, msg_txt, msg_code, None )
    # Verify the playback status of the content
    ve_test.screens.playback.verify_streaming_stopped()
    # back + ok
    ve_test.wait(2)
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(2)
    #ve_test.appium.key_event("KEYCODE_DPAD_RIGHT")
    #ve_test.wait(2)
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(5)
    # Verify the playback status of the content
    #verify_streaming_playing(ve_test,milestones)
    ve_test.screens.playback.verify_streaming_playing()

    # verification stream play.
    ve_test.end()
    # end test


# ERR_ROOTED_DEVICE
@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
def test_playback_rooted_device():
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApi("error:erro_rooted_device")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    status = check_error_playback(ve_test,E_STREAMING_ROOTED_DEVICE_ERROR_MSG,E_STREAMING_ROOTED_DEVICE_ERROR_CODE,"ERR_PLAYBACK_ROOTED_DEVICE",ip)
    mock_server.stop()
    ve_test.log_assert(status,"Expected message '"+E_STREAMING_ROOTED_DEVICE_ERROR_MSG+"' with code '"+E_STREAMING_ROOTED_DEVICE_ERROR_CODE+"'")
    ve_test.end()

@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression

def test_error_playback_general():
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApi("error:erro_general")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    status = check_error_playback(ve_test,E_STREAMING_GENERAL_ERROR_MSG,E_STREAMING_GENERAL_ERROR_CODE,"ERR_PLAYBACK_GENERAL",ip)
    mock_server.stop()
    ve_test.log_assert(status,"Expected message '"+E_STREAMING_GENERAL_ERROR_MSG+"' with code '"+E_STREAMING_GENERAL_ERROR_CODE+"'")
    ve_test.end()

@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
def test_error_playback_concurrency():
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApi("error:erro_concurrency")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    status = check_error_playback(ve_test,E_STREAMING_CONCURRENCY_ERROR_MSG,E_STREAMING_CONCURRENCY_ERROR_CODE,"ERR_PLAYBACK_CONCURENCY_LIMIT",ip)
    mock_server.stop()
    ve_test.log_assert(status,"Expected message '"+E_STREAMING_CONCURRENCY_ERROR_MSG+"' with code '"+E_STREAMING_CONCURRENCY_ERROR_CODE+"'")
    ve_test.end()

@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
def test_error_playback_network_type_ip():
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApi("error:erro_network_type")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    status = check_error_playback(ve_test,E_STREAMING_NETWORKTYPE_ERROR_MSG,E_STREAMING_NETWORKTYPE_ERROR_CODE,"ERR_PLAYBACK_NETWORK_TYPE",ip)
    mock_server.stop()
    ve_test.log_assert(status,"Expected message '"+E_STREAMING_NETWORKTYPE_ERROR_MSG+"' with code '"+E_STREAMING_NETWORKTYPE_ERROR_CODE+"'")
    ve_test.end()

@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
def test_error_playback_device_not_found():
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApi("error:erro_device_not_found")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    status = check_error_playback(ve_test,E_STREAMING_DEVICE_NOTFOUND_ERROR_MSG,E_STREAMING_DEVICE_NOTFOUND_ERROR_CODE,"ERR_PLAYBACK_DEVICE_NOT_FOUND",ip)
    mock_server.stop()
    ve_test.log_assert(status,"Expected message '"+E_STREAMING_DEVICE_NOTFOUND_ERROR_MSG+"' with code '"+E_STREAMING_DEVICE_NOTFOUND_ERROR_CODE+"'")
    ve_test.end()

@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
def test_error_playback_content_not_found():
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApi("error:erro_content_not_found")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    status = check_error_playback(ve_test,E_STREAMING_CONTENT_NOTFOUND_ERROR_MSG,E_STREAMING_CONTENT_NOTFOUND_ERROR_CODE,"ERR_PLAYBACK_CONTENT_NOT_FOUND",ip)
    mock_server.stop()
    ve_test.log_assert(status,"Expected message '"+E_STREAMING_CONTENT_NOTFOUND_ERROR_MSG+"' with code '"+E_STREAMING_CONTENT_NOTFOUND_ERROR_CODE+"'")
    ve_test.end()

@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
def test_error_playback_content_not_playable():
    ip = getMockServerIP()
    mock_server = responseServer()
    mock_server.start()
    ve_test = VeTestApi("error:erro_content_not_playable")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    status = check_error_playback(ve_test,E_STREAMING_CHANNEL_NOTPLAYABLE_ERROR_MSG,E_STREAMING_CHANNEL_NOTPLAYABLE_ERROR_CODE,"ERR_PLAYBACK_CONTENT_NOT_PLAYABLE",ip)
    mock_server.stop()
    ve_test.log_assert(status,"Expected message '"+E_STREAMING_CHANNEL_NOTPLAYABLE_ERROR_MSG+"' with code '"+E_STREAMING_CHANNEL_NOTPLAYABLE_ERROR_CODE+"'")
    ve_test.end()
