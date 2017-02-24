__author__ = 'oceane'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
import tests.KSTB.android.kpi_tests.kpi_utils as kpi_utils
from tests_framework.milestones.milestones_kpi_request_parser import KpiRequestParserAPI
from tests_framework.ui_building_blocks.KSTB.playback import LIVE_PLAYBACK_TYPE
import types
from datetime import datetime
import logging

' Global constants '
NUMBER_OF_P_PLUS = 5
NUMBER_OF_LOOP = 5
NUMBER_OF_P_PLUS_DRM = 6
NUMBER_OF_LOOP_DRM = 5

# 2 different timings
TUNING_WIFI_WAIT = 10
TUNING_ETHERNET_WAIT = 10
ZAPPING_START_CHANNEL = 32


#############
## FUNCTIONS
#############


def dirchanac(ve_test, testname, channel_number, tempo=0.2, time_out=2, with_ok=False):
    """
    function: Perform a zapping by dca
    :param channel_number: number of the channel to zap to
    :param tempo: in seconds. Time to wait before inputing a key
    :param time_out: in seconds. Time to wait before returning from the method
    :param with_ok: boolean. Pressing ok after inputing the channel number
    :return: None
    """

    # init KPI values for csv report
    kpiZappingDuration = "NA"
    kpiProfileResolution = "NA"
    kpiProfileBitrate = "NA"
    kpiProfileCount = "NA"

    for char in str(channel_number):
        ve_test.wait(tempo)
        ve_test.appium.key_event_adb("KEYCODE_" + char)
    ve_test.appium.key_event_adb("KEYCODE_DPAD_CENTER")

    ve_test.wait(time_out)

    request = ve_test.milestones.getLiveKpiMeasurement()
    parserApi = KpiRequestParserAPI(request)

    kpiZappingDuration = str(parserApi.getCurrentPlaybackDuration())
    logging.info( "test_zapping : zapping duration is : " + kpiZappingDuration)

    profiles = parserApi.getProfilesIds()
    for myId in profiles:
        kpiProfileResolution = str(parserApi.getProfileResolution(myId))
        logging.info( "profile resolution = " + kpiProfileResolution)
        kpiProfileBitrate = str(parserApi.getProfileBitrate(myId))
        logging.info( "profile bitrate = " + kpiProfileBitrate)
        kpiProfileCount = str(parserApi.getProfileCount(myId))
        logging.info( "profile count = " + kpiProfileCount)
        # only firt profile expectd for this KPI test.
        break

    # write zapping KPI to csv file
    kpi_utils.kpi_to_csv(testname, [kpiZappingDuration, kpiProfileResolution, kpiProfileBitrate, kpiProfileBitrate])

    ve_test.wait(time_out)


