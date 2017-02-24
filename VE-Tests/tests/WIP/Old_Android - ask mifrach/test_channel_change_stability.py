__author__ = 'bahirsch'

import logging
import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition
from tests_framework.ui_building_blocks.screen import ScreenActions
import random

' Global constants '
NUMBER_OF_STREAM_SWITCH_TESTS = 100

@pytest.mark.stability
@pytest.mark.channelchange_stability
#MF959 - Channel change via gesture [Android]
#Play the 1st channel in lineup (or the default channel), repeat in a loop 100 times: {swipe 1 channel up, wait for playback to start, play 5 seconds} then 1 channel down. Verify that the URL that the app receives for the channel matches that one it received before. During the change, verify you get the URL of the 1st channel once more. (list is cyclic)
def test_channel_change_stability_random_gestures():

    ve_test = VeTestApi("test_channel_change_stability_random_gestures")
    ve_test.begin()

    fullscreen = ve_test.screens.fullscreen
    infolayer = ve_test.screens.infolayer
    playback = ve_test.screens.playback

    ve_test.screens.main_hub.tune_to_linear_channel_by_position(EventViewPosition.left_event)
    infolayer.dismiss()
    status = playback.verify_streaming_playing(skip_not_playable_channel= True)
    prev_session_id = cur_session_id = status['sso']['sessionId']

    for index in range(NUMBER_OF_STREAM_SWITCH_TESTS):

        fullscreenactions_list = (ScreenActions.DOWN, ScreenActions.UP)
        swipe_direction = random.choice(list(fullscreenactions_list))
        fullscreen.navigate()
        logging.info('Channel switch iteration number: %s   swipe_direction: %s' %(index,swipe_direction))
        fullscreen.channel_change(swipe_direction, skip_not_playable_channel=True)
        ve_test.wait(3)

        status =  playback.verify_streaming_playing(skip_not_playable_channel= True)
        if('sso' in status):
            cur_session_id = status['sso']['sessionId']
        else:
            cur_session_id = status['currentChannelId']
        ve_test.log_assert(cur_session_id != prev_session_id, 'The current session should not be the same as the previous session, after two finger swipe channel change request on full screen')
        prev_session_id = cur_session_id

    ve_test.end()