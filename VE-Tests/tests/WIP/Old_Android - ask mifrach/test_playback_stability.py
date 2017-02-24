__author__ = 'bwarshaw'

import pytest
import logging
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition


@pytest.mark.stability
@pytest.mark.linear_stability
def test_linear_playback_stability():
    test = VeTestApi("test_linear_playback_stability")
    test.begin()

    test.screens.main_hub.tune_to_linear_channel_by_position(EventViewPosition.right_event)

    for i in range(90):
        test.screens.playback.verify_streaming_playing()
        test.wait(120)
        logging.info(" %s minutes passed " % ((i+1)*2))

    test.end()


@pytest.mark.stability
@pytest.mark.vod_stability
def test_vod_playback_stability():
    test = VeTestApi("test_vod_playback_stability")
    test.begin()

    test.screens.main_hub.play_vod_asset_by_position(EventViewPosition.left_event)

    playback_status = test.milestones.getPlaybackStatus()
    test.log_assert(playback_status["playbackType"] == "VOD")
    vod_time_in_seconds = (playback_status["playbackBufferEnd"] - playback_status["playbackBufferStart"])/1000

    for i in range(int(vod_time_in_seconds/100)-1):
        test.screens.playback.verify_streaming_playing()
        test.wait(100)
    test.end()
