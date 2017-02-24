import pytest
import logging
from tests_framework.ve_tests.ve_test import VeTestApi
from vgw_test_utils.IHmarks import IHmark


def check_content_provider_exclusion(test, Menu):
    my_test = test
    store = my_test.screens.store
    actionmenu = my_test.screens.action_menu
    dictAssetsId = {}
    my_test.wait(2)
    hub = my_test.screens.main_hub
    hub.navigate()
    my_test.wait(2)
    store.navigate()
    store.select_menu_item_by_title("RECOTESTS")
    my_test.wait(2)
    store.select_scroller_item_by_title(Menu)
    my_test.wait(2)
    my_current_screen = my_test.milestones.getElements()
    assets = my_test.milestones.getElementsArray([("event_source", "EVENT_SOURCE_TYPE_VOD", "==")], my_current_screen)
    #logging.info("VIP PROVIDER screen : %s", my_current_screen)
    my_test.log_assert(len(assets) != 0,'No assets in VIP PROVIDER classification')
    for asset in assets:
        relatedAssetsIdList = []
        assettitle = asset['title_text']
        #logging.info("\n MAIN ASSET : %s", asset)
        #logging.info("\n TITLE ASSET : %s", assettitle)
        #store.select_event_by_title(assettitle)
        my_test.appium.tap_element(asset)
        my_test.wait(2)
        my_current_screen = my_test.milestones.getElements()
        #logging.info("RELATED screen BEFORE Getting RELATED : %s", my_current_screen)
        if my_test.platform == "Android":
            window_width, window_height = my_test.milestones.getWindowSize()
            my_test.mirror.swipe_area(int(window_width / 2),
                                        window_height / 1.5, int(window_width / 2),
                                        window_height / 3, 1000)
            my_current_screen = my_test.milestones.getElements()
            logging.info("RELATED screen AFTER SWIPE ANDROID : %s", my_current_screen)
            relatedassets = my_test.milestones.getElementsArray([("event_source", "EVENT_SOURCE_TYPE_VOD", "==")],
                                                         my_current_screen)
            logging.info("\n RELATED ASSETS  : %s", relatedassets)
            mainAssetContent = asset
            #logging.info("\n MAIN ASSET DETAILS : %s", mainAssetContent)
            mainAssetIdStr = str((mainAssetContent["event_id"])[:-4])
            mainAssetIdArray = mainAssetIdStr.split("~")
            #logging.info('contentId: %s contentInstanceId: %s', mainAssetIdArray[0], mainAssetIdArray[1])
            mainAssetContentId = (mainAssetIdArray[0], mainAssetIdArray[1])
        else:
            relatedassets = my_test.milestones.getElementsArray([("event_source", "EVENT_SOURCE_TYPE_VOD", "==")],
                                                         my_current_screen)
            #logging.info("\n RELATED ASSETS  : %s", relatedassets)
            mainAssetContent = relatedassets[0]
            #logging.info("\n MAIN ASSET DETAILS : %s", mainAssetContent)
            relatedassets.pop(0)
            mainAssetIdStr = str((mainAssetContent["event_id"])[:-4])
            mainAssetIdArray = mainAssetIdStr.split("~")
            #logging.info('contentId: %s contentInstanceId: %s', mainAssetIdArray[0], mainAssetIdArray[1])
            mainAssetContentId = (mainAssetIdArray[0], mainAssetIdArray[1])

        #logging.info("\n mainAssetContentId : %s", mainAssetContentId)
        for relatedasset in relatedassets:
            #logging.info("\n relatedasset : %s", relatedasset)
            relatedassetdetails = ((relatedasset["event_id"])[:-4])
            #logging.info("\n RELATED ASSET DETAILS : %s", relatedassetdetails)
            relatedAssetsIdList.append(relatedassetdetails)
            store.scroll_related_section()

        dictAssetsId[mainAssetContentId] = relatedAssetsIdList
        #logging.info("\n ASSET ID LIST : %s", relatedAssetsIdList)
        store.go_to_previous_screen()
    my_test.log_assert(len(dictAssetsId) != 0,'No related assets in VIP PROVIDER classification')
    logging.info("\n DIC ASSET ID LIST : %s", dictAssetsId)

    #check provider names for all assets found
    for mainAssetContentId in dictAssetsId.keys():
        mainProvider = my_test.cmdc_queries.get_provider_from_contentId(mainAssetContentId[0])
        logging.info("\n MAIN CONTENT ID : %s", mainAssetContentId[0])
        logging.info("\n MAIN PROVIDER : %s", mainProvider)
        relatedList = dictAssetsId.get(mainAssetContentId)
        #check if related assets found for each provider
        if ((mainProvider=="relatedprovider1.com") or (mainProvider=="relatedprovider3.com")):  #VIP provider so only same assets provider should be found
            my_test.log_assert(len(relatedList)>0, "No related assets found for contentId %s" % mainAssetContentId[0])
            for related in relatedList:
                relatedIdArray = related.split("~")
                logging.info('contentId: %s contentInstanceId: %s', relatedIdArray[0], relatedIdArray[1])
                relatedId = (relatedIdArray[0], relatedIdArray[1])
                #check if related asset has same provider than mainContent
                provider = my_test.cmdc_queries.get_provider_from_contentId(relatedId[0])
                my_test.log_assert(provider != "","NO PROVIDER for %s" % relatedId[0])
                my_test.log_assert(provider==mainProvider, "asset %s have wrong related provider name for related asset %s found %s, should be %s" % (mainAssetContentId,relatedId,provider,mainProvider))
        else:
            my_test.log_assert(len(relatedList) > 0, "No related assets found for contentId %s" % mainAssetContentId[0])
            for related in relatedList:
                relatedIdArray = related.split("~")
                logging.info('contentId: %s contentInstanceId: %s', relatedIdArray[0], relatedIdArray[1])
                relatedId = (relatedIdArray[0], relatedIdArray[1])
                # check if related asset has same provider than mainContent
                provider = my_test.cmdc_queries.get_provider_from_contentId(relatedId[0])
                my_test.log_assert(provider != "","NO PROVIDER for %s" % relatedId[0])
                my_test.log_assert(((provider != "relatedprovider1.com") or (provider != "relatedprovider3.com")),
                                   "asset %s have wrong related provider name for related asset %s should not be %s" % (
                                   mainAssetContentId, relatedId, provider))

@IHmark.LV_L2
@IHmark.MF2048
@IHmark.MF2407
@pytest.mark.MF2048_VOD_Related_Vip_Content_Provider
@pytest.mark.MF2407_VOD_Exclusion_Restrict_Content_Provider
@pytest.mark.regression
@pytest.mark.export_regression_VOD_Related_Vip_Content_Provider
def test_related_specified_content_provider():
    my_test = VeTestApi("related:specified_provider")
    my_test.begin()
    check_content_provider_exclusion(my_test,"VIPPROVIDER")
    my_test.end()