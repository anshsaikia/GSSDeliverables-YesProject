__author__ = 'gcohen'

import logging
import pytest
from tests_framework.ui_building_blocks.KD.pincode import YouthChanneltype
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.he_utils.he_utils import VodContentType
from vgw_test_utils.IHmarks import IHmark

' Global constants '
TIMEOUT = 3


@IHmark.O_Allianz
@IHmark.LV_L2
def test_tune_to_youth_channel():
    ve_test = VeTestApi("test_tune_to_youth_channel")
    ve_test.begin()

    pincode = ve_test.screens.pincode
    zap_list = ve_test.screens.zaplist
    infolayer = ve_test.screens.infolayer
    playback = ve_test.screens.playback
    fullscreen = ve_test.screens.fullscreen

    "Verify Video Is Shown"
    ve_test.log_assert(playback.is_video_hidden() == False, "Video Is Hidden")

    "Tune to youth channel"
    yp_channel = pincode.get_youth_channel(type=YouthChanneltype.ALL_EVENTS_PROTECTED)
    zap_list.tune_to_channel_by_sek(yp_channel)
    ve_test.log_assert(playback.is_video_hidden() == True, "Video Is not Hidden on Locked channel %s" % yp_channel)

    pincode.navigate()

    "verify pin msg"
    retry = pincode.get_ctap_retry_count()
    pincode_enter_msg =  ve_test.milestones.get_dic_value_by_key('DIC_PIN_CODE_ENTRY_RETRIES', 'general') % retry
    pincode.verify_message(pincode_enter_msg)

    "enter wrong pin"
    logging.info("enter wrong pin")
    wrong_pin = "7182"
    pincode.enter_pin(wrong_pin)
    pincode_invalid_msg =  ve_test.milestones.get_dic_value_by_key('DIC_PIN_CODE_INVALID_RETRY', 'general') % (retry-1)
    pincode.verify_message(pincode_invalid_msg)

    "enter correct pin"
    logging.info("enter correct pin")
    pincode.enter_pin()
    ve_test.log_assert(playback.is_video_hidden() == False, "Video Is Hidden after entering pin")
    ve_test.log_assert(infolayer.is_program_locked() == False, "Unlock button shows after entering pin on action_menu")
    #action_menu.go_to_previous_screen()
    fullscreen.verify_active()
    ve_test.log_assert(fullscreen.is_program_locked() == False, "Unlock button shows after entering pin on full screen")

    ve_test.end()


@IHmark.O_Allianz
@IHmark.LV_L2
@pytest.mark.level2
def test_pin_retry_exhaust_linear():
    ve_test = VeTestApi("test_pin_retry_exhaust_linear")
    ve_test.begin()

    pincode = ve_test.screens.pincode
    zap_list = ve_test.screens.zaplist
    infolayer = ve_test.screens.infolayer
    playback = ve_test.screens.playback
    action_menu = ve_test.screens.linear_action_menu

    "Tune to youth channel"
    yp_channel = pincode.get_youth_channel(type=YouthChanneltype.ALL_EVENTS_PROTECTED)
    zap_list.tune_to_channel_by_sek(yp_channel)
    ve_test.log_assert(playback.is_video_hidden() == True, "Video Is not Hidden on Locked channel %s" % yp_channel)

    pincode.navigate()

    "enter wrong pin"
    for i in range(3):
        ve_test.wait(TIMEOUT)
        logging.info("enter wrong pin")
        wrong_pin = "7182"
        pincode.enter_pin(wrong_pin)

    pincode_invalid_msg = ve_test.milestones.get_dic_value_by_key('DIC_PIN_CODE_NO_MORE_RETRIES', 'general') % (10)
    pincode.verify_message(pincode_invalid_msg)


    "Get back to tuned channel"
    ve_test.screens.notification.go_to_previous_screen()

    "unlock from action Menu"
    infolayer.tap_unlock_program()
    ve_test.log_assert(pincode.verify_pin_blocked(), "User Blocked notification was not found!")

    ve_test.end()


@IHmark.O_Allianz
@IHmark.LV_L2
def test_vod_youthpin():
    ve_test = VeTestApi("test_vod_youthpin")
    ve_test.begin()
    pincode = ve_test.screens.pincode
    store = ve_test.screens.store
    action_menu = ve_test.screens.vod_action_menu
    playback = ve_test.screens.playback
    fullscreen = ve_test.screens.fullscreen

    "Tune to encrypted asset"
    pincode.navigate_to_low_rated_vod_asset()
    action_menu.play_asset(verify_streaming=False)
    ve_test.wait(TIMEOUT)
    ve_test.log_assert(playback.is_video_hidden() == False, "Video Is Hidden on Ecrypted asset")

    "Stop vod"
    action_menu.navigate()
    action_menu.press_stop()
    ve_test.wait(TIMEOUT)

    "Tune to youth asset"
    pincode.navigate_to_locked_vod_asset()
    action_menu.play_asset(verify_streaming=False)
    ve_test.wait(TIMEOUT)
    ve_test.log_assert(playback.is_video_hidden(), "Video Is not Hidden on Locked asset")

    pincode.navigate()

    "verify pin msg"
    retry = pincode.get_ctap_retry_count()
    pincode_enter_msg = ve_test.milestones.get_dic_value_by_key('DIC_PIN_CODE_ENTRY_RETRIES', 'general') % retry
    pincode.verify_message(pincode_enter_msg)

    "enter correct pin"
    logging.info("enter correct pin")
    pincode.enter_pin()
    fullscreen.verify_active()
    ve_test.wait(TIMEOUT)

    ve_test.end()

@pytest.mark.MF1232_youth_protected_vod
@pytest.mark.regression
@pytest.mark.export_regression_MF1232_youth_protected_vod
@IHmark.O_Allianz
@IHmark.LV_L2
@pytest.mark.level2
def test_pin_retry_exhaust_vod():
    ve_test = VeTestApi("test_pin_retry_exhaust_vod")
    ve_test.begin()
    pincode = ve_test.screens.pincode
    action_menu = ve_test.screens.vod_action_menu
    playback = ve_test.screens.playback

    "navigate to youth pin asset"
    pincode.navigate_to_locked_vod_asset()
    action_menu.play_asset(verify_streaming=False)
    ve_test.wait(TIMEOUT)
    ve_test.log_assert(playback.is_video_hidden() == True, "Video Is not Hidden on Locked asset")

    pincode.navigate()

    "verify pin msg"
    retry = pincode.get_ctap_retry_count()
    pincode_enter_msg = ve_test.milestones.get_dic_value_by_key('DIC_PIN_CODE_ENTRY_RETRIES', 'general') % retry
    pincode.verify_message(pincode_enter_msg)

    "enter wrong pin 3 times until blocked"
    logging.info("enter wrong pin %d times till pin validation is blocked" % retry)
    for i in range(1, retry + 1):
        wrong_pin = "7182"
        pincode.enter_pin(wrong_pin)
        if i == retry:
            blocking_time_minutes = pincode.get_expected_blocking_timeout_min()
            pincode_msg = ve_test.milestones.get_dic_value_by_key('DIC_PIN_CODE_NO_MORE_RETRIES',
                                                                  'general') % blocking_time_minutes
        else:
            pincode_msg = ve_test.milestones.get_dic_value_by_key('DIC_PIN_CODE_INVALID_RETRY', 'general') % (retry - i)
        pincode.verify_message(pincode_msg)

    ve_test.end()
