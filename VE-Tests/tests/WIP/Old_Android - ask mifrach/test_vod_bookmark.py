__author__ = 'darumugh'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.he_utils.he_utils import VodContentType
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition

AVERAGE_WAIT_TIME = 5
MIN_WAIT_TIME = 3
VOD_PLAY_WAIT_TIME = 10
VOD_ASSET_POSITION = EventViewPosition.left_event

@pytest.mark.MF480_vod_bookmark
@pytest.mark.MF480_vod_bookmark_regression
def test_vod_bookmark():

    ve_test = VeTestApi("store:test_vod_bookmark")
    ve_test.begin()

    # Test VOD Bookmark from by pressing STOP Button
    start_vod_play(ve_test, True)
    ve_test.wait(VOD_PLAY_WAIT_TIME)
    initial_position = get_content_played_position(ve_test, press_stop=True)
    ve_test.wait(AVERAGE_WAIT_TIME)
    start_vod_play(ve_test, False)
    ve_test.wait(VOD_PLAY_WAIT_TIME)
    final_position = get_content_played_position(ve_test, press_stop=True)
    ve_test.wait(AVERAGE_WAIT_TIME)
    ve_test.log_assert(initial_position <= final_position,\
                "Bookmark Resume not working\n Initial position: %d\n Final position: %d" %(initial_position,final_position))

    ve_test.end()


@pytest.mark.MF480_vod_bookmark
def test_vod_bookmark_restart():

    ve_test = VeTestApi("store:test_vod_bookmark_restart")
    ve_test.begin()
    range = xrange(0, 11)
    main_hub = ve_test.screens.main_hub
    vod_action_menu = ve_test.screens.vod_action_menu
    main_hub.navigate()
    ve_test.wait(AVERAGE_WAIT_TIME)
    main_hub.tune_to_linear_channel_by_position(EventViewPosition.left_event)
    ve_test.wait(MIN_WAIT_TIME)
    last_played_channel = ve_test.screens.playback.get_current_tuned()

    # Test VOD Bookmark from by pressing STOP Button
    start_vod_play(ve_test, True)
    ve_test.wait(VOD_PLAY_WAIT_TIME)
    vod_action_menu.navigate()
    vod_action_menu.press_stop()
    ve_test.wait(MIN_WAIT_TIME)
    nowPlaying = ve_test.screens.playback.get_current_tuned()
    ve_test.log_assert(nowPlaying==last_played_channel, \
        "after vod stop last played channel was not played. Last played was " + last_played_channel + \
        " ,and now channel " + nowPlaying + " is playing")

    start_vod_play(ve_test, True)
    ve_test.wait(MIN_WAIT_TIME)
    final_position = get_content_played_position(ve_test, press_stop=True)
    ve_test.log_assert(final_position in range,\
                "Bookmark Restart not working\n Final position: %d, not in range %s\n" %(final_position, str(range)))

    ve_test.end()

@pytest.mark.MF480_vod_bookmark
def test_vod_bookmark_end_of_play():

    ve_test = VeTestApi("store:test_vod_bookmark_end_of_play")
    ve_test.begin()

    main_hub = ve_test.screens.main_hub
    vod_action_menu = ve_test.screens.vod_action_menu
    main_hub.navigate()
    ve_test.wait(AVERAGE_WAIT_TIME)
    main_hub.tune_to_linear_channel_by_position(EventViewPosition.left_event)
    ve_test.wait(MIN_WAIT_TIME)
    last_played_channel = ve_test.screens.playback.get_current_tuned()

    # Test VOD Bookmark from by pressing STOP Button
    start_vod_play(ve_test, True)
    ve_test.wait(VOD_PLAY_WAIT_TIME)
    vod_action_menu.navigate()
    ve_test.wait(MIN_WAIT_TIME)
    vod_action_menu.seek(is_tap=False, percent=85)
    ve_test.wait(AVERAGE_WAIT_TIME)
    remaining_time = vod_action_menu.calculate_remaining_time() + 60
    ve_test.log("Waiting for %d seconds, for the video to complete" % remaining_time)
    ve_test.wait(remaining_time)

    asset = ve_test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.ENCRYPTED, VodContentType.LOW_RATED], {'policy':'false'})
    ve_test.log_assert('title' in asset and asset['title'], "Unable to get a VOD content")
    ve_test.screens.store.navigate_to_vod_asset_by_title(asset['title'])

    vod_action_menu.verify_play_menu(present=True)
    ve_test.wait(MIN_WAIT_TIME)
    nowPlaying = ve_test.screens.playback.get_current_tuned()
    ve_test.log_assert(nowPlaying==last_played_channel, \
        "after vod stop last played channel was not played. Last played was " + last_played_channel + \
        " ,and now channel " + nowPlaying + " is playing")
    ve_test.end()

def get_content_played_position(ve_test, press_stop=False):
    vod_action_menu = ve_test.screens.vod_action_menu
    vod_action_menu.navigate()
    seek_bar_elements = vod_action_menu.get_seek_bar_elements()
    seek_bar_view = seek_bar_elements['seek_bar_view']
    ve_test.log_assert(seek_bar_view, "Seek bar is not present")
    if press_stop:
        ve_test.log_assert(vod_action_menu.press_stop(), "Unable to STOP VOD playback")

    return int(seek_bar_view['position'])

def start_vod_play(ve_test, is_playback):
    action_menu = ve_test.screens.vod_action_menu
    asset = ve_test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.ENCRYPTED, VodContentType.LOW_RATED], {'policy':'false'})
    ve_test.log_assert('title' in asset and asset['title'], "Unable to get a VOD content")
    ve_test.screens.store.navigate_to_vod_asset_by_title(asset['title'])
    ve_test.wait(AVERAGE_WAIT_TIME)

    if is_playback:
        action_menu.play_asset()
    else:
        action_menu.resume_asset()

    ve_test.wait(MIN_WAIT_TIME)
    ve_test.screens.playback.verify_streaming_playing()
