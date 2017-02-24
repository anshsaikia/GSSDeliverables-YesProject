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
import random

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF956
@pytest.mark.MF956_channel_timeline
def test_close_timeline():
    test = VeTestApi("test_close_timeline")
    test.begin()
    timeline = test.screens.timeline
    time_line_dismiss = [ScreenDismiss.TAP, ScreenDismiss.CLOSE_BUTTON, ScreenDismiss.TAP_ON_EVENT]
    for item in time_line_dismiss:
        timeline.navigate()
        timeline.dismiss(item)
    test.end()

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF956
@pytest.mark.MF956_channel_timeline
@pytest.mark.level2
def test_verify_timeline_data():

    test = VeTestApi("test_verify_timeline_data")
    test.begin()

    timeline = test.screens.timeline
    timeline.navigate()

    '''get milestones elements and server data'''
    elements = test.milestones.getElements()
    server_data = test.ctap_data_provider.send_request('GRID', payload={'duration':'50000'})

    '''compare events metadata for current channel id'''
    current_channel_id = test.milestones.getElement([("screen", "timeline", "==")], elements)["channel_id"]
    timeline.compare_events_metadata(server_data, elements, current_channel_id, True)

    '''compare logos of channels in channels panel'''
    timeline.compare_channels_logos(server_data, elements, current_channel_id)

    '''tap on down arrow and refresh elements'''
    up_arrow = test.milestones.getElement([("id", "downImageView", "==")], elements)
    test.appium.tap_element(up_arrow)
    test.wait(3)
    elements = test.milestones.getElements()

    '''compare events metadata for next channel id'''
    next_channel_id = timeline.find_next_channel_id(current_channel_id, server_data)
    timeline.compare_events_metadata(server_data, elements, next_channel_id, False)

    '''compare logos of channels in channels panel'''
    timeline.compare_channels_logos(server_data, elements, next_channel_id)

    test.end()
