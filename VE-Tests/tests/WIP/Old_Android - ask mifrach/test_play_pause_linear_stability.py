__author__ = 'bwarshaw'

import logging
import pytest
from time import sleep

'''Globals'''
TWO_HOURS = 60*60*60*2
RESUME_PAYING_DELTA = 2.5*1000
from time import gmtime, strftime

'''
Pause and resume, then verify resume continues as expected for 2 hours
'''
'''
def test_play_and_pause_for_2_hours(ve_test):
    logging.info('Start test_play_and_pause_for_2_hours')

    start_app_signin(ve_test, "HH_test_play_and_pause_for_2_hours")

    ve_test.building_blocks.tune_to_channel_by_sek(102)
    verify_streaming_playing(ve_test.milestones)
    ve_test.building_blocks.navigate_to_action_menu()

    for i in range(TWO_HOURS/3):
        "Once the streaming is playing in background, verify that the 'play' image is displayed"
        play_pause_button = ve_test.milestones.getElement([("name", "play_pause_button", "==")])
        assert play_pause_button["state"] == "PLAYING"

        "Get timestamp before pausing the stream"
        print "request", strftime("%Y-%m-%d %H:%M:%S", gmtime())
        first_playback_status = ve_test.milestones.getPlaybackStatus()

        "Pause the stream"
        ve_test.appium.tap(play_pause_button["x_pos"], play_pause_button["y_pos"])
        "After pausing the stream, verify that 'pause' image is displayed"
        play_pause_button = ve_test.milestones.getElement([("name", "play_pause_button", "==")])
        assert play_pause_button["state"] == "PAUSED"
        verify_streaming_paused(ve_test.milestones)

        sleep(1)

        "Resume playing and wait 2 seconds for the stream to start"
        ve_test.appium.tap(play_pause_button["x_pos"], play_pause_button["y_pos"])

        sleep(2)

        "Verify that the stream did start and that the current resume time stamp is correct"
        print "request", strftime("%Y-%m-%d %H:%M:%S", gmtime())
        second_playback_status = ve_test.milestones.getPlaybackStatus()
        assert second_playback_status["playbackState"] == "PLAYING", "playback did not resume playing after 2 seconds"
        assert 0 <= second_playback_status["playbackBufferCurrent"] - first_playback_status["playbackBufferCurrent"] < RESUME_PAYING_DELTA + 2000
'''