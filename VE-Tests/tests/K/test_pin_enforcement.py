
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.pincode import YouthChanneltype
from tests_framework.he_utils.he_utils import VodContentType
from tests_framework.ui_building_blocks.KD.pincode import PinCodescreen
from vgw_test_utils.IHmarks import IHmark
import pytest
import logging

__author__ = 'dshalev'

' Global constants '
TIMEOUT = 3
INVALID_PIN_CODE = "5050"

# --------------------------- UTILS --------------------------


def tune_to_open_channel_and_verify_playing(ve_test, youth_channel_type=YouthChanneltype.CURRENT_EVENT_LOW_RATED):
    pincode = ve_test.screens.pincode
    channel = pincode.get_youth_channel(youth_channel_type)
    if channel is None:
        logging.error("couldn't find low rated linear channel")
        return False
    logging.info("found open channel: %s", channel)
    ve_test.screens.zaplist.tune_to_channel_by_sek(channel, False)
    ve_test.wait(TIMEOUT)
    if ve_test.screens.playback.is_video_hidden():
        logging.error("video is hidden")
        return False
    return True

# --------------------------- TESTS ---------------------------


@IHmark.LV_L1
@IHmark.O_Allianz
def test_pin_required_linear():
    ve_test = VeTestApi("test_pin_required_linear")
    pincode = ve_test.screens.pincode

    ve_test.begin()
    pincode.set_parental_rating_threshold()
    ve_test.wait(3)
    " relaunch app so new parental threshold will be cached"
    ve_test.appium.restart_app()
    ve_test.screens.tv_filter.verify_active()
    ve_test.log_assert(tune_to_open_channel_and_verify_playing(ve_test), "Failed while trying to tune to open channel")
    ve_test.log_assert(pincode.tune_to_locked_channel(), "Failed while trying to tune to locked channel")
    pincode.navigate()
    ve_test.wait(2)
    pincode.enter_pin()
    ve_test.wait(3)
    "verify if the content is playing"
    ve_test.log_assert(not ve_test.screens.infolayer.is_program_locked(), "Unlock button is showing after entering correct pin")
    ve_test.log_assert(not ve_test.screens.playback.is_video_hidden() == True, "Video Is Hidden after entering correct pin")

    logging.info('End test_pin_required_linear')
    ve_test.end()


@IHmark.LV_L2
@IHmark.O_Allianz
def test_pin_retry_exhaust_linear():
    ve_test = VeTestApi("test_pin_retry_exhaust_linear")
    pincode = ve_test.screens.pincode
    ve_test.begin()
    pincode.set_parental_rating_threshold()
    " relaunch app so new parental threshold will be cached"
    ve_test.wait(3)
    ve_test.appium.restart_app()
    ve_test.screens.tv_filter.verify_active()

    ve_test.log_assert(pincode.tune_to_locked_channel(), "Failed while trying to tune to locked channel")
    pincode.navigate()
    ve_test.wait(2)
    for i in range(0, 3):
        ve_test.wait(TIMEOUT)
        pincode.enter_pin(INVALID_PIN_CODE)

    logging.info("3 TIMES WRONG PIN ENTRY FINISHED")
    ve_test.wait(TIMEOUT)

    "verify if pin entry is disabled after 3 retries"
    ve_test.log_assert(pincode.verify_pin_blocked(), "User Blocked notification was not found!")

    ve_test.screens.notification.dismiss()
    pincode.navigate()
    ve_test.wait(3)
    ve_test.log_assert(pincode.verify_pin_blocked(), "User Blocked notification was not found!")

    logging.info('End test_retry_exhaust_linear')
    ve_test.end()


@IHmark.LV_L1
@IHmark.O_Allianz
def test_pin_required_vod():
    ve_test = VeTestApi("test_pin_required_vod")
    pincode = ve_test.screens.pincode
    ve_test.begin(preload="vod")

    pincode.set_parental_rating_threshold()
    ve_test.wait(3)
    " relaunch app so new parental threshold will be cached"
    ve_test.appium.restart_app()
    ve_test.screens.tv_filter.verify_active()
    " playing low rated vod asset"
    pincode.navigate_to_low_rated_vod_asset()
    ve_test.wait(4)
    ve_test.screens.vod_action_menu.play_asset()
    ve_test.wait(2)
    ve_test.screens.trick_bar.navigate()
    ve_test.wait(2)
    " playing pin protected VOD asset"
    pincode.navigate_to_locked_vod_asset()
    ve_test.wait(4)
    pincode.navigate()
    ve_test.wait(2)
    ve_test.screens.playback.verify_streaming_paused()
    logging.info('Playback paused as expected')
    pincode.enter_pin()
    ve_test.wait(3)
    ve_test.screens.playback.verify_streaming_playing()

    ve_test.end()


@IHmark.LV_L2
@IHmark.O_Allianz
def test_pin_retry_exhaust_vod():
    ve_test = VeTestApi("test_pin_retry_exhaust_vod")
    pincode = ve_test.screens.pincode
    ve_test.begin(preload="vod")

    pincode.set_parental_rating_threshold()
    ve_test.wait(3)
    " relaunch app so new parental threshold will be cached"
    ve_test.appium.restart_app()
    ve_test.screens.tv_filter.verify_active()
    pincode.navigate_to_locked_vod_asset()
    ve_test.wait(2)
    pincode.navigate()
    ve_test.wait(2)
    ve_test.screens.playback.verify_streaming_paused()
    logging.info('Playback paused as expected')
    for i in range(0, 3):
        pincode.enter_pin(INVALID_PIN_CODE)
        ve_test.wait(3)

    logging.info("3 TIMES WRONG PIN ENTRY FINISHED")
    ve_test.wait(3)

    "verify if pin entry is disabled after 3 retries"
    ve_test.log_assert(pincode.verify_pin_blocked(), "User Blocked notification was not found!")

    ve_test.screens.notification.dismiss()
    ve_test.wait(2)
    ve_test.screens.vod_action_menu.play_asset(verify_streaming=False, verify_fullscreen=False)
    pincode.verify_active()
    ve_test.wait(2)
    ve_test.log_assert(pincode.verify_pin_blocked(), "User Blocked notification was not found!")

    ve_test.end()
