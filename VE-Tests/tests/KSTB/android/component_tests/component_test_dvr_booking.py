__author__ = 'Yonatan Zwecher'

import pytest
import logging
import requests
import json
import httplib
from tests_framework.ve_tests.ve_test_KSTB import VeTestApiKSTB, FULL_SCREEN_NAME
from tests_framework.ve_tests.assert_mgr import AssertMgr
from tests_framework.ui_building_blocks.KSTB.ui_building_blocks_KSTB import KSTBBuildingBlocks, DVRBooking


def test_01_book_current_event_from_fullscreen():
    test = DVRBooking(title="test_01_book_current_event_from_fullscreen")
    test.start_test()
    test.to_fullscreen_from_hub()
    test.wait_for_screen(30, FULL_SCREEN_NAME)
    test.to_actionmenu_from_fullscreen()
    result = test.start_record()
    test.log_assert(result is True, str(result))
    test.wait_for_screen(30, FULL_SCREEN_NAME) #ack should be dismissed
    test.to_hub_from_fullscreen()
    result = test.verify_recordings_in_hub()
    test.log_assert(result is True, str(result))

    
def test_02_book_future_event_from_timeline():
    test = DVRBooking(title="test_02_book_future_event_from_timeline")
    test.start_test()
    test.wait_for_screen(30, FULL_SCREEN_NAME)
    test.to_timeline_from_fullscreen()
    result = test.to_nextevent_in_timeline()
    test.log_assert(result is True, str(result))
    test.to_actionmenu_from_timeline()
    result = test.start_record()
    test.log_assert(result is True, str(result))
    
def test_03_book_future_event_from_guide():
    test = DVRBooking(title="test_03_book_future_event_from_guide")
    test.start_test()
    test.to_guide_from_hub()
    for i in range(0,2):
        result = test.to_nextevent_in_guide()
        test.log_assert(result is True, str(result))
    test.screens.action_menu.navigate()
    result = test.start_record()
    test.log_assert(result is True, str(result))

def test_04_play_recording():
    test = DVRBooking(title="test_04_play_recording")
    test.start_test()
    result = test.verify_recordings_in_hub()
    test.log_assert(result is True, str(result))
    result = test.start_playback_of_focused_asset_in_hub_library_action_menu()
    test.log_assert(result is True, str(result))
    
    
def test_05_stop_recording():
    test = DVRBooking(title="test_05_stop_recording")
    test.start_test()
    result = test.verify_recordings_in_hub()
    test.log_assert(result is True, str(result))
    result = test.start_playback_of_focused_asset_in_hub_library_action_menu()
    test.log_assert(result is True, str(result))
    test.wait_for_screen(30, FULL_SCREEN_NAME)
    test.wait(30) #playback running
    result = test.stop_playback_of_playing_asset('main_hub')
    test.log_assert(result is True, str(result))

def test_06_wait_for_end_of_playback():
    test = DVRBooking(title="test_06_wait_for_end_of_playback")
    test.start_test()
    result = test.verify_recordings_in_hub()
    test.log_assert(result is True, str(result))
    result = test.start_playback_of_focused_asset_in_hub_library_action_menu()
    test.log_assert(result is True, str(result))
    result = test.wait_for_screen(100,'main_hub')
    test.log_assert(result is True, str('playback did not ended or did not got back to hub after end'))#eof should return to hub afater 50 sec
