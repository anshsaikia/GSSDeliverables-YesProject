__author__ = 'tchevall'

import pytest
import types
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KSTB.playback import LIVE_PLAYBACK_TYPE
from tests_framework.milestones.milestones_kpi_request_parser import KpiRequestParserAPI


' Global constants '
ZAPPING_LOOP_NUMBER = 500

# Different timings
TUNING_WIFI_WAIT = 10
TUNING_ETHERNET_WAIT = 5
TUNING_INFINITE_WAIT = 8
PROFILE_UPDATE = 10

NUMBER_OF_P_PLUS = 5
MAX_NUMBER_OF_ERROR = 100
MAX_AUTHORIZED_RETRY = 15


# Try to zap ZAPPING_LOOP_NUMBER times, accepting MAX_NUMBER_OF_ERROR, with NUMBER_OF_P_PLUS zapping with P+, then  P-
def internal_robustness_zapping_to_next_channel(ve_test, network_mode, expected_duration):
    remaining_zapping_number = ZAPPING_LOOP_NUMBER
    number_error_displayed = 0
    i = 0
    while remaining_zapping_number > 0 and number_error_displayed < MAX_NUMBER_OF_ERROR:
        print "test_zapping : remaining="+str(remaining_zapping_number) + " -- number_error_displayed="+str(number_error_displayed)
        # Zap
        if i < NUMBER_OF_P_PLUS:
            print "test_zapping : Zapp to next channel"
            ve_test.screens.playback.zap_to_next_channel(expected_duration)

        else:
            print "test_zapping : Zapp to previous channel"
            ve_test.screens.playback.zap_to_previous_channel(expected_duration)

        i = (i+1) % 10

        # Check if the zapping succeed
        playback_status = ve_test.milestones.getPlaybackStatus()
        print "test_zapping : playback status = " + playback_status["playbackState"]
        if playback_status["playbackState"] == "PLAYING":
            print "    ---> Zapping OK"
            remaining_zapping_number -= 1
        else:
            print "    ---> Zapping KO : checking notification"
            # An error should be displayed
            currentScreen = ""
            retry = 0
            # Check x times until a screen is shown
            while currentScreen != "notification" and retry < MAX_AUTHORIZED_RETRY:
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

            # To be improved
            if currentScreen:
                ve_test.check_notification_screen(True)
            number_error_displayed += 1

    ve_test.screens.playback.kpi_to_html(ve_test,LIVE_PLAYBACK_TYPE)
    request = ve_test.milestones.getLiveKpiMeasurement()
    parserApi = KpiRequestParserAPI(request)
    ve_test.log_assert( number_error_displayed < MAX_NUMBER_OF_ERROR , "Too many errors displayed ( " + str(number_error_displayed) + " errors )")
    ve_test.log_assert(parserApi.getMaxPlaybackStartSequenceDuration() < expected_duration * 1000, ("A zapping took more than ( " + str(expected_duration) + "seconds )"))
    ve_test.log_assert(parserApi.getSuccessPlaybackNb() >= ZAPPING_LOOP_NUMBER, "The number of reached zapping is incorrect")


def internal_infinite_zapping_to_next_channel(ve_test, expected_duration):
    ve_test.screens.playback.zap_to_previous_channel(expected_duration)
    while True:
        for i in range(1,10):
             # Second step, send a P+ event, in order to zap to next channel
            ve_test.screens.playback.zap_to_next_channel(expected_duration)
            ve_test.screens.playback.verify_streaming_playing_kpi(LIVE_PLAYBACK_TYPE)
        for i in range(1,10):
            #third step, send a P- event in order to zap to previous channel
            ve_test.screens.playback.zap_to_previous_channel(expected_duration)
            ve_test.screens.playback.verify_streaming_playing_kpi(LIVE_PLAYBACK_TYPE)


@pytest.mark.robustness
@pytest.mark.FS_Live
@pytest.mark.ethernet
@pytest.mark.short
@pytest.mark.LV_L4
def test_robustness_zapping_to_next_channel_ethernet():
    ve_test = VeTestApi("test_zapping_robustness_ethernet")
    ve_test.begin(screen=ve_test.screens.fullscreen) 
    internal_robustness_zapping_to_next_channel(ve_test, "Ethernet", TUNING_ETHERNET_WAIT)
    ve_test.end()

@pytest.mark.robustness
@pytest.mark.FS_Live
@pytest.mark.ethernet
@pytest.mark.short
@pytest.mark.LV_L4
def test_robustness_zapping_to_next_channel_ethernet_profile_update():
    ve_test = VeTestApi("test_zapping_robustness_ethernet_profile_update")
    ve_test.begin(screen=ve_test.screens.fullscreen) 
    internal_robustness_zapping_to_next_channel(ve_test, "Ethernet", TUNING_ETHERNET_WAIT + PROFILE_UPDATE)
    ve_test.end()


@pytest.mark.robustness
@pytest.mark.FS_Live
@pytest.mark.wifi
@pytest.mark.short
@pytest.mark.LV_L4
def test_robustness_zapping_to_next_channel_wifi():
    ve_test = VeTestApi("test_zapping_robustness_wifi")
    ve_test.begin(screen=ve_test.screens.fullscreen) 
    internal_robustness_zapping_to_next_channel(ve_test, "Wifi", TUNING_WIFI_WAIT)
    ve_test.end()


@pytest.mark.robustness
@pytest.mark.FS_Live
@pytest.mark.wifi
@pytest.mark.short
@pytest.mark.LV_L4
def test_robustness_zapping_to_next_channel_wifi_profile_update():
    ve_test = VeTestApi("test_zapping_robustness_wifi_profile_update")
    ve_test.begin(screen=ve_test.screens.fullscreen) 
    internal_robustness_zapping_to_next_channel(ve_test, "Wifi", TUNING_WIFI_WAIT + PROFILE_UPDATE)
    ve_test.end()
    
    
@pytest.mark.robustness
@pytest.mark.FS_Live
@pytest.mark.ethernet
@pytest.mark.wifi
@pytest.mark.LV_L4
def test_robustness_infinite_zapping_to_next_channel():
    ve_test = VeTestApi("test_zapping_robustness_infinite")
    ve_test.begin(screen=ve_test.screens.fullscreen) 
    internal_infinite_zapping_to_next_channel(ve_test, TUNING_INFINITE_WAIT)
    ve_test.end()

