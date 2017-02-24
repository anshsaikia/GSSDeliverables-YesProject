__author__ = 'upnidhi'


import pytest
import logging
from time import sleep
from tests_framework.ve_tests.ve_test import VeTestApi


' Global constants '
TIMEOUT = 3
INVALID_PIN_CODE = "1234"
YOUTHPINCODE = "0098"

FSK16_CHANNEL_ID = "151"
CHANNEL_ID = "152"

@pytest.mark.reg_MF460_youth_protection
@pytest.mark.MF460_youth_protection
#MF460 - Youth Protection [Android]
def test_pin_required():
    ve_test = VeTestApi("test_pin_required")
    ve_test.begin()

    "setting YouthPincode"
    hhId = ve_test.configuration["he"]["generated_household"]
    ve_test.he_utils.setYouthPin(hhId, YOUTHPINCODE)

    "Tune to channel with FSK 16 content"
    ve_test.screens.zaplist.tune_to_channel_by_sek(FSK16_CHANNEL_ID)
    sleep(TIMEOUT)

    "Pin screen appears"
    ve_test.screens.pincode.verify_active()
    sleep(TIMEOUT)
    "enter pin"
    ve_test.screens.pincode.enter_pin(YOUTHPINCODE)
    "verify if the content is playing"
    ve_test.screens.playback.verify_streaming_playing()

    logging.info('End test_pin_required')
    ve_test.end()

@pytest.mark.reg_MF460_youth_protection
@pytest.mark.MF460_youth_protection
#MF460 - Youth Protection [Android]
def test_no_pin_required():
    ve_test = VeTestApi("test_no_pin_required")
    ve_test.begin()

    "setting YouthPincode"
    hhId = ve_test.configuration["he"]["generated_household"]
    ve_test.he_utils.setYouthPin(hhId, YOUTHPINCODE)

    "Tune to channel with no FSK 16 content"
    ve_test.screens.zaplist.tune_to_channel_by_sek(CHANNEL_ID)
    sleep(TIMEOUT)
    "Infolayer screen"
    ve_test.log_assert(ve_test.screens.infolayer.is_active(timeout=10), "No infolayer screen" )
    sleep(TIMEOUT)

    "verify if the content is playing"
    ve_test.screens.playback.verify_streaming_playing()
    logging.info('End test_no_pin_required')
    ve_test.end()

@pytest.mark.reg_MF460_youth_protection
@pytest.mark.MF460_youth_protection
#MF460 - Youth Protection [Android]
def test_pin_validation():
    ve_test = VeTestApi("test_pin_validation")
    ve_test.begin()

    "setting YouthPincode"
    hhId = ve_test.configuration["he"]["generated_household"]
    ve_test.he_utils.setYouthPin(hhId, YOUTHPINCODE)

    "Tune to channel with FSK 16 content"
    ve_test.screens.zaplist.tune_to_channel_by_sek(FSK16_CHANNEL_ID)
    sleep(TIMEOUT)

    "Pin screen appears"
    ve_test.screens.pincode.verify_active()
    sleep(TIMEOUT)
    "enter invalid pin"
    ve_test.screens.pincode.enter_pin(INVALID_PIN_CODE)
    "verify if the current screen is still pinscreen"
    ve_test.screens.pincode.verify_active()
    sleep(TIMEOUT)
    "enter valid pin"
    ve_test.screens.pincode.enter_pin(YOUTHPINCODE)
    "verify if the content is playing"
    ve_test.screens.playback.verify_streaming_playing()

    logging.info('End test_pin_validation')
    ve_test.end()

@pytest.mark.MF460_youth_protection
#MF460 - Youth Protection [Android]
def test_retry_exhaust():
    ve_test = VeTestApi("test_retry_exhaust")
    ve_test.begin()

    "setting YouthPincode"
    hhId = ve_test.configuration["he"]["generated_household"]
    ve_test.he_utils.setYouthPin(hhId, YOUTHPINCODE)

    "Tune to channel with FSK 16 content"
    ve_test.screens.zaplist.tune_to_channel_by_sek(FSK16_CHANNEL_ID)
    sleep(TIMEOUT)

    "Pin screen appears"
    ve_test.screens.pincode.verify_active()
    sleep(TIMEOUT)

    "Enter invalid pin thrice"
    for i in range(0,3):
        ve_test.screens.pincode.enter_pin(INVALID_PIN_CODE)

    "verify if pin entry is disabled after 3 retries"
    ve_test.screens.pincode.verify_pin_entry_disabled()

    logging.info('End test_retry_exhaust')
    ve_test.end()