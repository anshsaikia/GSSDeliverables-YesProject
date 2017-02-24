__author__ = 'darumugh'
import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition

AVERAGE_WAIT_TIME = 5
MIN_WAIT_TIME = 3
VOD_PLAY_WAIT_TIME = 10
VOD_ASSET_POSITION = EventViewPosition.left_event
VOD_PLAY_MID_POSITION = 50
VOD_PLAY_END_POSITION = 90
VOD_PLAY_START_POSITION = 10
VOD_SEEK_BAR_TIMEOUT = 10

@pytest.mark.MF251_vod_trickmode
def test_seek_on_tap():

    ve_test = VeTestApi("store:test_seek_on_tap")
    ve_test.begin()
    start_vod_play(ve_test, True)
    ve_test.wait(VOD_PLAY_WAIT_TIME)
    verify_seek(ve_test, True)
    ve_test.end()

@pytest.mark.MF251_vod_trickmode
def test_seek_on_swipe():

    ve_test = VeTestApi("store:test_seek_on_swipe")
    ve_test.begin()
    start_vod_play(ve_test, True)
    ve_test.wait(VOD_PLAY_WAIT_TIME)
    verify_seek(ve_test, False)
    ve_test.end()

@pytest.mark.MF251_vod_trickmode
def test_trick_mode_bar_timeout():
    ve_test = VeTestApi("store:test_trick_mode_bar_timeout")
    ve_test.begin()
    start_vod_play(ve_test, True)
    ve_test.wait(VOD_PLAY_WAIT_TIME)
    verify_timeout(ve_test)
    ve_test.end()

def verify_seek(ve_test, is_tap):
    # Verifying forward when video is playing
    ve_test.screens.playback.verify_streaming_playing()
    seek(ve_test, is_tap)
    # Verifying forward when video is paused
    ve_test.screens.vod_action_menu.press_play_pause()
    ve_test.wait(MIN_WAIT_TIME)
    ve_test.screens.playback.verify_streaming_paused()
    seek(ve_test, is_tap)


def seek(ve_test, is_tap):
    vod_action_menu = ve_test.screens.vod_action_menu
    position = vod_action_menu.get_current_seek_bar_position()
    if position >= VOD_PLAY_MID_POSITION:
        vod_action_menu.seek(is_tap, percent=VOD_PLAY_START_POSITION)
        ve_test.wait(MIN_WAIT_TIME)

    vod_action_menu.seek(is_tap, percent=VOD_PLAY_MID_POSITION)
    ve_test.wait(MIN_WAIT_TIME)
    position = vod_action_menu.get_current_seek_bar_position()
    ve_test.log_assert(position >= VOD_PLAY_MID_POSITION, \
        "Fast forward(Play mode) test failed on tap action,\n Expected position: %d, Actual position: %d"\
        %(VOD_PLAY_MID_POSITION, position))
    vod_action_menu.seek(is_tap, percent=VOD_PLAY_START_POSITION)
    ve_test.wait(MIN_WAIT_TIME)

def verify_timeout(ve_test):
    vod_action_menu = ve_test.screens.vod_action_menu
    # Verify Seek bar Timeout when video is playing
    vod_action_menu.navigate()
    ve_test.wait(VOD_SEEK_BAR_TIMEOUT)
    ve_test.log_assert(is_seek_bar_present(ve_test), "Seek bar is not present, timer should not expire")
    ve_test.log_assert(is_action_menu_present(ve_test), "Action menu is not present, timer should not expired")

    vod_action_menu.seek(True, percent=VOD_PLAY_MID_POSITION)
    ve_test.wait(MIN_WAIT_TIME)
    ve_test.log_assert(not is_seek_bar_present(ve_test), "Seek bar is present, Timer should have expired")

    # Verify Timeout when video is paused
    vod_action_menu.navigate()
    vod_action_menu.press_play_pause()
    ve_test.wait(MIN_WAIT_TIME)
    ve_test.screens.playback.verify_streaming_paused()
    # Verify Seek bar timer while video is PAUSED
    ve_test.log_assert(is_seek_bar_present(ve_test), "Seek bar Timer expired, when video is PAUSED")
    # Verify Action timer after actions in seek bar
    ve_test.log_assert(not is_action_menu_present(ve_test), "Action menu is present, action menu should have expired")

def start_vod_play(ve_test, is_playback):
    credentials = ve_test.he_utils.default_credentials
    pin_screen = ve_test.screens.pincode
    pin_code = ve_test.he_utils.getYouthpincode(credentials[0])
    action_menu = ve_test.screens.vod_action_menu
    ve_test.screens.main_hub.open_vod_action_menu_by_position(VOD_ASSET_POSITION)

    ve_test.wait(AVERAGE_WAIT_TIME)
    if is_playback:
        action_menu.play_restart_asset()
    else:
        action_menu.resume_asset()

    ve_test.wait(MIN_WAIT_TIME)

    if pin_screen.is_active():
        pin_screen.enter_pin(pin_code)

    ve_test.wait(AVERAGE_WAIT_TIME)
    ve_test.screens.playback.verify_streaming_playing()

def is_seek_bar_present(ve_test):
    milestones = ve_test.milestones
    elements = milestones.getElements()
    if milestones.getElementContains(elements, "seek_bar_view", "name"):
        return True
    else:
        return False

def is_action_menu_present(ve_test):
    milestones = ve_test.milestones
    elements = milestones.getElements()
    if milestones.getElementContains(elements, "EVENT_SOURCE_TYPE_VOD", "event_source"):
        return True
    else:
        return False

