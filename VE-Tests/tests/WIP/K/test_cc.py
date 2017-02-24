__author__ = 'eacarq'

from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.screen import ScreenActions
from vgw_test_utils.IHmarks import IHmark

import pytest
import logging

# CC support is not in the manifest and not in the catalague
# so we resort to hardcoding a test URL ...
CC_FILTER = {'url':'http://devimages.apple.com.edgekey.net/streaming/examples/bipbop_4x3/bipbop_4x3_variant.m3u8'}

@IHmark.LV_L2
@pytest.mark.MF1801
@pytest.mark.level2
def test_cc():
    ve_test = VeTestApi("test_cc")
    ve_test.begin()

    hhId = ve_test.configuration["he"]["generated_household"]
    ve_test.he_utils.setTenantValue(hhId, 'k')

    ve_test.screens.ksettings.navigate()
    ve_test.wait(5)

    logging.info("Select CC1")
    ccValue = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_CLOSED_CAPTIONS","general")
    langValue = "CC1"
    select_settings = ve_test.screens.ksettings.select(ccValue.upper(),langValue.upper())
    ve_test.log_assert(select_settings, "can not select "+langValue+ " in "+ccValue)
    ve_test.wait(2)

    logging.info("Back to main hub")
    ve_test.appium.back()
    ve_test.wait(5)


    logging.info("Zap to CC channel")
    ve_test.screens.closed_caption.play_live_cc(CC_FILTER)
    ve_test.wait(5)

    logging.info("Check CC is playing")
    playbackStatus = ve_test.milestones.getPlaybackStatus()
    stream_lang_played = [stream['language'] for stream in playbackStatus['playbackStreams'] if stream['type'] == "TEXT"]
    ve_test.log_assert("CC1" in stream_lang_played, "played CC [" +str(stream_lang_played) +"] does correspond to the selected one [CC1]")

    ve_test.end()
