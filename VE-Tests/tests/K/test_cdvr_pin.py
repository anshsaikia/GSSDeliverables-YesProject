import pytest
import logging

from tests_framework.ve_tests.ve_test import VeTestApi

__author__ = 'guzan'

' Global constants '
TIMEOUT = 3
INVALID_PIN_CODE = "5050"
TUNING_WAIT = 10


@pytest.mark.parametrize("test_name, asset", [
    pytest.mark.test_record(("test_record", "single_event")),
    pytest.mark.test_episode_record(("test_episode_record", "episode")),
])
def a_test_generic_record(test_name, asset):
    test = VeTestApi(test_name)
    assets = test.assets
    test.begin()

    # record event and check the recording start
    asset = getattr(assets, asset)
    asset.labels_set() # Should be after test.begin()
    title = assets.generic_book_record_and_check(asset)

    # set pcThreshold to 7 and restart the application
    pincode = test.screens.pincode
    pincode.set_parental_rating_threshold(threshold=7)
    " relaunch app so new parental threshold will be cached"
    test.appium.restart_app()
    test.screens.tv_filter.verify_active()

    #Navigate to library and check pin is displayed on playback of the recording
    test.screens.library_filter.navigate()

    elements = test.milestones.getElementsArray([("event_type", "EVENT_CONTENT_TYPE_STANDALONE", "==")])
    test.appium.tap_element(elements[0])
    test.wait(3)
    test.screens.pvr_action_menu.play_asset(verify_streaming=False)

    test.screens.wait_for_screen(pincode, is_match=False,retries=40)
    pincode.enter_pin()
    test.wait(3)
    test.screens.playback.verify_streaming_playing()

    test.end()

@pytest.mark.parametrize("test_name, asset", [
    pytest.mark.test_record(("test_record", "single_event"))
])
def test_pin_retry_exhause(test_name, asset):
    test = VeTestApi(test_name)
    assets = test.assets
    test.begin()

    # record event and check the recording start
    asset = getattr(assets, asset)
    asset.labels_set()  # Should be after test.begin()
    title = assets.generic_book_record_and_check(asset)

    # set pcThreshold to 7 and restart the application
    pincode = test.screens.pincode
    pincode.set_parental_rating_threshold(threshold=7)
    " relaunch app so new parental threshold will be cached"
    test.appium.restart_app()
    test.screens.tv_filter.verify_active()

    # Navigate to library and check pin is displayed on playback of the recording
    test.screens.library_filter.navigate()

    elements = test.milestones.getElementsArray([("event_type", "EVENT_CONTENT_TYPE_STANDALONE", "==")])
    test.appium.tap_element(elements[0])
    test.wait(3)
    test.screens.pvr_action_menu.play_asset(verify_streaming=False)

    test.screens.wait_for_screen(pincode, is_match=False, retries=40)

    for i in range(0, 3):
        pincode.enter_pin(INVALID_PIN_CODE)
        test.wait(3)

    logging.info("3 TIMES WRONG PIN ENTRY FINISHED")
    test.wait(3)

    "verify if pin entry is disabled after 3 retries"
    test.log_assert(pincode.verify_pin_blocked(), "User Blocked notification was not found!")

    test.screens.notification.dismiss()
    test.wait(2)
    test.screens.vod_action_menu.play_asset(verify_streaming=False, verify_fullscreen=False)
    pincode.verify_active()
    test.wait(2)
    test.log_assert(pincode.verify_pin_blocked(), "User Blocked notification was not found!")

    test.end()

