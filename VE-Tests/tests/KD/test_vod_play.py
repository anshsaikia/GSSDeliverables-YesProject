__author__ = 'abarilan'
#__author__ = 'mibenami'

from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.he_utils.he_utils import VodContentType
from vgw_test_utils.IHmarks import IHmark
import logging
import pytest

TIMEOUT = 4

@IHmark.FS_Playback
@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
# @IHmark.F_Playback_VOD
@pytest.mark.level2
def test_play_vod():
    test = VeTestApi("test_play_vod")
    test.begin(preload="vod")

    asset = test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.ENCRYPTED, VodContentType.LOW_RATED, VodContentType.NON_EROTIC], {'policy':'false'})
    test.screens.store.play_vod_by_title(asset['title'])
    test.wait(10)

    test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF1209
@IHmark.MF946
@IHmark.MF259
@pytest.mark.MF1209_vod_drm
@pytest.mark.MF946_watch_vod
@pytest.mark.MF259_playvod
def test_play_vod_gestures():
    test = VeTestApi("test_play_vod_gestures")
    test.begin()

    asset = test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.ENCRYPTED, VodContentType.LOW_RATED, VodContentType.NON_EROTIC], {'policy':'false'})
    test.screens.store.play_vod_by_title(asset['title'])

    logging.info("horizontal swipe")
    #from timeline
    window_width, window_height = test.milestones.getWindowSize()
    y = window_height/2
    left_x = window_width*0.1
    right_x = window_width*0.75
    test.mirror.swipe_area(right_x, y, left_x, y)
    test.wait(2)
    current_screen = test.milestones.get_current_screen()
    test.log_assert(current_screen == "fullscreen", "horizontal swipe caused current screen to become: " + current_screen + " instead of fullscreen")

    logging.info("vertical swipe")
    #from timeline
    x = window_width/2
    upper_y = window_height*0.35
    lower_y = window_height*0.75
    for retry in range(2):
        test.appium.swipe_area(x, upper_y, x, lower_y)
    test.wait(2)
    current_screen = test.milestones.get_current_screen()
    test.log_assert(current_screen == "fullscreen", "vertical swipe caused current screen to become: " + current_screen + " instead of fullscreen")

    logging.info("tap")
    actionMenu = test.screens.vod_action_menu
    actionMenu.navigate()

    test.end()

"""Remove authorization and check if the 'play' option is absent"""
@IHmark.LV_L2
#@IHmark.O_iOS
#@IHmark.O_Android
@IHmark.MF258
@IHmark.MF1119
@pytest.mark.MF258_vod_entitlement
@pytest.mark.MF1119_vod_entitlement
@pytest.mark.export_regression_vod_play
@pytest.mark.regression
@pytest.mark.level2
def test_vod_entitlement():
    ve_test = VeTestApi("test_vod_entitlement")
    vod_action_menu = ve_test.screens.vod_action_menu
    store = ve_test.screens.store

    ve_test.begin()

    svod_offers, tvod_offers = ve_test.he_utils.getAllOffers()
    ve_test.say("removing s-v-o-d offers at head-end")
    ve_test.he_utils.setHouseHoldAuthorization(ve_test.he_utils.default_credentials[0], svod_offers,remove=True)

    asset = ve_test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.ENCRYPTED, VodContentType.LOW_RATED, VodContentType.NON_EROTIC], {'policy':'false'})
    store.navigate_to_vod_asset_by_title(asset['title'])
    ve_test.screens.vod_action_menu.verify_play_menu(present=False)

    ve_test.say("restoring offers for user at head-end")
    ve_test.he_utils.setHouseHoldAuthorization(ve_test.he_utils.default_credentials[0], svod_offers)
    store.go_to_previous_screen()
    store.select_event_by_title(asset['title'])
    ve_test.screens.vod_action_menu.verify_play_menu(present=True)

    ve_test.say("removing s-v-o-d offers")
    ve_test.he_utils.setHouseHoldAuthorization(ve_test.he_utils.default_credentials[0], svod_offers,remove=True)

    ve_test.say("Trying to play the non-entitled asset. Expecting an error!")
    ve_test.screens.vod_action_menu.play_asset(verify_streaming=False, verify_fullscreen=False)
    ve_test.wait(2)
    playback_status = ve_test.screens.playback.get_playback_status()
    ve_test.log_assert(playback_status["playbackState"] == "STOPPED", "content playing after authorization removed. playback_state= % s" % playback_status["playbackState"])

    notification = ve_test.screens.notification
    notification.verify_notification_message_by_key("DIC_ERROR_PLAYBACK_CONTENT_NOT_ENTITLED")
    notification.dismiss_notification()

    vod_action_menu.navigate()

    ve_test.say("verifying PLAY button not existing")
    vod_action_menu.verify_play_menu(present=False)

    ve_test.say("Restoring offers for user at head-end")
    ve_test.he_utils.setHouseHoldAuthorization(ve_test.he_utils.default_credentials[0], svod_offers)

    vod_action_menu.dismiss()
    vod_action_menu.navigate()
    vod_action_menu.play_asset(verify_streaming=True)
    ve_test.end()

@pytest.mark.MF1232_youth_protected_vod
@pytest.mark.export_regression_youth_vod
@pytest.mark.regression
@pytest.mark.level2
@IHmark.LV_L2
def test_vod_youthpin():
    ve_test = VeTestApi("test_vod_youthpin")
    ve_test.begin()
    pincode = ve_test.screens.pincode
    store = ve_test.screens.store
    action_menu = ve_test.screens.vod_action_menu
    playback = ve_test.screens.playback
    fullscreen = ve_test.screens.fullscreen
    infolayer = ve_test.screens.infolayer

    "Tune to youth asset"
    yp_asset = pincode.get_youth_asset()
    store.navigate_to_vod_asset_by_title(yp_asset['title'])
    action_menu.play_asset(verify_streaming=False)
    ve_test.wait(TIMEOUT)
    ve_test.log_assert(playback.is_video_hidden() == True, "Video Is not Hidden on Locked asset %s" % yp_asset['title'])

    infolayer.tap_unlock_program()

    "verify pin msg"
    retry = pincode.get_ctap_retry_count()
    pincode_enter_msg = ve_test.milestones.get_dic_value_by_key('DIC_PIN_CODE_ENTRY_RETRIES', 'general') % retry
    pincode.verify_message(pincode_enter_msg)

    "enter correct pin"
    logging.info("enter correct pin")
    pincode.enter_pin()
    fullscreen.verify_active()
    ve_test.wait(TIMEOUT)

    "navigate again to pin entry screen"
    action_menu.navigate()
    action_menu.press_stop()
    ve_test.wait(TIMEOUT)

    "navigate to asset again and retry"
    store.navigate_to_vod_asset_by_title(yp_asset['title'])
    action_menu.play_asset(verify_streaming=False)
    ve_test.wait(TIMEOUT)
    ve_test.log_assert(playback.is_video_hidden() == True, "Video Is not Hidden on Locked asset %s" % yp_asset['title'])

    infolayer.tap_unlock_program()

    "enter wrong pin 3 times until blocked"
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

    ve_test.end()