__author__ = 'eacarq'

from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.screen import ScreenActions

import pytest
import logging

STREAM_TYPE_SMPTEE_ID3 = "SMPTEE_ID3"
STREAM_TYPE_AUDIO = "AUDIO"
# DVB sub support is not in the manifest and not in the catalague
# so we resort to hardcoding a test URL ...
DVB_SUB_FILTER = {'url':'http://ubu-iptv01.cisco.com/androidtv/streams/dvbsub/extract1/index.m3u8'}
MULTI_AUDIO_FILTER = {'url':'http://live-2.mpe.mos.ih-iptv.labs.fr.ciscolabs.com/live-2-1/2-channel22/2-channel22.m3u8'}
MULTI_AUDIO_VOD_ASSET="MULTI AUDIO AWAKENING"
DVB_SUB_VOD_ASSET= "SVOD DVB Subtitle The F Word"
# this needs to be present both in the asset and in the settings
SETTINGS_SUBTITLE_TEST_LANG="por"

PLAYER_MENU_ITEM_ID = {
    STREAM_TYPE_AUDIO : "playermenu_audio_item",
    STREAM_TYPE_SMPTEE_ID3 : "playermenu_subtitle_item"
}


@pytest.mark.MF1047
@pytest.mark.level2
def test_dvb_subtitle_settings_live():
    ve_test = VeTestApi("test_dvb_subtitle")
    ve_test.begin()

    ve_test.screens.dvb_subtitle.settings_select_subtitle_lang(SETTINGS_SUBTITLE_TEST_LANG)
    ve_test.screens.dvb_subtitle.play_live_dvb_sub(DVB_SUB_FILTER)

    logging.info("Check DVB sub language")
    (status, stream_lang) = ve_test.screens.playback.playback_streams_played(STREAM_TYPE_SMPTEE_ID3, SETTINGS_SUBTITLE_TEST_LANG)
    ve_test.log_assert(status, "player did not switch to %s (still %s)" % (SETTINGS_SUBTITLE_TEST_LANG, stream_lang))

    ve_test.end()


@pytest.mark.MF1047
@pytest.mark.level2
def test_dvb_subtitle_settings_vod():
    ve_test = VeTestApi("test_vod_dvb_subtitle")
    ve_test.begin()

    ve_test.screens.dvb_subtitle.settings_select_subtitle_lang(SETTINGS_SUBTITLE_TEST_LANG)
    ve_test.screens.dvb_subtitle.play_vod_dvb_sub(DVB_SUB_VOD_ASSET)

    logging.info("Check DVB sub language")
    (status, stream_lang) = ve_test.screens.playback.playback_streams_played(STREAM_TYPE_SMPTEE_ID3, SETTINGS_SUBTITLE_TEST_LANG)
    ve_test.log_assert(status, "player did not switch to %s (still %s)" % (SETTINGS_SUBTITLE_TEST_LANG, stream_lang))

    ve_test.end()


def player_menu_test_selection(ve_test, stream_type, lang):
    logging.info("selecting (%s, %s)" % (stream_type, lang))
    item_id = PLAYER_MENU_ITEM_ID[stream_type]

    item_label = ve_test.milestones.get_dic_value_by_key(ve_test.screens.dvb_subtitle.lang_to_dic(lang)).upper()

    # screen with the trick mode bar is either infolayer (for live) or trick_bar (vod)
    # but we don't know here which ...
    current_screen = ve_test.milestones.get_current_screen()
    if current_screen == "trick_bar" or current_screen == "infolayer" or current_screen == "audio_subtitle_overlay":
        pass
    elif current_screen == "fullscreen":
        ve_test.ui.center_tap()
        ve_test.wait(2)
        current_screen = ve_test.milestones.get_current_screen()
        ve_test.log_assert(current_screen in ["infolayer", "trick_bar"], "trick bar did not appear after 2s (still %s)" % current_screen)
    else:
        ve_test.log_assert(False, "%s but should in be [trick_bar, infolayer, fullscreen]")

    # show the menu
    if ve_test.platform == "iOS":
        subtitle_button = ve_test.milestones.get_element_by_id(None, "audio_subtitle_button")
        if None == subtitle_button:
            subtitle_button = ve_test.milestones.get_element_by_id(None, "audioSubtitlesButton")
            ve_test.appium.tap_element(subtitle_button)
            ve_test.wait(1)
    else:
        subtitle_button = ve_test.milestones.get_element_by_id(None, "media_button");
        if subtitle_button["state"] == "OFF":
            subtitle_button = ve_test.milestones.get_element_by_id(None, "audioSubtitlesButton")
            ve_test.appium.tap_element(subtitle_button)
            ve_test.wait(1)

    # get the entry for lang
    elements = ve_test.milestones.getElements()
    menu_item = [elt for elt in elements if elt.get("id", "") == item_id and elt.get("title_text", "").upper() == item_label]
    ve_test.log_assert(len(menu_item) == 1, "no player menu entry for %s/%s" % (lang, item_label))
    menu_item = menu_item[0]

    # now select it
    ve_test.appium.tap_element(menu_item)
    ve_test.wait(1)

    # check UI
    elements = ve_test.milestones.getElements()
    menu_item = [elt for elt in elements if elt.get("id", "") == item_id and elt.get("title_text", "").upper() == item_label]
    ve_test.log_assert(len(menu_item) == 1, "no player menu entry for %s/%s" % (lang, item_label))
    menu_item = menu_item[0]
    ve_test.log_assert(menu_item.get("state", "") in ["SELECTION", "INITIAL_SELECTION"], "entry %s not selected" % item_label)

    # check player
    (status, stream_lang) = ve_test.screens.playback.playback_streams_played(stream_type, lang)
    ve_test.log_assert(status, "player did not switch to %s (still %s)" % (lang, stream_lang))

    # check that the item is now INITIAL_SELECTION
    ve_test.appium.tap_element(subtitle_button)
    ve_test.wait(1)
    ve_test.appium.tap_element(subtitle_button)
    ve_test.wait(1)

    # get the new entry
    elements = ve_test.milestones.getElements()
    menu_item = [elt for elt in elements if elt.get("id", "") == item_id and elt.get("title_text", "").upper() == item_label]
    ve_test.log_assert(len(menu_item) == 1, "no player menu entry for %s/%s" % (lang, item_label))
    menu_item = menu_item[0]
    ve_test.log_assert(menu_item.get("state", "") == "INITIAL_SELECTION", "player menu entry for %s/%s is not initial selection" % (lang, item_label))


