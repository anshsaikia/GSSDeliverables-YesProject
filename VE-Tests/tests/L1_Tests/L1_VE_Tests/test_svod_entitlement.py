from tests_framework.ve_tests.ve_test import VeTestApi
import pytest
import logging
import random
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition

TIMEOUT = 4
AVERAGE_WAIT_TIME=3
MIN_WAIT_TIME = 3

@pytest.mark.level1
def test_svod_entitlement():
    ve_test = VeTestApi("test_svod_entitlement")
    ve_test.begin()
    vod_action_menu = ve_test.screens.vod_action_menu
    if ve_test.project_type == "KD":
        #vod_asset_position = random.choice(list(EventViewPosition))
        vod_asset_position = EventViewPosition.left_event
    else:
        vod_asset_position = 0

    logging.info ("VOD_ASSET_POSITION={}".format(vod_asset_position))

    svod_offers, tvod_offers = ve_test.he_utils.getAllOffers()
    ve_test.say("removing SVOD offers at head-end by BOA")
    offer_keys = ve_test.he_utils.getOfferKey(svod_offers)
    for offer_key in offer_keys:
        ve_test.he_utils.deleteAuthorizationSubscriptionUsingBoa(ve_test.he_utils.default_credentials[0],offer_key, "KD-SERVICES")

    ve_test.startup_screen.open_vod_action_menu_by_position(vod_asset_position)
    ve_test.wait(AVERAGE_WAIT_TIME)
    pin_screen = ve_test.screens.pincode

    elements = ve_test.milestones.getElements()
    events = ve_test.milestones.getElementsArray([("name", "event_view", "==")], elements)

    #asset_title = events[0]['title_text']
    asset_title = "Awakening"

    ve_test.screens.vod_action_menu.verify_play_menu(present=False)

    ve_test.say("restoring offers for user at head-end")
    for offer_key in offer_keys:
        ve_test.he_utils.addAuthorizationSubscriptionUsingBoa(ve_test.he_utils.default_credentials[0],"SUBSCRIPTION",offer_key, "KD-SERVICES")

    ve_test.screens.vod_action_menu.go_to_previous_screen()
    ve_test.startup_screen.open_vod_action_menu_by_position(vod_asset_position)
    ve_test.screens.vod_action_menu.verify_play_menu(present=True)
    ve_test.say("removing SVOD offers")
    for offer_key in offer_keys:
        ve_test.he_utils.deleteAuthorizationSubscriptionUsingBoa(ve_test.he_utils.default_credentials[0],offer_key, "KD-SERVICES")
    ve_test.say("Trying to play the non-entitled asset. Expecting an error!")
    ve_test.screens.vod_action_menu.play_asset(verify_streaming=False, verify_fullscreen=False)
    ve_test.wait(2)     # wait to get playback_state==STOPPED, otherwise it is SETUP.
    playback_status = ve_test.screens.playback.get_playback_status()
    ve_test.log_assert(playback_status["playbackState"] == "STOPPED", "content playing after authorization removed. playback_state= % s" % playback_status["playbackState"])

    notification = ve_test.screens.notification
    notification.verify_notification_message_by_key("DIC_ERROR_PLAYBACK_CONTENT_NOT_ENTITLED")
    notification.dismiss_notification()

    vod_action_menu.navigate()
    ve_test.say("verifying WATCH button not existing")
    vod_action_menu.verify_play_menu(present=False)
    ve_test.say("Restoring offers for user at head-end")
    for offer_key in offer_keys:
        ve_test.he_utils.addAuthorizationSubscriptionUsingBoa(ve_test.he_utils.default_credentials[0],"SUBSCRIPTION",offer_key, "KD-SERVICES")
    vod_action_menu.dismiss()

    #ve_test.screens.vod_action_menu.go_to_previous_screen()
    ve_test.startup_screen.navigate()
    ve_test.startup_screen.open_vod_action_menu_by_position(vod_asset_position)

    ve_test.screens.vod_action_menu.play_restart_asset()
    ve_test.wait(TIMEOUT)
    unlock_button = ve_test.screens.infolayer.is_program_locked()
    if unlock_button :
        ve_test.log_assert(unlock_button, "Program is not Locked. No Unlock button on the Screen")
        ve_test.appium.tap_center_element(unlock_button)

        "verify pin msg"
        retry = pin_screen.get_ctap_retry_count()
        pincode_enter_msg = ve_test.milestones.get_dic_value_by_key('DIC_PIN_CODE_ENTRY_RETRIES', 'general') % retry
        pin_screen.verify_message(pincode_enter_msg)

        "enter correct pin"
        logging.info("enter correct pin")
        pin_screen.enter_pin()
        ve_test.screens.fullscreen.verify_active()
    playback_state = ve_test.screens.playback.get_playback_status()["playbackState"]
    logging.info ("Playing SVOD asset : {}, playback_status = {}".format(asset_title,playback_state))
    ve_test.end()