# Try to zapp NUMBER_OF_STREAM_SWITCH_TESTS times, accepting MAX_NUMBER_OF_ERROR, with local_number_of_p_plus zapping with P+, and same with P-
def internal_zapping_to_next_channel(ve_test, testname, network_mode, expected_duration, local_number_of_p_plus, local_number_of_loop):
    """
    function: Try to zapp NUMBER_OF_STREAM_SWITCH_TESTS times, accepting MAX_NUMBER_OF_ERROR, with local_number_of_p_plus zapping with P+, and same with P-
    :param ve_test:
    :param testname:
    :param network_mode:
    :param expected_duration:
    :param local_number_of_p_plus:
    :param local_number_of_loop:
    :return:
    """

    # init VAR
    NUMBER_OF_STREAM_SWITCH_TESTS = 2 * local_number_of_p_plus
    MAX_NUMBER_OF_ERROR = local_number_of_p_plus
    MAX_AUTHORIZED_RETRY = local_number_of_p_plus

    remaining_zapping_number = NUMBER_OF_STREAM_SWITCH_TESTS
    loop_number = local_number_of_loop
    total_remaining_zapping_number = local_number_of_loop * NUMBER_OF_STREAM_SWITCH_TESTS
    number_error_displayed = 0
    i = 0

    playback_status = ve_test.milestones.getPlaybackStatus()
    logging.info( "test_zapping : playback status = " + playback_status["playbackState"])
    logging.info( "channel URL is : " + playback_status['sso']['sessionPlaybackUrl'])

    while (loop_number > 0 and remaining_zapping_number > 0 and number_error_displayed < MAX_NUMBER_OF_ERROR):

        # reset KPI values for csv report
        kpiZappingDuration = "NA"
        kpiProfileResolution = "NA"
        kpiProfileBitrate = "NA"
        kpiProfileCount = "NA"

        logging.info( "test_zapping : remaining=" + str(total_remaining_zapping_number) + " -- number_error_displayed=" + str(
            number_error_displayed))
        # Zapp
        if (i < local_number_of_p_plus):
            logging.info( "test_zapping : Zapp to next channel")
            ve_test.screens.playback.zap_to_next_channel(expected_duration)

        else:
            logging.info( "test_zapping : Zapp to previous channel")
            ve_test.screens.playback.zap_to_previous_channel(expected_duration)
        i = (i + 1) % NUMBER_OF_STREAM_SWITCH_TESTS
        # Check if the zapping succeed
        playback_status = ve_test.milestones.getPlaybackStatus()
        logging.info( "test_zapping : playback status = " + playback_status["playbackState"])
        logging.info( "channel URL after ZAP is : ", playback_status['sso']['sessionPlaybackUrl'])
        if (playback_status["playbackState"] == "PLAYING"):
            logging.info( "    ---> Zapping OK")
            remaining_zapping_number -= 1
            total_remaining_zapping_number -= 1

            request = ve_test.milestones.getLiveKpiMeasurement()
            parserApi = KpiRequestParserAPI(request)

            kpiZappingDuration = str(parserApi.getCurrentPlaybackDuration())
            logging.info( "test_zapping : zapping duration is : " + kpiZappingDuration)

            profiles = parserApi.getProfilesIds()

            for myId in profiles:
                kpiProfileResolution = str(parserApi.getProfileResolution(myId))
                logging.info( "profile resolution = " + kpiProfileResolution)
                kpiProfileBitrate = str(parserApi.getProfileBitrate(myId))
                logging.info( "profile bitrate = " + kpiProfileBitrate)
                kpiProfileCount = str(parserApi.getProfileCount(myId))
                logging.info( "profile count = " + kpiProfileCount)
                # only firt profile expectd for this KPI test.
                break

            # write zapping KPI to csv file
            kpi_utils.kpi_to_csv(testname,[kpiZappingDuration, kpiProfileResolution, kpiProfileBitrate, kpiProfileBitrate])

        else:
            logging.info( "    ---> Zapping KO : checking notification")
            remaining_zapping_number -= 1
            total_remaining_zapping_number -= 1
            # An error should be displayed
            currentScreen = ""
            retry = 0
            # Check x times until a screen is shown
            while (currentScreen != "notification" and retry < MAX_AUTHORIZED_RETRY):
                elements = ve_test.milestones.getElements()
                screen = ve_test.milestones.get_value_by_key(elements, "screen_name")
                retry += 1
                if type(screen) == types.BooleanType:
                    logging.info( "test_zapping : A notification is not displayed on service " + playback_status['sso'][
                        'sessionPlaybackUrl'])
                    ve_test.wait(2)
                else:
                    currentScreen = screen
                    text = ve_test.milestones.get_value_by_key(elements, "msg_text")
                    logging.info( "test_zapping : A notification (" + text + ")is displayed on service " + \
                          playback_status['sso']['sessionPlaybackUrl'])

            # not used :
            # notification = ve_test.check_notification_screen(True)
            number_error_displayed += 1

        if (loop_number > 0 and remaining_zapping_number == 0):
            loop_number -= 1
            remaining_zapping_number = NUMBER_OF_STREAM_SWITCH_TESTS

    ve_test.screens.playback.kpi_to_html(LIVE_PLAYBACK_TYPE)
    request = ve_test.milestones.getLiveKpiMeasurement()
    parserApi = KpiRequestParserAPI(request)
    ve_test.log_assert(number_error_displayed < MAX_NUMBER_OF_ERROR,
                       "Too many errors displayed ( " + str(MAX_NUMBER_OF_ERROR) + ")")
    ve_test.log_assert(parserApi.getMaxPlaybackStartSequenceDuration() < expected_duration * 1000,
                       ("[%s] A zapping took more than %ds to be displayed", network_mode, str(expected_duration)))
    logging.info( "getSuccessPlaybackNb = " + str(parserApi.getSuccessPlaybackNb() )  )

########################################
#### TESTS
########################################

