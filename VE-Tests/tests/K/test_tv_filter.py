
from tests_framework.ve_tests.ve_test import VeTestApi
import pytest
from time import sleep
from enum import Enum
from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ui_building_blocks.screen import ScreenDismiss
from vgw_test_utils.IHmarks import IHmark
import logging
from operator import itemgetter
from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ve_tests.tests_conf import DeviceType

@IHmark.O_iOS
@IHmark.O_Android
@pytest.mark.tv_filter
def test_tv_filter_last_tuned_channel():
    '''check if the first event in feature poster change to the last tuned channel'''
    test = VeTestApi("test_tv_filter_last_tuned_channel")
    test.begin()
    tv_filter = test.screens.tv_filter
    channelsNumber = tv_filter.scroll_and_return_events("poster")
    tv_filter.verify_first_item_after_tuned()
    test.end()

@IHmark.O_iOS
@IHmark.O_Android
@pytest.mark.tv_filter
def test_feature_poster_events_in_ascending_order():
    '''check if the events in poster section is in accending order'''
    test = VeTestApi("test_feature_poster_events_in_ascending_order")
    test.begin()
    tv_filter = test.screens.tv_filter
    channelsNumber = tv_filter.scroll_and_return_events("poster")
    test.log_assert(sorted(channelsNumber) == channelsNumber, "The items is not in ascending order")
    test.end()

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF1895
@pytest.mark.level2
@pytest.mark.tv_filter
@pytest.mark.MF1895_Recommended_Content
def test_count_events_each_sections():
    '''check if the number in each sections is the same number we got from ctap'''
    test = VeTestApi("test_count_events_each_sections")
    test.begin()
    tv_filter = test.screens.tv_filter
    tv_filter.count_events_each_sections()
    tv_filter.check_button_see_all()
    test.end()

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF1895
@pytest.mark.level2
@pytest.mark.tv_filter
@pytest.mark.MF1895_Recommended_Content
def test_tv_filter_navigation():
    '''check if Feature Poster events navigate to action_menu and On Air events navigate to Info Layer'''
    test = VeTestApi("test_tv_filter_navigation")
    test.begin()
    tv_filter = test.screens.tv_filter
    tv_filter.verify_navigation_from_sections()
    test.end()


