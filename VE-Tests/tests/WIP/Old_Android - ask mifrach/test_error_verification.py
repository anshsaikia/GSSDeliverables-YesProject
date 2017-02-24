__author__ = 'rahulku3'

import logging

import pytest
from tests_framework.error_mock_server.error_response_server import *
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition

''' Global constants '''
TIMEOUT = 2
VERIFIED = False
KEEPALIVE_TIMEOUT = 10
FIRST_LAUNCH_TIMEOUT = 10
CHANNEL_CHANGE_TIMEOUT = 7
MAIN_HUB_SLEEP = 3

def get_ui_property_value(ve_test,client, propertyName, setName="catv-sm"):
    value = client.service.getPropertiesInSet(setName)
    for field in value:
        if field.PropertyDefName == propertyName :
            logging.info("DefValue for %s = \"%s\"" % (propertyName, field.PropertyDefValue))
            return field.PropertyDefValue
    logging.error('PropertyDefValue %s undefined in ui' %propertyName )
    ve_test.log_assert(False ," Required UI property Not Found")

def update_ui_property_value(client, propertyName, propertyValue, setName ="catv-sm"):
    logging.info('Setting UI property: ''%s'' with value %s' % (propertyName, propertyValue))
    client.service.updatePropertyValue(setName, propertyName, propertyValue)

def getLocalIP(ve_test):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


# def live_video_main_hub(ve_test, main_hub):
#     logging.info('Start Live from Main HUB')
#     milestones = ve_test.milestones
#
#     main_hub.navigate()
#     ve_test.wait(MAIN_HUB_SLEEP)
#     elements = milestones.getElements()
#
#     hubtv_panel = milestones.getElement([("name", "ShowcaseExpo_TV", "==")], elements)
#     ve_test.log_assert(hubtv_panel," HubTv Panel not Found")
#
#     #elements = milestones.getElements()
#
#     linearItems = milestones.getElementInBorders(elements, hubtv_panel, True)
#     logging.info("Elements info = %s" % linearItems)
#     ve_test.log_assert(linearItems, "No Linear Item Found")
#
#     "Test playback from mainhub"
#     if (ve_test.milestones.get_current_screen() == "notification"):
#         ve_test.screens.notification.go_to_previous_screen()
#
#     main_hub.tune_to_linear_channel_by_position(EventViewPosition.right_event)
#     ve_test.wait(CHANNEL_CHANGE_TIMEOUT)
#     logging.info('End Live from Main HUB')
#
#     return
#
#
# def play_video_keep_alive(ve_test, dicString , urlString, ip):
#     ve_test.wait(5)
#     if(ve_test.milestones.get_current_screen() == "notification"):
#         ve_test.screens.notification.go_to_previous_screen()
#     ve_test.wait(2)
#     live_video_main_hub(ve_test, ve_test.screens.main_hub)
#
#     errorString = ve_test.milestones.get_dic_value_by_key(dicString,"error")
#     if(ve_test.milestones.get_current_screen() == "notification"):
#         ve_test.screens.notification.go_to_previous_screen()
#     ve_test.milestones.update_url("keepAlive",urlString,ip, None)
#     ve_test.wait(KEEPALIVE_TIMEOUT+8)
#
#     screenElements = ve_test.milestones.getElements()
#     element = ve_test.milestones.getElement([("name","NotificationView", "==")],screenElements)
#     if errorString not in element["text_0"]:
#         return urlString
#
#
# def test_error_keep_alive_cases():
#     ve_test = VeTestApi("error:keep Alive")
#     ip = getLocalIP(ve_test)
#     mock_server = responseServer()
#     mock_server.start()
#
#     soapUrl = ve_test.he_utils.PrmUrl + ve_test.he_utils.configServiceWSDL
#     client = Client(soapUrl)
#
#     uiLinearExpiration = get_ui_property_value(ve_test, client, "net.beaumaris.catv.keepaliveinterval")
#     update_ui_property_value(client, "net.beaumaris.catv.keepaliveinterval", "10")
#
#     ve_test.begin()
#     device_details = ve_test.milestones.getDeviceDetails()
#     errorContext_dicString = {'ERR_SM_KEEPALIVE_BAD_PARAMS':'DIC_ERROR_PLAYBACK','ERR_SM_KEEPALIVE_NETWORK_TYPE':'DIC_ERROR_NETWORK_TYPE','ERR_SM_KEEPALIVE_OFFNET':'DIC_ERROR_OFFNET','ERR_SM_KEEPALIVE_BLACKLIST':'DIC_ERROR_BLACKLIST','ERR_SM_KEEPALIVE_ANONYMOUS_IP':'DIC_ERROR_PROXY_VPN_ERROR'}
#     flag = {}
#     actual_app_server_base_url = device_details['preferences']["pref_app_server_base_url"]
#     count = 0
#     for key in errorContext_dicString:
#         f = play_video_keep_alive(ve_test, errorContext_dicString[key], key, ip)
#         if f is not None:
#             flag[count] = f
#
#         ve_test.milestones.update_url("sessionSetup", "", "", actual_app_server_base_url)
#
#         # ve_test.wait(5)
#         # ve_test.screens.main_hub.navigate()
#         count = count + 1
#
#     ve_test.log_assert(len(flag) == 0,"The following error cases Failed" + str(flag))
#     update_ui_property_value(client, "net.beaumaris.catv.keepaliveinterval", uiLinearExpiration)
#     mock_server.stop()
#     ve_test.end()


