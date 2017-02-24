__author__ = 'gcohen'

import logging
import pytest
from tests_framework.ui_building_blocks.KD.pincode import YouthChanneltype
from tests_framework.ve_tests.ve_test import VeTestApi
from vgw_test_utils.IHmarks import IHmark

def get_time_left_till_end_of_event(test, event):
     start_time_utc = test.ctap_data_provider.get_event_time_utc(event['startDateTime'])
     now = test.ctap_data_provider.ve_test.appium.get_device_time() * 1000 #UTC timestamp in mili
     logging.info("now: %d, event start time: %d, duration=%d "%(now, start_time_utc, event['duration']))
     time_till_event_end = (event['duration'] -(now - start_time_utc)) / 1000 #return time in seconds
     return time_till_event_end

def get_alternately_yp_cur_event(test, alternately_yp_channel_id):
    cur_event = test.ctap_data_provider.get_current_event_by_id(alternately_yp_channel_id)
    time_till_event_end = get_time_left_till_end_of_event(test, cur_event)
    "to avoide event change before the test is ready"
    if time_till_event_end < 30 :
        test.wait(30 + 10)
    cur_event = test.ctap_data_provider.get_current_event_by_id(alternately_yp_channel_id)
    return cur_event

def event_change_parental_validation(test, cur_event):
    if test.screens.pincode.is_youth_event(cur_event):
        logging.info("event change from LOCK->UNLOCK")
        test.screens.fullscreen.tap_unlock_program()
        time_till_event_end = get_time_left_till_end_of_event(test, cur_event)
        test.wait(time_till_event_end + 10)
        test.screens.fullscreen.verify_active()
        test.log_assert(test.screens.fullscreen.is_program_locked() == False, "Unlock button was not dismiss after event change from lock to unlock")
        test.log_assert(test.screens.playback.is_video_hidden() == False, "Video Is Hidden after event change from lock to unlock")
    else:
         logging.info("event change from UNLOCK->LOCK")
         time_till_event_end = get_time_left_till_end_of_event(test, cur_event)
         test.wait(time_till_event_end + 10)
         test.log_assert(test.screens.fullscreen.is_program_locked(), "Unlock button is not showing after event change from unlock to lock")
         test.log_assert(test.screens.playback.is_video_hidden() == True, "Video Is not Hidden after event change from lock to unlock")


