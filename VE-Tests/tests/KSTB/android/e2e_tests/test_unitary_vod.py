__author__ = 'tchevall'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi

' Global constants '
TIME_INACTIVITY = 3
STREAM_TO_PLAY="http://devimages.apple.com/iphone/samples/bipbop/gear1/prog_index.m3u8"

@pytest.mark.sanity
@pytest.mark.FS_VOD
@pytest.mark.non_regression
@pytest.mark.dummy
def test_unitary_vod_start_stop():
    ve_test = VeTestApi("test_unitary_vod_start_stop")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    ve_test.wait(3)
    ve_test.milestones.sendCommand("playURL", STREAM_TO_PLAY)
    ve_test.wait(5)
    ve_test.log_assert(ve_test.milestones.getPlaybackStatus()["playbackState"]=="PLAYING", "Playback should be playing")
    ve_test.milestones.sendCommand("stopPlayback")
    ve_test.wait(4)
    ve_test.log_assert(ve_test.milestones.getPlaybackStatus()["playbackState"]=="STOPPED", "Playback should be stopped")
    ve_test.end()

@pytest.mark.sanity
@pytest.mark.FS_VOD
@pytest.mark.non_regression
@pytest.mark.dummy
def test_unitary_vod_start_invalid_asset():
    ve_test = VeTestApi("test_unitary_vod_start_invalid_asset")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    ve_test.wait(3)
    ve_test.log_assert(ve_test.milestones.getPlaybackStatus()["playbackState"]=="PLAYING", "Playback should not be playing")
    ve_test.milestones.sendCommand("playURL", "http://AAAA.m3u8")
    ve_test.wait(2)
    ve_test.log_assert(ve_test.milestones.getPlaybackStatus()["playbackState"]=="STOPPED", "Playback should not be playing")
    ve_test.end()

@pytest.mark.sanity
@pytest.mark.FS_VOD
@pytest.mark.non_regression
@pytest.mark.dummy
def test_unitary_get_duration():
    ve_test = VeTestApi("test_unitary_get_duration")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    ve_test.screens.playback.verify_streaming_playing()

    ve_test.screens.playback.verify_duration(-1)

    ve_test.milestones.sendCommand("playURL", STREAM_TO_PLAY)
    ve_test.wait(TIME_INACTIVITY)
    #This asset contains 181 segments of 10 seconds (last segment can be shorter)
    ve_test.screens.playback.verify_duration(1800000, "more")
    ve_test.screens.playback.verify_duration(1810000, "less")
    ve_test.end()

@pytest.mark.sanity
@pytest.mark.FS_VOD
@pytest.mark.non_regression
@pytest.mark.dummy
def test_unitary_get_position():
    ve_test = VeTestApi("test_unitary_get_position")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    ve_test.screens.playback.verify_streaming_playing()

    ve_test.milestones.sendCommand("playURL", STREAM_TO_PLAY)
    ve_test.wait(TIME_INACTIVITY)
    #playback has started. position shall be greater than 0
    position = ve_test.screens.playback.verify_position( 0, "more")
    ve_test.wait(TIME_INACTIVITY)
    #new position is more than previous positoin but less than previous + 2*TIME_INACTIVITY (convert from sec to ms)
    ve_test.screens.playback.verify_position( position + 2000*TIME_INACTIVITY, "less")
    ve_test.screens.playback.verify_position( position, "more")
    ve_test.end()

@pytest.mark.sanity
@pytest.mark.FS_VOD
@pytest.mark.non_regression
@pytest.mark.dummy
def test_unitary_set_position():
    ve_test = VeTestApi("test_unitary_set_position")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    ve_test.screens.playback.verify_streaming_playing()

    ve_test.milestones.sendCommand("playURL", STREAM_TO_PLAY, "VOD")
    ve_test.wait(2*TIME_INACTIVITY)
    duration = ve_test.screens.playback.verify_duration(0, "more")

    #jump to a valid position
    ve_test.milestones.sendCommand("seekPlayback",str(duration/10))
    ve_test.wait(TIME_INACTIVITY)
    ve_test.screens.playback.verify_position( duration/10, "more")

    #jump to an invalid position. player gets paused
    ve_test.milestones.sendCommand("seekPlayback",str(duration+1000))
    ve_test.wait(TIME_INACTIVITY)
    position = ve_test.screens.playback.verify_position( 0, "more")
    ve_test.wait(TIME_INACTIVITY)
    ve_test.screens.playback.verify_position( position, "equal")

    #jump to 1 sec before the eof and verify that player gets paused at eof
    ve_test.milestones.sendCommand("seekPlayback",str(duration-1000))
    ve_test.wait(2*TIME_INACTIVITY)
    position = ve_test.screens.playback.verify_position( duration-1000, "more")
    ve_test.wait(TIME_INACTIVITY)
    ve_test.screens.playback.verify_position( position, "equal")

    ve_test.milestones.sendCommand("seekPlayback",str(duration/2))
    ve_test.wait(TIME_INACTIVITY)

    #jump to position after end of asset and verify that position doesn't change
    ve_test.milestones.sendCommand("seekPlayback",str(2*duration))
    #position is refreshed once every second. So wait 1 second in order to get sure the position is refreshed
    ve_test.wait(1)
    ve_test.screens.playback.verify_position( 2*duration, "equal")
    ve_test.wait(TIME_INACTIVITY)
    ve_test.screens.playback.verify_position( 2*duration, "equal")

    ve_test.milestones.sendCommand("seekPlayback",str(duration/2))
    ve_test.wait(TIME_INACTIVITY)

    #jump to negative position and verify that player jumps to beginning of asset and plays
    ve_test.milestones.sendCommand("seekPlayback",str(-10000))
    #wait a little bit to let player time to play
    ve_test.wait(TIME_INACTIVITY)
    ve_test.screens.playback.verify_position( 4000, "less")
    position = ve_test.screens.playback.verify_position( 0, "more")
    ve_test.wait(TIME_INACTIVITY)
    ve_test.screens.playback.verify_position( position+1, "more")

    #combine pause and jump. Verify that position is updated by the jump and then remains unchanged
    #resume and checks that player plays from new position
    ve_test.milestones.sendCommand("pausePlayback")
    ve_test.milestones.sendCommand("seekPlayback",str(duration/2))
    #position is refreshed once every second. So wait 1 second in order to get sure the position is refreshed
    ve_test.wait(1)
    ve_test.screens.playback.verify_position( duration/2, "about")
    ve_test.wait(TIME_INACTIVITY)
    ve_test.screens.playback.verify_position( duration/2, "about")
    ve_test.milestones.sendCommand("resumePlayback")
    ve_test.wait(TIME_INACTIVITY)
    ve_test.screens.playbac.verify_position((duration/2)+1, "more")
    ve_test.end()
