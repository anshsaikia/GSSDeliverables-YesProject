__author__ = 'bbagland'


from tests_framework.ui_building_blocks.KSTB.error import *
from tests_framework.ve_tests.ve_test import VeTestApi
import pytest
import logging

def check_last_error(ve_test,error_type):
        screen = ve_test.milestones.get_current_screen();
        ve_test.logger.log_assert(screen == "fullscreen", "Current screen is '" + str(screen) + "', expected 'fullscreen'")
        elements = ve_test.milestones.getElements()
        last_error_type = ve_test.milestones.get_value_by_key(elements, "last_error_type")
        if last_error_type:
            return last_error_type == error_type
        else:
            logging.info("No last error available")
            return False

def network_recovery(ve_test):
    """
    Disable the wifi during 2 minutes and check the error has been really detected
    :param ve_test: The test instance in progress
    :return: Assert failed if the last error type is not a network connection loss
    """
    prev_playback_status = ve_test.screens.playback.verify_streaming_playing()
    prev_url = prev_playback_status['sso']['sessionPlaybackUrl']
    ve_test.wifi_disconnect()
    # shall wait enough to be sure the network error is detected
    ve_test.wait(120)
    ve_test.wifi_connect()
    # shall wait enough to be sure the playback started again
    ve_test.wait(30)
    current_playback_status = ve_test.screens.playback.verify_streaming_playing()
    current_url = current_playback_status['sso']['sessionPlaybackUrl']
    ve_test.log_assert(current_url == prev_url, "Current playback is '" + str(current_url) + "', expected : '" + str(prev_url) +"'")
    ve_test.log_assert(check_last_error(ve_test, E_NETWORK_ERROR_TYPE), "Last Error is not Network")

@pytest.mark.sanity
@pytest.mark.wifi
@pytest.mark.FS_Live
@pytest.mark.LV_L3
def test_wifi_connect_live():
    """
    Start on the full screen
    Check the stream is playing
    Disable the wifi connexion
    Wait about two minutes
    Enable the wifi connexion
    Check the last displayed error is network error ERR-101
    :return: assert is failed if the no network error detected
    """
    ve_test = VeTestApi("test_wifi_connect_live")
    ve_test.begin(screen=ve_test.screens.fullscreen) 
    network_recovery(ve_test)
    ve_test.end()


@pytest.mark.sanity
@pytest.mark.wifi
@pytest.mark.FS_VOD
@pytest.mark.LV_L3
def test_wifi_connect_vod():
    """
    Start on the full screen
    Check the stream is playing
    Disable the wifi connexion
    Wait about two minutes
    Enable the wifi connexion
    Check the last displayed error is network error ERR-101
    :return: assert is failed if the no network error detected
    """
    test = VeTestApi("test_wifi_connect_vod")
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    status = test.screens.playback.vod_manager.start_free_playback(12)
    test.log_assert(status, "Can start the VOD asset")
    network_recovery(test)
    test.end()