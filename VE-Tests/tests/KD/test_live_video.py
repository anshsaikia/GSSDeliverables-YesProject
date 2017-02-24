__author__ = 'isinitsi'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition


@pytest.mark.regression
@pytest.mark.export_regression_MF241_Watch_live_ABR
@pytest.mark.MF241_playlinear
#MF241 - Watch live ABR [Android]
def test_live_video():
    test = VeTestApi("test_live_video")
    test.begin()

    channel_id, channel_prop = test.he_utils.getLinearContentABR('clear')
    test.screens.zaplist.tune_to_channel_by_sek(channel_id, verify_streaming_started =True)

    test.end()