@pytest.mark.KPI
@pytest.mark.KPI_zapping
@pytest.mark.KPI_zapping_ethernet
def test_kpi_zapping_ethernet():
    """
    TEST: gets KPI about zapping sequence with clear channels and Ethernet network connection
    :return:
    """
    test_name = "test_kpi_zapping_ethernet"

    # init KPI result file (csv)
    kpi_utils.kpi_to_csv(test_name, [test_name + " run : ", datetime.now().strftime("%Y-%m-%d %H:%M:%S") ])
    kpi_utils.kpi_to_csv(test_name, ["zapping duration (s)", "profile resolution", "profile bitrate", "profile count"])

    # init test
    ve_test = VeTestApi(test_name)
    ve_test.begin_to_fullscreen()
    ve_test.wait(5)

    # go to initial channel before KPI sequence start
    dirchanac(ve_test, test_name, ZAPPING_START_CHANNEL)
    ve_test.wait(5)

    # run zapping KPI sequence
    internal_zapping_to_next_channel(ve_test, test_name, "Ethernet", TUNING_ETHERNET_WAIT, NUMBER_OF_P_PLUS, NUMBER_OF_LOOP)

    # end of test
    ve_test.end()

@pytest.mark.KPI
@pytest.mark.KPI_zapping
@pytest.mark.KPI_zapping_wifi
def test_kpi_zapping_wifi():
    """
    TEST: gets KPI about zapping sequence with clear channels and Wifi network connection
    :return:
    """
    test_name = "test_kpi_zapping_wifi"

    # init KPI result file (csv)
    kpi_utils.kpi_to_csv(test_name, [test_name + " run : ", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    kpi_utils.kpi_to_csv(test_name,["zapping duration (s)", "profile resolution", "profile bitrate", "profile count"])

    # init test
    ve_test = VeTestApi(test_name)
    ve_test.begin_to_fullscreen()
    ve_test.wait(5)

    # go to initial channel before KPI sequence start
    dirchanac(ve_test, test_name, ZAPPING_START_CHANNEL)
    ve_test.wait(5)

    # run zapping KPI sequence
    internal_zapping_to_next_channel(ve_test, test_name, "Wifi", TUNING_WIFI_WAIT, NUMBER_OF_P_PLUS, NUMBER_OF_LOOP)

    # end of test
    ve_test.end()


@pytest.mark.KPI
@pytest.mark.KPI_zapping_drm
@pytest.mark.KPI_zapping_drm_ethernet
def test_kpi_zapping_drm_ethernet():
    """
    TEST: gets KPI about zapping sequence with DRM channels and Ethernet network connection
    :return:
    """
    test_name = "test_kpi_zapping_drm_ethernet"

    # init KPI result file (csv)
    kpi_utils.kpi_to_csv(test_name, [test_name + " run : ", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    kpi_utils.kpi_to_csv(test_name, ["zapping duration (s)", "profile resolution", "profile bitrate", "profile count"])

    # init test
    ve_test = VeTestApi(test_name)
    ve_test.begin_to_fullscreen()
    ve_test.wait(5)

    # go to initial channel before KPI sequence start
    dirchanac(ve_test, test_name, ZAPPING_START_CHANNEL)
    ve_test.wait(5)

    # run zapping KPI sequence
    internal_zapping_to_next_channel(ve_test, test_name, "Ethernet", TUNING_ETHERNET_WAIT, NUMBER_OF_P_PLUS_DRM,
                                               NUMBER_OF_LOOP_DRM)

    # end of test
    ve_test.end()

@pytest.mark.KPI
@pytest.mark.KPI_zapping_drm
@pytest.mark.KPI_zapping_drm_wifi
def test_kpi_zapping_drm_wifi():
    """
    TEST: gets KPI about zapping sequence with DRM channels and Wifi network connection
    :return:
    """

    test_name = "test_kpi_zapping_drm_wifi"

    # init KPI result file (csv)
    kpi_utils.kpi_to_csv(test_name, [test_name + " run : ", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    kpi_utils.kpi_to_csv(test_name, ["zapping duration (s)", "profile resolution", "profile bitrate", "profile count"])

    # init test
    ve_test = VeTestApi(test_name)
    ve_test.begin_to_fullscreen()
    ve_test.wait(5)

    # go to initial channel before KPI sequence start
    dirchanac(ve_test, test_name, ZAPPING_START_CHANNEL)
    ve_test.wait(5)

    # run zapping KPI sequence
    internal_zapping_to_next_channel(ve_test, test_name, "Wifi", TUNING_WIFI_WAIT, NUMBER_OF_P_PLUS_DRM,
                                               NUMBER_OF_LOOP_DRM)

    # end of test
    ve_test.end()
