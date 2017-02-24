from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.notification import Notification
import fabric.api as fab
import time

use_dummy_app = True

if use_dummy_app:
        PURCHASE_PIN = '1234'
        WRONG_PIN = '4321'
else:
        PURCHASE_PIN = '1111'
        WRONG_PIN = '4321'

def verify_pin_blocked(ve_test, time_pass):
    pin_exhaust_msg = ve_test.milestones.get_dic_value_by_key("DIC_PIN_CODE_INVALID_BLOCKED")
    value_time_left = time.time()-time_pass
    if(int(value_time_left)/60 == 0):
        time_left = 10-int(value_time_left)/60
    else:
        time_left = 10-int(value_time_left)/60 + 1
    pin_exhaust_msg = pin_exhaust_msg.replace("%1$s",str(time_left))
    element = ve_test.milestones.getElement([('title_text', pin_exhaust_msg, '==')])
    return element is not None

def verify_tvod_failed(ve_test):
    tvod_fail_message = ve_test.milestones.get_dic_value_by_key("DIC_ERROR_VOD_PURCHASE_FAILED")
    elements = ve_test.milestones.getElements()
    tvod_fail_message = ve_test.milestones.getElement([("title_text", tvod_fail_message, "==")], elements)
    ve_test.log_assert(tvod_fail_message, "wrong OSD")

def raise_tvod_action_menu(ve_test, title):
        tvod = ve_test.milestones.getElement([("title_text", title, "=="), ("name", "event_view", "==")])
        ve_test.appium.tap_element(tvod)
        ve_test.wait(2)

def re_select_asset_in_search_screen(ve_test, title, search):
        search.navigate()
        # we're back in previous search, re-select same asset
        raise_tvod_action_menu(ve_test,title)

def purchase_and_verify(ve_test, action_menu, pin, title):
        # purchase, enter pin & confirm
        notification = ve_test.screens.notification
        pincode = ve_test.screens.pincode
        action_menu.rent_asset()
        pincode.enter_pin(pin)
        if pin == PURCHASE_PIN:
            notification.verify_notification_message_by_key("DIC_TVOD_RENT_CONFIRMATION", "general")
            notification.get_and_tap_notification_button("DIC_ACTION_MENU_CONTINUE")
            ve_test.wait(3)

            if title != 'TVOD FAIL':
                # verify PLAY button and expiration date
                play_button = action_menu.verify_button(action_menu.button_type.PLAY)
                ve_test.log_assert(play_button, "PLAY button not found on screen")


def verify_youthPin_and_play_event(ve_test):
    pincode = ve_test.screens.pincode
    pincode.enter_pin(PURCHASE_PIN)
    ve_test.wait(2)
    ve_test.screens.playback.verify_streaming_playing()
    ve_test.log_assert('VOD' == ve_test.screens.playback.get_playback_status()["playbackType"], "playbackType is not VOD")
    ve_test.screens.fullscreen.verify_active()
    ve_test.end()


def test_tvod_actions():
    """
    US26293:
    Given that I have rented a TVOD for x days, when I raise the action menu within the rental duration, then I can view the related metadata of the vod rental as per spec (show rental duration, duration, etc,...)
    When I raise the action menu after x days had passed, then I can view the option to RENT again with the expected metadata as per spec (currency, rental duration, etc..)
    Given that I had rented the tvod again, then rental duration is updated accordingly on the rental in the action info.
    """
    if use_dummy_app:
        TITLE = 'TVOD PURCHASE'
    else:
        TITLE = 'TVODVE1'   # known TVOD asset

    ve_test = VeTestApi("test_tvod_actions")
    ve_test.begin()

    search = ve_test.screens.search
    action_menu = ve_test.screens.vod_action_menu


    # navigate to the known asset via search screen
    search.navigate()
    search.input_event_into_search_filed_and_search(TITLE)
    ve_test.wait(2)
    tvod = ve_test.milestones.getElement([("title_text", TITLE, "=="), ("name", "text_view", "==")])
    ve_test.appium.tap_element(tvod)
    ve_test.wait(2)
    raise_tvod_action_menu(ve_test, TITLE)
    #
    # TODO: verify rental duration, correct currency

    purchase_and_verify(ve_test, action_menu, PURCHASE_PIN, TITLE)

    # navigate again to same asset, verify that it's still purchased, now by playing
    re_select_asset_in_search_screen(ve_test, TITLE, search)

    # verify asset is playable
    action_menu.play_asset()

    # stop playback (goes back to action menu)
    ve_test.ui.center_tap()   # tap anywhere to raise ui
    ve_test.wait(2)
    # ve_test.ui.tap_element("exit") ### getElements is stuck in_transition when trickmode screen is raised, so meanwhile use hardcoded x, y
    ve_test.appium.tap(1948, 48)
    ve_test.wait(2)

    # trigger rental expiration
    if use_dummy_app:
        ve_test.milestones.post_milestones_request("setIsTvodPurchased", "[false]")
    else:
        # TODO: simulate rental expiration in HE
        pass

    # navigate again to same asset, verify that it's again purchasable
    re_select_asset_in_search_screen(ve_test, TITLE, search)

    # re-purchase, enter pin & confirm
    purchase_and_verify(ve_test,action_menu, PURCHASE_PIN, TITLE)

    ve_test.end()


