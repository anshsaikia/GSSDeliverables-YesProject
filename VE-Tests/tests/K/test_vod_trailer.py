__author__ = 'dshalev'
""" test plan:  https://wiki.cisco.com/display/SPVSSPE/MF2406+-+VOD+Trailer
    dicomposition: https://wiki.cisco.com/pages/editpage.action?pageId=46171673 """

import pytest
import logging
from vgw_test_utils.IHmarks import IHmark
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.he_utils.he_utils import VodContentType


TIMEOUT = 5


def set_parental_rating_threshold(ve_test):
    pincode = ve_test.screens.pincode
    pincode.set_parental_rating_threshold(threshold=7)
    hhId = ve_test.configuration["he"]["generated_household"]
    ve_test.he_utils.setTenantValue(hhId, 'k')


def navigate_to_vod(ve_test, vod_asset):
    search = ve_test.screens.search
    full_content = ve_test.screens.full_content_screen

    asset_title = vod_asset['title']
    ve_test.screens.tv_filter.navigate()

    search.navigate()
    logging.info("searching for vod asset named {0}".format(asset_title))
    search.input_event_into_search_filed_and_search(asset_title)
    if ve_test.platform == "Android":
        search.navigate_to_action_menu_by_event_title(asset_title)
    else:
        full_content.tap_event_by_event_id(vod_asset['contentId'])
    ve_test.wait(2)


@IHmark.MF2406
@IHmark.FS_VE_VOD
@IHmark.FS_Playback
@IHmark.F_Playback_Trailer
@IHmark.O_Three_Rivers
@IHmark.O_Allianz
def test_play_trailer_not_restricted():
    test = VeTestApi("test_play_trailer_not_restricted")
    test.begin()
    asset = test.he_utils.getVodContent([VodContentType.WITH_LOW_RATED_TRAILER, VodContentType.NON_EROTIC])
    navigate_to_vod(test, asset)
    test.screens.vod_action_menu.play_trailer()

    test.wait(TIMEOUT)
    test.end()


@IHmark.MF2406
@IHmark.FS_VE_VOD
@IHmark.FS_Playback
@IHmark.F_Playback_Trailer
@IHmark.O_Three_Rivers
@IHmark.O_Allianz
def test_play_trailer_restricted():
    test = VeTestApi("test_play_trailer_restricted")
    test.begin()
    set_parental_rating_threshold(test)
    " relaunch app so new parental threshold will be cached"
    test.appium.restart_app()
    test.wait(TIMEOUT)
    asset = test.he_utils.getVodContent([VodContentType.WITH_HIGH_RATED_TRAILER, VodContentType.NON_EROTIC])
    navigate_to_vod(test, asset)
    test.screens.vod_action_menu.play_trailer(verify_streaming=False)
    test.wait(2)
    logging.info("enter correct pin")
    test.screens.pincode.enter_pin()
    test.wait(TIMEOUT)
    test.screens.playback.verify_streaming_playing()

    test.wait(TIMEOUT)
    test.end()


@IHmark.MF2406
@IHmark.FS_VE_VOD
@IHmark.FS_Playback
@IHmark.F_Playback_Trailer
@IHmark.O_Three_Rivers
@IHmark.O_Allianz
def test_stop_play_trailer():
    test = VeTestApi("test_stop_play_trailer")
    test.begin()
    asset = test.he_utils.getVodContent([VodContentType.WITH_LOW_RATED_TRAILER, VodContentType.NON_EROTIC])
    navigate_to_vod(test, asset)
    test.screens.vod_action_menu.play_trailer()
    test.wait(TIMEOUT)
    test.screens.trick_bar.navigate()
    test.wait(2)
    exit_element = test.milestones.getElement([("id", "back", "==")])
    test.appium.tap_element(exit_element)
    test.wait(2)
    test.screens.vod_action_menu.verify_active()

    test.end()


@IHmark.MF2406
@IHmark.FS_VE_VOD
@IHmark.FS_Playback
@IHmark.F_Playback_Trailer
@IHmark.O_Three_Rivers
@IHmark.O_Allianz
def test_end_of_play_trailer():
    test = VeTestApi("test_end_of_play_trailer")
    test.begin()
    asset = test.he_utils.getVodContent([VodContentType.WITH_LOW_RATED_TRAILER, VodContentType.NON_EROTIC])
    navigate_to_vod(test, asset)
    test.screens.vod_action_menu.play_trailer()
    test.wait(TIMEOUT)
    test.screens.trick_bar.navigate()
    test.screens.trick_bar.seek(is_tap=True, percent=85)
    test.screens.trick_bar.wait_untill_not_active()
    logging.info("playback ended")
    test.wait(1)

    test.screens.vod_action_menu.verify_active()

    test.end()
