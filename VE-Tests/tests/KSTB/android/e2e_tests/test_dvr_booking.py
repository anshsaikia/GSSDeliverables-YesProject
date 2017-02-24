__author__ = 'Yonatan Zwecher'

import pytest
import logging
import requests
import json
import httplib
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ve_tests.assert_mgr import AssertMgr
from vgw_test_utils.IHmarks import IHmark
from tests_framework.ui_building_blocks.KSTB.dvrbooking import DVRBooking, DVRSeriesBooking, FULL_SCREEN_NAME
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS

CHANNEL_WITH_CVDR=14
CHANNEL_WITH_SERIES=6


@pytest.mark.O_Foxboro
@pytest.mark.MF1975
@pytest.mark.non_regression
@pytest.mark.FS_Live
@pytest.mark.ethernet
@pytest.mark.wifi
@pytest.mark.F_Booking
@pytest.mark.F_Booking_Current
@pytest.mark.LV_L2
@pytest.mark.parametrize("test_name, channel2record, test_class",[
    pytest.mark.test_01_book_current_event_from_fullscreen((
        "test_01_book_current_event_from_fullscreen", CHANNEL_WITH_CVDR, DVRBooking)),
    pytest.mark.test_01_book_episode_from_fullscreen((
        "test_01_book_episode_from_fullscreen", CHANNEL_WITH_SERIES, DVRBooking)),
    pytest.mark.test_01_book_season_from_fullscreen((
            "test_01_book_season_from_fullscreen", CHANNEL_WITH_SERIES, DVRSeriesBooking))
])
def test_01_generic_book_from_fullscreen(test_name, channel2record, test_class):

    test = test_class(ve_test = VeTestApi(test_name), title=test_name)
    test.ve_test.begin(screen=test.ve_test.screens.fullscreen)
    test.ve_test.wait_for_screen(30, FULL_SCREEN_NAME)
    test.ve_test.screens.playback.dca(channel2record)
    test.ve_test.wait_for_screen(30, FULL_SCREEN_NAME)
    test.ve_test.wait(5)
    test.ve_test.screens.fullscreen.wait_for_event_with_minimum_time_until_end()

    test.ve_test.screens.action_menu.navigate()
    result = test.start_record(test_flag=False)
    test.ve_test.log_assert(result is True, str(result).replace(",","\n"))
    test.ve_test.end()

@pytest.mark.O_Foxboro
@pytest.mark.MF1975
@pytest.mark.non_regression
@pytest.mark.FS_Timeline
@pytest.mark.F_Booking
@pytest.mark.F_Booking_Future
@pytest.mark.LV_L2
def test_02_book_future_event_from_timeline():
    test = DVRBooking(ve_test=VeTestApi("test_02_book_future_event_from_timeline"), title="test_02_book_future_event_from_timeline" )
    test.ve_test.begin(screen=test.ve_test.screens.fullscreen)
    test.ve_test.wait_for_screen(30, FULL_SCREEN_NAME)
    test.ve_test.screens.playback.dca(CHANNEL_WITH_CVDR)
    test.ve_test.wait_for_screen(30, FULL_SCREEN_NAME)
    test.ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT+ CONSTANTS.GENERIC_WAIT)
    test.ve_test.screens.timeline.navigate()
    result = test.ve_test.screens.timeline.to_nextevent()
    test.ve_test.log_assert(result is True, str(result).replace(",","\n"))
    test.ve_test.screens.action_menu.navigate()
    result = test.start_record(test_flag=False)
    test.ve_test.log_assert(result is True, str(result).replace(",","\n"))
    test.ve_test.end()


@pytest.mark.O_Foxboro
@pytest.mark.MF1975
@pytest.mark.non_regression
@pytest.mark.FS_Guide
@pytest.mark.F_Booking
@pytest.mark.F_Booking_Future
@pytest.mark.LV_L2
@pytest.mark.parametrize("test_name, channel2record, test_class",[
    pytest.mark.test_03_book_future_event_from_guide((
        "test_03_book_future_event_from_guide", CHANNEL_WITH_CVDR, DVRBooking)),
    pytest.mark.test_03_book_future_episode_from_guide((
        "test_03_book_future_episode_from_guide", CHANNEL_WITH_SERIES, DVRBooking)),
    pytest.mark.test_03_book_future_season_from_guide((
            "test_03_book_future_season_from_guide", CHANNEL_WITH_SERIES, DVRSeriesBooking))
])
def test_03_generic_book_future_event_from_guide(test_name, channel2record, test_class):
    test = test_class(ve_test=VeTestApi(test_name), title=test_name)
    test.ve_test.begin(screen=test.ve_test.screens.fullscreen)
    test.ve_test.screens.fullscreen.navigate()
    test.ve_test.screens.guide.navigate()
    result = test.ve_test.screens.guide.to_specific_channel_in_guide(channel2record)
    test.ve_test.log_assert(result is True, str(result).replace(",","\n"))
    for i in range(0,2):
        result = test.ve_test.screens.guide.to_nextevent_in_guide()
        test.ve_test.log_assert(result is True, str(result).replace(",","\n"))
    test.ve_test.screens.action_menu.navigate()
    result = test.start_record(test_flag = False)
    test.ve_test.log_assert(result is True, str(result).replace(",","\n"))

    test.ve_test.end()
