__author__ = 'ljusseau'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from time import sleep


' Global constants '
TIME_INACTIVITY = 3
TIME_INACTIVITY_LONG = 10
TOGGLE_LOOP_NUMBER = 5

@pytest.mark.FS_Live
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.wifi
@pytest.mark.ethernet
def test_unitary_resize():
    ve_test = VeTestApi("test_unitary_all_commands:unitary_resize")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    #ve_test.zap_to_next_channel(TIME_INACTIVITY_LONG)

    ve_test.screens.playback.verify_streaming_playing()

    #ve_test.milestones.sendCommand("playURL","http://192.118.34.62/data/HAClear/latest.m3u8")
    #sleep(TIME_INACTIVITY)
    ve_test.milestones.sendCommand("setPlaybackOutputType","SCALE")
    ve_test.screens.playback.verify_output_type("SCALE")
    sleep(TIME_INACTIVITY_LONG)
    ve_test.milestones.sendCommand("setPlaybackOutputType","STRETCH")
    ve_test.screens.playback.verify_output_type("STRETCH")
    sleep(TIME_INACTIVITY_LONG)
    ve_test.milestones.sendCommand("setPlaybackOutputType","FIT")
    ve_test.screens.playback.verify_output_type("FIT")
    sleep(TIME_INACTIVITY_LONG)
    ve_test.end()

@pytest.mark.FS_Live
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.wifi
@pytest.mark.ethernet
def test_unitary_mute_unmute():
    ve_test = VeTestApi("test_unitary_all_commands:mute_unmute")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    #ve_test.zap_to_next_channel(TIME_INACTIVITY_LONG)

    ve_test.screens.playback.verify_streaming_playing()
    ve_test.screens.playback.verify_streaming_muted(False)
    
    #mute and verify new state, even after some inactivity
    ve_test.milestones.sendCommand("muteAudio")
    ve_test.screens.playback.verify_streaming_muted(True)
    sleep(TIME_INACTIVITY)
    ve_test.screens.playback.verify_streaming_muted(True)
    
    #mute again and verify that state is unchanged
    ve_test.milestones.sendCommand("muteAudio")
    ve_test.screens.playback.verify_streaming_muted(True)
    
    #unmute and verify new state, even after some inactivity
    ve_test.milestones.sendCommand("unmuteAudio")
    ve_test.screens.playback.verify_streaming_muted(False)
    sleep(TIME_INACTIVITY)
    ve_test.screens.playback.verify_streaming_muted(False)
    
    #unmute again and verify that state is unchanged
    ve_test.milestones.sendCommand("unmuteAudio")
    ve_test.screens.playback.verify_streaming_muted(False)
    
    #quick toggle should not cause issues
    for i in range(1, TOGGLE_LOOP_NUMBER):
        ve_test.milestones.sendCommand("muteAudio")
        ve_test.screens.playback.verify_streaming_muted(True)
        ve_test.milestones.sendCommand("unmuteAudio")
        ve_test.screens.playback.verify_streaming_muted(False)

    ve_test.end()

@pytest.mark.FS_Live
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.wifi
@pytest.mark.ethernet
def test_unitary_blank_unblank():
    ve_test = VeTestApi("test_unitary_all_commands:blank_unblank")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    #ve_test.zap_to_next_channel(TIME_INACTIVITY_LONG)

    ve_test.screens.playback.verify_streaming_playing()
    ve_test.screens.playback.verify_streaming_blanked(False)
    
    #blank video and verify new state, even after some inactivity
    ve_test.milestones.sendCommand("blankVideo")
    ve_test.screens.playback.verify_streaming_blanked(True)
    sleep(TIME_INACTIVITY)
    ve_test.screens.playback.verify_streaming_blanked(True)
    
    #blank video again and verify that state is unchanged
    ve_test.milestones.sendCommand("blankVideo")
    ve_test.screens.playback.verify_streaming_blanked(True)
    
    #unblank and verify new state, even after some inactivty
    ve_test.milestones.sendCommand("unblankVideo")
    ve_test.screens.playback.verify_streaming_blanked(False)
    sleep(TIME_INACTIVITY)
    ve_test.screens.playback.verify_streaming_blanked(False)
    
    #unblank again and verify that state is unchanged
    ve_test.milestones.sendCommand("unblankVideo")
    ve_test.screens.playback.verify_streaming_blanked(False)
    
    #quick toggle should not cause issues
    for i in range(1, TOGGLE_LOOP_NUMBER):
        ve_test.milestones.sendCommand("blankVideo")
        ve_test.screens.playback.verify_streaming_blanked(True)
        ve_test.milestones.sendCommand("unblankVideo")
        ve_test.screens.playback.verify_streaming_blanked(False)
    
    ve_test.end()    


