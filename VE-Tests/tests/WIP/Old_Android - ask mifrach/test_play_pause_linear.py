__author__ = 'bwarshaw'

import logging
import pytest
from time import sleep, time

'''Globals'''
TWO_HOURS = 60*60*60*2
RESUME_PAYING_DELTA = 2.5*1000

'''
- The test verifies that the play pause image is changing accordingly and correctly
'''
''' test_verify_play_pause_images_switch(ve_test):
    logging.info('Start test_verify_play_pause_images_switch')

    start_app_signin(ve_test, 'HH_test_verify_play_pause_images_switch')

    ve_test.building_blocks.tune_to_channel_by_sek(102)
    verify_streaming_playing(ve_test.milestones)
    ve_test.building_blocks.navigate_to_action_menu()

    play_pause_button = ve_test.milestones.getElement([("name", "play_pause_button", "==")])
    assert play_pause_button and play_pause_button["state"] == "PLAYING"

    ve_test.appium.tap_element(play_pause_button)

    play_pause_button = ve_test.milestones.getElement([("name", "play_pause_button", "==")])
    assert play_pause_button and play_pause_button["state"] == "PAUSED"
    verify_streaming_paused(ve_test.milestones)

    "Adding required edge case, Verify that streaming begins after 1 seconds"
    ve_test.appium.tap_element(play_pause_button)
    sleep(1.5)
    playback_status = ve_test.milestones.getPlaybackStatus()
    assert playback_status["playbackState"] == "PLAYING"

'''
'''
Pause and do channel change, verify it resumes playing the requested channel immediately
- Verify that the paused channel return playing after channel change again to it
'''
'''
def test_continue_playing_after_channel_change(ve_test):
    logging.info('Start test_continue_playing_after_channel_change')

    start_app_signin(ve_test, "HH_test_continue_playing_after_channel_change")

    ve_test.building_blocks.tune_to_channel_by_sek(102)
    verify_streaming_playing(ve_test.milestones)
    ve_test.building_blocks.navigate_to_action_menu()

    play_pause_button = ve_test.milestones.getElement([("name", "play_pause_button", "==")])
    assert play_pause_button and play_pause_button["state"] == "PLAYING"

    ve_test.appium.tap_element(play_pause_button)

    play_pause_button = ve_test.milestones.getElement([("name", "play_pause_button", "==")])
    assert play_pause_button and play_pause_button["state"] == "PAUSED"

    ve_test.building_blocks.tune_to_channel_by_sek(103)
    verify_streaming_playing(ve_test.milestones)
    sleep(2)

    ve_test.building_blocks.tune_to_channel_by_sek(102)
    verify_streaming_playing(ve_test.milestones)
    ve_test.building_blocks.navigate_to_action_menu()

    play_pause_button = ve_test.milestones.getElement([("name", "play_pause_button", "==")])
    assert play_pause_button and play_pause_button["state"] == "PLAYING"

'''
'''
Pause and resume continues from the same point in time
- Assert that when the resume button is then tapped, the video continues for the point it was paused at
- Assert that video is playing within X sec from the tap on the resume button (after being paused)
'''
'''
def test_continue_playing_after_pause(ve_test):
    logging.info('Start test_continue_playing_after_channel_change')

    start_app_signin(ve_test, "HH_test_continue_playing_after_channel_change")
    ve_test.building_blocks.tune_to_channel_by_sek(102)
    verify_streaming_playing(ve_test.milestones)

    ve_test.building_blocks.navigate_to_action_menu()
    play_pause_button = ve_test.milestones.getElement([("name", "play_pause_button", "==")])

    first_playback_status = ve_test.milestones.getPlaybackStatus()
    ve_test.appium.tap_element(play_pause_button)
    sleep(10)
    ve_test.appium.tap_element(play_pause_button)
    second_playback_status = ve_test.milestones.getPlaybackStatus()

    assert 0 <= second_playback_status["playbackBufferCurrent"] - first_playback_status["playbackBufferCurrent"] < RESUME_PAYING_DELTA


'''
'''
TODO: still not in use, has to verified once again.
'''
'''
def seek_review_buffer(appium, milestones, building_blocks, minutes):
    building_blocks.navigate_to_action_menu()
    seek_bar = milestones.getElement([("name", "seek_bar_view", "==")])
    playback_manager = milestones.getPlaybackStatus()
    review_buffer = (playback_manager["playbackBufferEnd"] - playback_manager["playbackBufferStart"])/60000
    appium.swipe_area(seek_bar["x_pos"] + seek_bar["width"] - 1,
                      seek_bar["y_pos"] + seek_bar["height"]/2,
                      seek_bar["x_pos"] + seek_bar["width"] - ((minutes*seek_bar["width"])/review_buffer),
                      seek_bar["y_pos"] + seek_bar["height"]/2)

'''
'''
Assert after review buffer time, the app starts playing cur channel
The test verify that streaming continues after that
'''
'''
def test_playing_after_review_buffer(ve_test):
    start_app_signin(ve_test, "HH_test_playing_after_review_buffer")

    "Tune to channel 102, FOODHD"
    ve_test.building_blocks.tune_to_channel_by_sek(102)
    verify_streaming_playing(ve_test.milestones)

    "Navigate to ActionMenu"
    ve_test.building_blocks.navigate_to_action_menu()

    "Pause stream and sleep"
    play_pause_button = ve_test.milestones.getElement([("name", "play_pause_button", "==")])
    playback_manager = ve_test.milestones.getPlaybackStatus()
    review_buffer_in_seconds = (playback_manager["playbackBufferEnd"] - playback_manager["playbackBufferStart"])/1000
    ve_test.appium.tap_element(play_pause_button)
    sleep(review_buffer_in_seconds+5)

    "Verify streaming started and that Play image is presented"
    verify_streaming_playing(ve_test.milestones)
    play_button = ve_test.milestones.getElement([("name", "play_pause_button", "=="), ("state", "PLAYING", "==")])
    assert play_button

    "Verify streaming continues from current real time"
    playback_time = ve_test.milestones.getPlaybackStatus()["playbackBufferCurrent"]
    current_real_time = int(time())
    assert current_real_time - playback_time < 30
'''
