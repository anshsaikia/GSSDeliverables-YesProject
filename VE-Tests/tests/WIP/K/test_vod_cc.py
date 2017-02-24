__author__ = 'eacarq'

from tests_framework.ve_tests.ve_test import VeTestApi

import pytest
import logging

VOD_CC_ASSET="All Cheerleaders Die"

@pytest.mark.MF1801
@pytest.mark.level2
def test_vod_cc():
    ve_test = VeTestApi("test_vod_cc")
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


    logging.info("Play VOD CC asset")
    ve_test.screens.tv_filter.navigate()
    search = ve_test.screens.search
    search.navigate()
    search.input_event_into_search_filed_and_search(VOD_CC_ASSET)
    search.navigate_to_action_menu_by_event_title(VOD_CC_ASSET)
    ve_test.wait(5)
    play_button = ve_test.milestones.getElement([("name", "actions_menu_play_button", "==")])
    ve_test.appium.tap_element(play_button)
    ve_test.wait(10)

    logging.info("Check CC is playing")
    playbackStatus = ve_test.milestones.getPlaybackStatus()
    stream_lang_played = [stream['language'] for stream in playbackStatus['playbackStreams'] if stream['type'] == "TEXT"]
    ve_test.log_assert("CC1" in stream_lang_played, "played CC [" +str(stream_lang_played) +"] does correspond to the selected one [CC1]")

    ve_test.end()