@IHmark.O_Allianz
def test_tune_to_youth_channel():
    ve_test = VeTestApi("test_tune_to_youth_channel")
    ve_test.begin()

    pincode = ve_test.screens.pincode
    zap_list = ve_test.screens.zaplist
    infolayer = ve_test.screens.infolayer
    action_menu = ve_test.screens.linear_action_menu
    playback = ve_test.screens.playback
    fullscreen = ve_test.screens.fullscreen

    "Tune to youth channel"
    yp_channel = pincode.get_youth_channel(type=YouthChanneltype.ALL_EVENTS_PROTECTED)
    zap_list.tune_to_channel_by_sek(yp_channel)
    infolayer.dismiss()
    ve_test.log_assert(playback.is_video_hidden() == True, "Video Is not Hidden on Locked channel %s" % yp_channel)

    "unlock from action Menu"
    action_menu.navigate()
    action_menu.tap_unlock_program()

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
    action_menu.verify_active()
    ve_test.log_assert(playback.is_video_hidden() == False, "Video Is Hidden after entering pin")
    ve_test.log_assert(action_menu.is_program_locked() == False, "Unlock button shows after entering pin on action_menu")
    #action_menu.go_to_previous_screen()
    action_menu.dismiss()
    fullscreen.verify_active()
    ve_test.log_assert(fullscreen.is_program_locked() == False, "Unlock button shows after entering pin on full screen")

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF511
@pytest.mark.MF511_youth_protected_linear
def test_blocking_pin_code_validation():
    ve_test = VeTestApi("test_blocking_pin_code_validation")
    ve_test.begin()

    pincode = ve_test.screens.pincode
    zap_list = ve_test.screens.zaplist
    infolayer = ve_test.screens.infolayer
    fullscreen = ve_test.screens.fullscreen
    playback = ve_test.screens.playback

    "Tune to youth channel"
    yp_channel = pincode.get_youth_channel(type = YouthChanneltype.ALL_EVENTS_PROTECTED)
    zap_list.tune_to_channel_by_sek(yp_channel, verify_streaming_started=False)

    "unlock from info layer"
    infolayer.verify_active()
    infolayer.tap_unlock_program()

    "enter wrong pin till pin validation is blocked"
    retry = pincode.get_ctap_retry_count()
    ve_test.log_assert(retry == pincode.RETRY_COUNT, "Ctap retry count %d is different than expected retry count %d" % (retry, pincode.RETRY_COUNT))
    logging.info("enter wrong pin %d times till pin validation is blocked" % retry)
    for i in range (1, retry+1):
        wrong_pin = "7182"
        pincode.enter_pin(wrong_pin)
        if i == retry:
            blocking_time_minutes = pincode.get_expected_blocking_timeout_min()
            pincode_msg =  ve_test.milestones.get_dic_value_by_key('DIC_PIN_CODE_NO_MORE_RETRIES', 'general') % blocking_time_minutes
        else:
            pincode_msg =  ve_test.milestones.get_dic_value_by_key('DIC_PIN_CODE_INVALID_RETRY', 'general') % (retry-i)
        pincode.verify_message(pincode_msg)

    pincode.go_to_previous_screen()
    infolayer.verify_active()

    "verify pincode is still block before blocking timeout passes"
    wait_time = (blocking_time_minutes * 60)/2
    ve_test.wait(wait_time)
    fullscreen.tap_unlock_program()
    pincode.verify_subscreen("messages")
    blocking_time_minutes = pincode.get_expected_blocking_timeout_min()
    pincode_block_msg =  ve_test.milestones.get_dic_value_by_key('DIC_PIN_CODE_LOCKED', 'general') % blocking_time_minutes
    pincode.verify_message(pincode_block_msg)

    "verify pincode screen dismiss after timeout"
    ve_test.wait(pincode.DISMISS_TIMEOUT_SEC + 10)
    ve_test.log_assert(pincode.is_active() == False, "Pinscreen was not dismiss after timeout (%d sec)" % pincode.DISMISS_TIMEOUT_SEC)

    "verify pincode entering is enable after blocking timeout"
    ve_test.wait(wait_time - pincode.DISMISS_TIMEOUT_SEC)
    infolayer.tap_unlock_program()
    pincode.enter_pin()
    fullscreen.verify_active()
    ve_test.log_assert(playback.is_video_hidden() == False, "Video Is Hidden after entering pin")

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF511
@pytest.mark.MF511_youth_protected_linear
def test_pincode_event_change():
    ve_test = VeTestApi("test_pincode_event_change")
    ve_test.begin()

    pincode = ve_test.screens.pincode
    zap_list = ve_test.screens.zaplist
    infolayer = ve_test.screens.infolayer
    playback = ve_test.screens.playback
    fullscreen = ve_test.screens.fullscreen

    "Tune to alternately youth channel"
    alternately_yp_channel = pincode.get_youth_channel(type = YouthChanneltype.ALTERNATELY_EVENTS_PROTECTED)
    zap_list.tune_to_channel_by_sek(alternately_yp_channel)
    infolayer.dismiss()

    "verify event change from [lock->unlock, unlock->lock]"
    cur_event = get_alternately_yp_cur_event(ve_test, alternately_yp_channel)
    event_change_parental_validation(ve_test, cur_event)
    cur_event = get_alternately_yp_cur_event(ve_test, alternately_yp_channel)
    event_change_parental_validation(ve_test, cur_event)

    "Tune to youth channel"
    yp_channel = pincode.get_youth_channel(type = YouthChanneltype.ALL_EVENTS_PROTECTED)
    zap_list.tune_to_channel_by_sek(yp_channel)

    "verify event change from lock->lock"
    logging.info("event change from LOCK->LOCK")
    infolayer.dismiss()
    fullscreen.tap_unlock_program()
    cur_event = ve_test.ctap_data_provider.get_current_event_by_id(yp_channel)
    time_till_event_end = get_time_left_till_end_of_event(ve_test, cur_event)
    ve_test.wait(time_till_event_end + 10)
    fullscreen.verify_active()
    ve_test.log_assert(fullscreen.is_program_locked(), "Unlock button is not showing after event change from lock to lock")
    ve_test.log_assert(playback.is_video_hidden() == True, "Video Is not Hidden after event change from lock to lock")
