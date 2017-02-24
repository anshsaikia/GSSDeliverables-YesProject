import pytest
import logging
from tests_framework.ve_tests.ve_test import VeTestApi
from vgw_test_utils.IHmarks import IHmark

logger = logging.getLogger("MF2165")
logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(name)-5s %(levelname)-8s : %(message)s')


@IHmark.LV_L2
@IHmark.O_Roland_Garros
@IHmark.MF2165
@pytest.mark.MF2165_VOD_Hub_Top_List_Edito
@pytest.mark.level2
@pytest.mark.vod_hub
def test_vod_hub_toplist_edito():
    test = VeTestApi("test_vod_hub_toplist_edito")
    test.begin()
    store = test.screens.store
    #INITIALIZE TOPLIST WITH LEARN ACTIONS AND TOPLIST FULLREFRESH ACTION
    test.ta_queries.initialize_top_list()

    #NAVIGATE TO VOD HUB
    store.navigate_no_tap()

    my_previous_screen = list()
    hub_assets_contentIds = list()

    #GET ALL ASSET CONTENT ID IN VOD HUB : 3 rows
    my_current_screen = test.milestones.getElements()
    row = 0
    #while my_previous_screen != my_current_screen:
    for row in range(0,3):
        #my_previous_screen = my_current_screen
        #my_current_screen = test.milestones.getElements()
        hub_vod_elements = test.milestones.getElementsArray([("event_source", "EVENT_SOURCE_TYPE_VOD", "==")], my_current_screen)
        test.log_assert(hub_vod_elements,"No VOD elements in HUB store ")
        for vod_element in hub_vod_elements:
            vodeventid = str((vod_element["event_id"])[:-4])
            vodeventArray = vodeventid.split("~")
            hub_assets_contentIds.append(vodeventArray[0])
        window_width, window_height = test.milestones.getWindowSize()
        test.appium.swipe_area(window_width / 2, window_height / 10 * 8, window_width / 2, window_height / 10 * 9, 0)
        row += 1
        test.wait(1)
        my_current_screen = test.milestones.getElements()

    #GET EDITORIAL ASSETS FROM CMDC
    cmdc_editorial_assetsContentId = test.cmdc_queries.get_editorial_contentId_list()

    #FILTER EDITORIAL ASSETS FROM HUB VOD ASSETS
    edito_assets_from_hub = hub_assets_contentIds[0:(len(cmdc_editorial_assetsContentId))]

    #FILTER TOPLIST ASSETS FROM HUB VOD ASSETS
    toplist_assets_from_hub = hub_assets_contentIds[(len(cmdc_editorial_assetsContentId)):]
    logging.info('VOD ASSETS CONTENTID IN HUB : %s' % hub_assets_contentIds)
    logging.info('EDITO ASSETS CONTENTID IN HUB : %s' % edito_assets_from_hub)
    logging.info('TOP LIST ASSETS CONTENTID IN HUB : %s' % toplist_assets_from_hub)
    logging.info('EDITORIAL ASSETS CONTENTID FROM CMDC: %s' % cmdc_editorial_assetsContentId)
    test.log_assert(cmdc_editorial_assetsContentId)

    #GET TOPLIST ASSETS ASSETS FROM TA
    ta_toplist_assetsContentId = test.ta_queries.get_toplist_contentId_list()
    test.log_assert(ta_toplist_assetsContentId)
    logging.info('TOPLIST ASSETS CONTENTID FROM TA: %s' % ta_toplist_assetsContentId)

    #CHECK THAT EDITO HUB STORE ASSETS ARE IN EDITO CMDC RESULTS
    test.log_assert(len(set(edito_assets_from_hub).intersection(cmdc_editorial_assetsContentId)) == len(cmdc_editorial_assetsContentId), "EDITORIAL LIST recommendations don't match")
    #CHECK THAT TOPLIST HUB STORE ASSETS ARE IN TOPLIST TA RESULTS
    test.log_assert(len(set(toplist_assets_from_hub).intersection(ta_toplist_assetsContentId)) == len(toplist_assets_from_hub), "TOP LIST recommendations don't match")

    test.end()