__author__ = 'tchevall'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.milestones.milestones_kpi_request_parser import KpiRequestParserAPI
from tests_framework.ui_building_blocks.KSTB.playback import LIVE_PLAYBACK_TYPE
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS

import types
' Global constants '
NUMBER_OF_STREAM_SWITCH_TESTS = 10
NUMBER_OF_P_PLUS = 5
MAX_NUMBER_OF_ERROR = 20
MAX_AUTHORIZED_RETRY = 15

# 2 different timings
TUNING_WIFI_WAIT = 10
TUNING_ETHERNET_WAIT = 5


# Try to zapp NUMBER_OF_STREAM_SWITCH_TESTS times, accepting MAX_NUMBER_OF_ERROR, with NUMBER_OF_P_PLUS zapping with P+, and same with P-
def internal_zapping_to_next_channel(ve_test, network_mode, expected_duration):
    remaining_zapping_number = NUMBER_OF_STREAM_SWITCH_TESTS
    number_error_displayed = 0
    i = 0
    while (remaining_zapping_number > 0 and number_error_displayed < MAX_NUMBER_OF_ERROR):
        print "test_zapping : remaining="+str(remaining_zapping_number) + " -- number_error_displayed="+str(number_error_displayed)
        # Zapp
        if (i < NUMBER_OF_P_PLUS):
            print "test_zapping : Zapp to next channel"
            ve_test.screens.playback.zap_to_next_channel(expected_duration)
        else:
            print "test_zapping : Zapp to previous channel"
            ve_test.screens.playback.zap_to_previous_channel(expected_duration)
        i = (i+1) % NUMBER_OF_STREAM_SWITCH_TESTS
        # Check if the zapping succeed
        playback_status = ve_test.milestones.getPlaybackStatus()
        print "test_zapping : playback status = "+ playback_status["playbackState"]
        if (playback_status["playbackState"] == "PLAYING" ):
            print "    ---> Zapping OK"
            remaining_zapping_number -= 1
        else:
            print "    ---> Zapping KO : checking notification"
            # An error should be displayed
            currentScreen = ""
            retry = 0
            # Check x times until a screen is shown
            while (currentScreen != "notification" and retry < MAX_AUTHORIZED_RETRY):
                elements = ve_test.milestones.getElements()
                screen = ve_test.milestones.get_value_by_key(elements, "screen_name")
                retry += 1
                if type(screen) == types.BooleanType:
                    print "test_zapping : A notification is not displayed on service " + playback_status['sso']['sessionPlaybackUrl']
                    ve_test.wait(2)
                else :
                    currentScreen = screen
                    text = ve_test.milestones.get_value_by_key(elements, "msg_text")
                    print "test_zapping : A notification ("+ text +")is displayed on service " + playback_status['sso']['sessionPlaybackUrl']

            notification = ve_test.check_notification_screen(True)
            number_error_displayed += 1

    ve_test.screens.playback.kpi_to_html(LIVE_PLAYBACK_TYPE)
    request = ve_test.milestones.getLiveKpiMeasurement()
    parserApi = KpiRequestParserAPI(request)
    ve_test.log_assert( number_error_displayed < MAX_NUMBER_OF_ERROR , "Too many errors displayed ( "+ str(MAX_NUMBER_OF_ERROR) +")")
    ve_test.log_assert(parserApi.getMaxPlaybackStartSequenceDuration() < expected_duration * 1000, ("[%s] A zapping took more than %ds to be displayed", network_mode, str(expected_duration)))
    ve_test.log_assert(parserApi.getSuccessPlaybackNb() == NUMBER_OF_STREAM_SWITCH_TESTS + 1, "A zapping has failed")


@pytest.mark.FS_Live
@pytest.mark.non_regression
@pytest.mark.ethernet
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_zapping
def test_unitary_zapping_to_next_channel_ethernet():
    ve_test = VeTestApi("test_unitary_zapping_to_next_channel_ethernet")
    ve_test.begin(screen=ve_test.screens.fullscreen) 
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    internal_zapping_to_next_channel(ve_test, "Ethernet", TUNING_ETHERNET_WAIT)
    ve_test.end()

@pytest.mark.FS_Live
@pytest.mark.non_regression
@pytest.mark.wifi
@pytest.mark.LV_L2
def test_unitary_zapping_to_next_channel_wifi():
    ve_test = VeTestApi("test_unitary_zapping_to_next_channel_wifi")
    ve_test.begin(screen=ve_test.screens.fullscreen) 
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    internal_zapping_to_next_channel(ve_test, "Wifi", TUNING_WIFI_WAIT)
    ve_test.end()


