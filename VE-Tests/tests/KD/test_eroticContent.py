__author__ = 'abarilan'

import logging
import pytest
from tests_framework.he_utils.he_utils import VodContentType
from tests_framework.ui_building_blocks.KD.pincode import YouthChanneltype
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import Showcases
from vgw_test_utils.IHmarks import IHmark

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF522
@pytest.mark.MF522_erotic_content_vod
@pytest.mark.skip(reason="Can't run this test until we get the new CMDC fix for the erotic flag")
@pytest.mark.level2
def test_search_for_erotic_content():
    ve_test = VeTestApi("test_search_for_erotic_content")
    ve_test.begin(preload="vod")

    action_menu = ve_test.screens.vod_action_menu
    pin_screen = ve_test.screens.pincode
    search = ve_test.screens.search
    infolayer = ve_test.screens.infolayer

    "find vod erotic content event"
    try:
        asset = ve_test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.EROTIC])
    except Exception as e:
        ve_test.log_assert(False, "Failed to get erotic vod content, error=%s" % e)

    if not 'title' in asset or not asset['title']:
        logging.info("no erotic content found")
        ve_test.end()

    "validate event is reachable through store"
    ve_test.screens.store.navigate_to_vod_asset_by_title(asset['title'])
    action_menu.verify_active()

    "validate event requests pin code for play"
    action_menu.play_asset(False)
    ve_test.wait(3)
    infolayer.tap_unlock_program()
    pin_screen.verify_active()

    "search for that event"
    search.navigate()

    "validate event is not found in suggestions"
    search.input_event_into_search_filed_and_search(asset['title'])
    search.verify_no_suggestions()

    "validate event is not found in search results"
    search.verify_no_results()

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF607
@pytest.mark.MF607_exclude_erotic_content_from_recommendations
def test_for_erotic_content_in_recommendations():
    ve_test = VeTestApi("test_for_erotic_content_in_recommendations")

    ve_test.begin()
    main_hub = ve_test.screens.main_hub
    main_hub.navigate()
    ve_test.wait(2)
    main_hub.check_erotic_content_linear()
    main_hub.check_erotic_content_VOD()

    ve_test.end()