def test_tvod_wrong_pin():
    if use_dummy_app:
        TITLE = 'TVOD PURCHASE'
    else:
        TITLE = 'TVODVE1'   # known TVOD asset

    ve_test = VeTestApi("test_tvod_wrong_pin")
    ve_test.begin()

    search = ve_test.screens.search
    action_menu = ve_test.screens.vod_action_menu

    # navigate to the known asset via search screen
    search.navigate()
    search.input_event_into_search_filed_and_search(TITLE)
    ve_test.wait(2)
    tvod = ve_test.milestones.getElement([("title_text", TITLE, "=="), ("name", "text_view", "==")])
    ve_test.appium.tap_element(tvod)
    ve_test.wait(2)
    raise_tvod_action_menu(ve_test, TITLE)

    purchase_and_verify(ve_test, action_menu, WRONG_PIN, TITLE)
    now_time = time.time()

    # insert if for dummy app vs real he and then check for OSD
    if use_dummy_app:
        verify_pin_blocked(ve_test, now_time)

    ve_test.end()


def test_tvod_fail():
    if use_dummy_app:
        TITLE = 'TVOD FAIL'
    else:
        TITLE = 'TVODVE1'   # known TVOD asset

    ve_test = VeTestApi("test_tvod_fail")
    ve_test.begin()

    search = ve_test.screens.search
    action_menu = ve_test.screens.vod_action_menu

    # navigate to the known asset via search screen
    search.navigate()
    search.input_event_into_search_filed_and_search(TITLE)
    ve_test.wait(2)
    tvod = ve_test.milestones.getElement([("title_text", TITLE, "=="), ("name", "text_view", "==")])
    ve_test.appium.tap_element(tvod)
    ve_test.wait(2)
    raise_tvod_action_menu(ve_test, TITLE)

    purchase_and_verify(ve_test, action_menu, PURCHASE_PIN, TITLE)

    verify_tvod_failed(ve_test)

    ve_test.end()

def test_tvod_erotic():
    if use_dummy_app:
        TITLE = 'TVOD EROTIC'
    else:
        TITLE = 'TVODVE1'   # known TVOD asset

    ve_test = VeTestApi("test_tvod_fail")
    ve_test.begin()

    search = ve_test.screens.search
    action_menu = ve_test.screens.vod_action_menu
    screen = ve_test.screen

    # navigate to the known asset via search screen
    search.navigate()
    search.input_event_into_search_filed_and_search(TITLE)
    ve_test.wait(2)
    tvod = ve_test.milestones.getElement([("title_text", TITLE, "=="), ("name", "text_view", "==")])
    ve_test.appium.tap_element(tvod)
    ve_test.wait(2)
    raise_tvod_action_menu(ve_test, TITLE)

    purchase_and_verify(ve_test, action_menu, PURCHASE_PIN, TITLE)

    # navigate again to same asset, verify that it's still purchased, now by playing
    re_select_asset_in_search_screen(ve_test, TITLE, search)

    # verify asset is playable
    action_menu.play_asset(False)
    screen.tap_unlock_program()
    ve_test.wait(2)
    verify_youthPin_and_play_event(ve_test)