@pytest.mark.MF1047
@pytest.mark.level2
def test_dvb_subtitle_live_playermenu():
    ve_test = VeTestApi("test_dvb_subtitle")
    ve_test.begin()

    hhId = ve_test.configuration["he"]["generated_household"]
    ve_test.he_utils.setTenantValue(hhId, 'k')

    logging.info("Zap to DVB sub channel")
    ve_test.screens.dvb_subtitle.play_live_dvb_sub(DVB_SUB_FILTER)
    playbackStatus = ve_test.milestones.getPlaybackStatus()
    playbackStreams = ve_test.milestones.getPlaybackStatus('playbackStreams')
    allPlaybackStreams = ve_test.milestones.getPlaybackStatus('allPlaybackStreams')
    stream_sub_languages = [stream['language'] for stream in allPlaybackStreams if stream['type'] == STREAM_TYPE_SMPTEE_ID3]
    stream_sub_played = [stream['language'] for stream in playbackStreams  if stream['type'] == STREAM_TYPE_SMPTEE_ID3]

    logging.info("DVB subs detected: %s, playing: %s" % (str(stream_sub_languages), str(stream_sub_played)))

    ve_test.log_assert(len(stream_sub_languages) > 0, "no DVB subtitles detected in %s" % playbackStatus["sso"]["sessionPlaybackUrl"])

    for lang in stream_sub_languages:
        player_menu_test_selection(ve_test, STREAM_TYPE_SMPTEE_ID3, lang)
        ve_test.wait(1)

    player_menu_test_selection(ve_test, STREAM_TYPE_SMPTEE_ID3, "none")

    ve_test.end()


@pytest.mark.MF1047
@pytest.mark.level2
def test_dvb_subtitle_vod_playermenu():
    ve_test = VeTestApi("test_dvb_subtitle")
    ve_test.begin()

    hhId = ve_test.configuration["he"]["generated_household"]
    ve_test.he_utils.setTenantValue(hhId, 'k')

    logging.info("Zap to DVB sub channel")
    ve_test.screens.dvb_subtitle.play_vod_dvb_sub(DVB_SUB_VOD_ASSET)

    playbackStatus = ve_test.milestones.getPlaybackStatus()

    stream_sub_languages = [stream['language'] for stream in playbackStatus['allPlaybackStreams'] if stream['type'] == STREAM_TYPE_SMPTEE_ID3]
    stream_sub_played = [stream['language'] for stream in playbackStatus['playbackStreams'] if stream['type'] == STREAM_TYPE_SMPTEE_ID3]

    logging.info("DVB subs detected: %s, playing: %s" % (str(stream_sub_languages), str(stream_sub_played)))

    ve_test.log_assert(len(stream_sub_languages) > 0, "no DVB subtitles detected in %s" % playbackStatus["sso"]["sessionPlaybackUrl"])

    for lang in stream_sub_languages:
        player_menu_test_selection(ve_test, STREAM_TYPE_SMPTEE_ID3, lang)
        ve_test.wait(1)

    player_menu_test_selection(ve_test, STREAM_TYPE_SMPTEE_ID3, "none")

    ve_test.end()

@pytest.mark.skip(reason="should this be here ?")
def test_multi_audio_live_playermenu():
    ve_test = VeTestApi("test_dvb_subtitle")
    ve_test.begin()

    hhId = ve_test.configuration["he"]["generated_household"]
    ve_test.he_utils.setTenantValue(hhId, 'k')

    logging.info("Zap to DVB sub channel")
    ve_test.screens.playback.play_live_multi_audio(MULTI_AUDIO_FILTER)

    playbackStatus = ve_test.milestones.getPlaybackStatus()

    stream_sub_languages = [stream['language'] for stream in playbackStatus['allPlaybackStreams'] if stream['type'] == STREAM_TYPE_AUDIO]
    stream_sub_played = [stream['language'] for stream in playbackStatus['playbackStreams'] if stream['type'] == STREAM_TYPE_AUDIO]

    logging.info("DVB subs detected: %s, playing: %s" % (str(stream_sub_languages), str(stream_sub_played)))

    ve_test.log_assert(len(stream_sub_languages) > 0, "no DVB subtitles detected in %s" % playbackStatus["sso"]["sessionPlaybackUrl"])

    for lang in stream_sub_languages:
        player_menu_test_selection(ve_test, STREAM_TYPE_AUDIO, lang)
        ve_test.wait(1)

    ve_test.end()
