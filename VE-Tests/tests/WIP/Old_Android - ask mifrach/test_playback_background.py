__author__ = 'isinitsi'

from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition

' Global constants '
PAUSE = 3


def test_verify_playback_background():
    test = VeTestApi("test_playback_background")
    test.begin()

    test.screens.main_hub.tune_to_linear_channel_by_position(EventViewPosition.left_event)
    test.screens.playback.verify_streaming_playing()
    test.appium.key_event(3)
    test.wait(PAUSE)
    test.screens.playback.verify_streaming_stopped()

    test.end()
