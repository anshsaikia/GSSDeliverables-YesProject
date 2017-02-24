__author__ = 'bbagland'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi

REMAIN_IN_BACKGROUND_TIMEOUT = 10
VIDEO_AFTER_FOREGROUND_TIMEOUT = 10
BEFORE_BACKGROUND_TIMEOUT = 10

@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.FS_Live
@pytest.mark.ethernet
@pytest.mark.wifi
@pytest.mark.LV_L2
def test_background_live():
    '''
    verify that we get the same live channel after going to background
    '''
    ve_test = VeTestApi("test_background_live")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    elements = ve_test.milestones.getElements()
    lcn_before = ve_test.milestones.get_value_by_key(elements, "current_channel")
    session_id_before = ve_test.milestones.getPlaybackStatus()["sso"]["sessionId"]

    ve_test.appium.send_app_to_background()
    ve_test.wait(REMAIN_IN_BACKGROUND_TIMEOUT)
    ve_test.appium.send_app_to_foreground()

    ve_test.wait(VIDEO_AFTER_FOREGROUND_TIMEOUT)

    elements = ve_test.milestones.getElements()
    lcn_after = ve_test.milestones.get_value_by_key(elements, "current_channel")
    session_id_after = ve_test.milestones.getPlaybackStatus()["sso"]["sessionId"]

    ve_test.log_assert(session_id_before + " " +  session_id_after)

    ve_test.log_assert(lcn_after == lcn_before, "channel changed !")
    ve_test.log_assert(session_id_after != session_id_before, "session was not created !")

    ve_test.end()

@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L2
@pytest.mark.FS_VOD
@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_app_background_foreground
def test_background_vod():
    '''
    verify that we get resume in pause on the asset position (roughly)
    '''
    ve_test = VeTestApi("test_background_vod")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    # start a vod asset
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    status = ve_test.screens.playback.vod_manager.start_free_playback(BEFORE_BACKGROUND_TIMEOUT)
    ve_test.logger.log_assert(status, "Can't start the VOD asset.")
    playbackStatusBefore = ve_test.milestones.getPlaybackStatus()

    ve_test.appium.send_app_to_background()
    ve_test.wait(REMAIN_IN_BACKGROUND_TIMEOUT)
    ve_test.appium.send_app_to_foreground()

    ve_test.wait(VIDEO_AFTER_FOREGROUND_TIMEOUT)

    elements = ve_test.milestones.getElements()
    screen = ve_test.milestones.get_value_by_key(elements, "screen")
    is_paused = ve_test.milestones.get_value_by_key(elements, "is_paused")
    is_trickmode_visible = ve_test.milestones.get_value_by_key(elements, "is_trickmode_visible")
    playbackStatus = ve_test.milestones.getPlaybackStatus()

    # UI checks
    ve_test.log_assert(screen == "trickmode", "not in trickmode screen")
    ve_test.log_assert(is_paused == True, "TM banner not paused")
    ve_test.log_assert(is_trickmode_visible == True, "TM banner not visible")

    # player checks
    ve_test.log_assert(playbackStatus['playbackType'] == "VOD", "playback is not vod")
    ve_test.log_assert(playbackStatus['playbackState'] == "PAUSED", "playback not in pause")
    ve_test.log_assert(abs(int(playbackStatus['playbackBufferCurrent']) - int(playbackStatusBefore['playbackBufferCurrent'])) < 5*1000, "resuming with more than 5s")

    ve_test.end()
