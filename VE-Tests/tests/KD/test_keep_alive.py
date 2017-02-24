import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.screen import ScreenActions
from vgw_test_utils.IHmarks import IHmark

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF972
@pytest.mark.MF972_watch_live_abr
@pytest.mark.level2
def test_channelChange_and_KeepAlive_5Mins():
    test = VeTestApi("MF972: Keep Alive after 5 Minutes")
    test.begin()
    playback = test.screens.playback
    playback_status = test.milestones.getPlaybackStatus()
    start_playing_channel = playback_status["currentChannelId"]
    while playback_status["playbackState"] != "PLAYING":
        test.screens.fullscreen.swipe_channel(ScreenActions.DOWN)
        test.wait(8)
        test.screens.notification.dismiss_notification()
        playback_status = test.milestones.getPlaybackStatus()
        test.log_assert(playback_status["currentChannelId"] == start_playing_channel,"No Playable channel found")
            
    playback.keep_alive(5.5)
    test.end()

@IHmark.O_iOS
@IHmark.O_Android
@pytest.mark.stability
def test_channelChange_and_KeepAlive_4Hours():
    test = VeTestApi("MF972: Keep Alive after 4 Hours")
    test.begin()
    playback = test.screens.playback
    playback.keep_alive(60*4)
    test.end()
