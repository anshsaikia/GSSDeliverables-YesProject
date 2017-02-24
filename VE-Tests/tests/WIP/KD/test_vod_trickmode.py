__author__ = 'darumugh'
import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition
from tests_framework.he_utils.he_utils import VodContentType
import logging
import json

AVERAGE_WAIT_TIME = 5
MIN_WAIT_TIME = 3
VOD_PLAY_WAIT_TIME = 5
VOD_ASSET_POSITION = EventViewPosition.left_event
VOD_PLAY_MID_POSITION = 50
VOD_PLAY_END_POSITION = 90
VOD_PLAY_START_POSITION = 10
VOD_SEEK_BAR_TIMEOUT = 10

@pytest.mark.MF1689_vod_trickmode
@pytest.mark.MF251_vod_trickmode
def test_trick_modes():

    ve_test = VeTestApi("store:test_trick_modes")
    ve_test.begin()
    vod_action_menu = ve_test.screens.vod_action_menu
    asset = ve_test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.ENCRYPTED, VodContentType.LOW_RATED, VodContentType.NON_EROTIC], {'policy':'false'})
    ve_test.screens.store.play_vod_by_title(asset['title'])
    ve_test.wait(VOD_PLAY_WAIT_TIME)
    '''when playback'''
    ve_test.screens.playback.verify_streaming_playing()

    '''Verify Seek bar doesn't time out when video is playing and user didn't touch controls'''
    vod_action_menu.navigate()
    ve_test.wait(VOD_SEEK_BAR_TIMEOUT)
    vod_action_menu.verify_active()
    seek_bar_view = ve_test.milestones.getElement([("name", "seek_bar_view", "==")])
    ve_test.log_assert(seek_bar_view, "Seek bar is not present, timer should not expire")

    '''verify that after touching seek bar, action menu and seek bar time out'''
    vod_action_menu.seek(True, percent=VOD_PLAY_START_POSITION)
    ve_test.wait(VOD_SEEK_BAR_TIMEOUT)
    seek_bar_view = ve_test.milestones.getElement([("name", "seek_bar_view", "==")])
    ve_test.log_assert(not seek_bar_view, "Seek bar is present, timer should have expired")
    ve_test.log_assert(not vod_action_menu.is_active(), "Action menu did not time out")

    '''verify seek on tap'''
    seek(ve_test, True)
    ve_test.wait(VOD_PLAY_WAIT_TIME)
    '''verify seek on swipe'''
    seek(ve_test, False)
    ve_test.wait(VOD_PLAY_WAIT_TIME)
    '''when pause'''
    ve_test.screens.vod_action_menu.press_play_pause()
    ve_test.wait(MIN_WAIT_TIME)
    ve_test.screens.playback.verify_streaming_paused()
    ve_test.wait(VOD_SEEK_BAR_TIMEOUT)
        # Verify Seek bar timer while video is PAUSED
    seek_bar_view = ve_test.milestones.getElement([("name", "seek_bar_view", "==")])
    ve_test.log_assert(seek_bar_view, "Seek bar Timer expired, when video is PAUSED")
    ve_test.log_assert(not ve_test.milestones.getElement("EVENT_SOURCE_TYPE_VOD", "event_source"), "Action menu did not time out")

    '''verify seek on tap'''
    seek(ve_test, True)
    ve_test.wait(VOD_PLAY_WAIT_TIME)
    '''verify seek on swipe'''
    seek(ve_test, False)
    ve_test.wait(VOD_PLAY_WAIT_TIME)

    ve_test.end()

def seek(ve_test, is_tap):
    vod_action_menu = ve_test.screens.vod_action_menu
    range = xrange(VOD_PLAY_MID_POSITION - 2, VOD_PLAY_MID_POSITION + 10)
    action = "Tap" if is_tap else "Swipe"
    vod_action_menu.seek(is_tap, percent=VOD_PLAY_MID_POSITION)
    ve_test.wait(MIN_WAIT_TIME)
    seek_bar_element = vod_action_menu.get_seek_bar_elements()
    position = float(seek_bar_element['seek_bar_view']['position'])
    width = float(seek_bar_element['seek_bar_view']['width'])
    current_position = int( (position/width) * 100)

    ve_test.log_assert(current_position in range, \
        "Fast forward(Play mode) test failed on %s action,\n Expected range: %s, Actual position: %d"\
        %(action, str(range), current_position))

    vod_action_menu.seek(is_tap, percent=VOD_PLAY_START_POSITION)
    ve_test.wait(MIN_WAIT_TIME)