def play_video_for_playback(ve_test, dicString , error_context, ip, actual_app_server_base_url):
    main_hub = ve_test.screens.main_hub
    main_hub.navigate()
    ve_test.wait(2)

    # if(ve_test.milestones.get_current_screen() == "notification"):
    #     ve_test.screens.notification.go_to_previous_screen()
    #     ve_test.wait(2)

    ve_test.milestones.update_url("sessionSetup", error_context, ip, None)
    ve_test.wait(2)

    main_hub.tune_to_linear_channel_by_position(EventViewPosition.right_event, False)
    ve_test.wait(CHANNEL_CHANGE_TIMEOUT)

    screenElements = ve_test.milestones.getElements()
    element = ve_test.milestones.getElement([("name", "NotificationView", "==")], screenElements)
    errorString = ve_test.milestones.get_dic_value_by_key(dicString, "error")

    ve_test.milestones.update_url("sessionSetup", "", "", actual_app_server_base_url)
    ve_test.wait(2)
    ve_test.screens.main_hub.navigate()

    if errorString not in element["text_0"]:
        return error_context


@pytest.mark.MF1382_infra_error_message
def test_error_playback_cases():
    ve_test = VeTestApi("error:playback")
    ip = getLocalIP(ve_test)

    #Start the mock error simulator server
    mock_server = responseServer()
    mock_server.start()

    ve_test.begin()

    device_details = ve_test.milestones.getDeviceDetails()

    actual_app_server_base_url = device_details['preferences']["pref_app_server_base_url"]
    errorContext_dicString = {'ERR_PLAYBACK_BAD_PARAMS':'DIC_ERROR_PLAYBACK','ERR_PLAYBACK_INTERNAL_SERVER':'DIC_ERROR_PLAYBACK','DIC_ERROR_PLAYBACK_GEO_LOCATION':'DIC_ERROR_PLAYBACK_GEO_LOCATION','DIC_ERROR_PLAYBACK_NETWORK_TYPE': 'DIC_ERROR_PLAYBACK_NETWORK_TYPE','DIC_ERROR_PLAYBACK_OFF_NETWORK':'DIC_ERROR_PLAYBACK_OFF_NETWORK','DIC_ERROR_PLAYBACK_BLACKLISTED':'DIC_ERROR_PLAYBACK_BLACKLISTED','DIC_ERROR_PLAYBACK_PROXY_VPN':'DIC_ERROR_PLAYBACK_PROXY_VPN','DIC_ERROR_PLAYBACK_DEVICE_NOT_FOUND':'DIC_ERROR_PLAYBACK_DEVICE_NOT_FOUND','DIC_ERROR_PLAYBACK_CONTENT_NOT_FOUND':'DIC_ERROR_PLAYBACK_CONTENT_NOT_FOUND'}
    flag = {}
    count = 0
    for key in errorContext_dicString:
        logging.info("Key: " + key)
        f = play_video_for_playback(ve_test, errorContext_dicString[key], key, ip, actual_app_server_base_url)
        if f is not None:
            flag[count] = f

        count = count + 1

    ve_test.log_assert(len(flag) == 0, "The following error cases failed " + str(flag))

    mock_server.stop()
    ve_test.end()


@pytest.mark.MF1382_infra_error_message
def test_remote_version_error():
    dicString="DIC_ERROR_VERSION_CHECK_FAILED_VERIFY_APPLICATION_VERSION"
    urlString="ERR_VERSION_NO_REMOTE_VERSION"

    ve_test = VeTestApi("test_remote_version_error")
    ip = getLocalIP(ve_test)

    #Start the mock error simulator server
    mock_server = responseServer()
    mock_server.start()

    ve_test.begin()
    ve_test.wait(2)

    ve_test.appium.push_data_to_settings("version_check_url", "http://" + ip + ":8080/" + urlString)

    ve_test.appium.launch_app()
    ve_test.wait(10)

    errorString = ve_test.milestones.get_dic_value_by_key(dicString, "error")
    screenElements = ve_test.milestones.getElements()
    element = ve_test.milestones.getElement([("name", "NotificationView", "==")],screenElements)

    ve_test.appium.reset_app()

    ve_test.log_assert(errorString in element["text_0"] ,"Required Message Not Found")

    mock_server.stop()
    ve_test.end()