@pytest.mark.FS_Live
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.wifi
@pytest.mark.ethernet
def test_unitary_blank_and_mute():
    ve_test = VeTestApi("test_unitary_all_commands:blank_and_mute")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    #ve_test.zap_to_next_channel(TIME_INACTIVITY_LONG)
    ve_test.screens.playback.verify_streaming_playing()
    
    ve_test.screens.playback.verify_streaming_muted(False)
    ve_test.screens.playback.verify_streaming_blanked(False)
    
    ve_test.milestones.sendCommand("muteAudio")
    ve_test.screens.playback.verify_streaming_muted(True)
    ve_test.screens.playback.verify_streaming_blanked(False)
    
    ve_test.milestones.sendCommand("blankVideo")
    ve_test.screens.playback.verify_streaming_muted(True)
    ve_test.screens.playback.verify_streaming_blanked(True)
    
    ve_test.milestones.sendCommand("unmuteAudio")
    ve_test.screens.playback.verify_streaming_muted(False)
    ve_test.screens.playback.verify_streaming_blanked(True)
    
    ve_test.milestones.sendCommand("unblankVideo")
    ve_test.screens.playback.verify_streaming_muted(False)
    ve_test.screens.playback.verify_streaming_blanked(False)
    ve_test.end()    

@pytest.mark.FS_Live
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.wifi
@pytest.mark.ethernet
def test_unitary_dimmer():
    DIMMER_OFFSET = 0.05
    ve_test = VeTestApi("test_unitary_all_commands:unitary_dimmer")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    ve_test.screens.playback.verify_streaming_playing()

    sleep(TIME_INACTIVITY_LONG)

    ve_test.milestones.sendCommand("setDimmer","0")
    ve_test.screens.playback.verify_percent_dimmer(DIMMER_OFFSET)
    sleep(TIME_INACTIVITY)

    ve_test.milestones.sendCommand("setDimmer","0.5")
    ve_test.screens.playback.verify_percent_dimmer((0.5+DIMMER_OFFSET))
    sleep(TIME_INACTIVITY)

    ve_test.milestones.sendCommand("setDimmer","1")
    ve_test.screens.playback.verify_percent_dimmer((1+DIMMER_OFFSET))
    sleep(TIME_INACTIVITY)

    ve_test.end()

@pytest.mark.FS_Live
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.wifi
@pytest.mark.ethernet
def test_unitary_live_get_duration():
    ve_test = VeTestApi("test_unitary_all_commands:live_get_duration")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    #ve_test.zap_to_next_channel(TIME_INACTIVITY_LONG)

    ve_test.screens.playback.verify_streaming_playing()

    #playback has started. position shall be -1 on live stream
    ve_test.wait(TIME_INACTIVITY)
    ve_test.screens.playback.verify_duration(-1)
    ve_test.wait(TIME_INACTIVITY)
    ve_test.screens.playback.verify_duration(-1)
    ve_test.end()

@pytest.mark.FS_Live
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.wifi
@pytest.mark.ethernet
@pytest.mark.LV_L2
def test_unitary_live_get_position():
    ve_test = VeTestApi("test_unitary_all_commands:live_get_position")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    #ve_test.zap_to_next_channel(TIME_INACTIVITY_LONG)
    ve_test.screens.playback.verify_streaming_playing()

    #playback has started. position shall be curent time on live
    ve_test.wait(TIME_INACTIVITY)
    ve_test.screens.playback.verify_position( ve_test.getInternetTime(), "about", delta=2000)
    ve_test.wait(TIME_INACTIVITY)
    ve_test.screens.playback.verify_position( ve_test.getInternetTime(), "about", delta=2000)
    ve_test.end()
