__author__ = 'pculembo'

import pytest
import logging

from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS

def get_deviceId(elements, key):
    if elements == None:
        return False
    for element in elements:
        logging.info("element %s"%element)
        if key == element:
            return elements[element]
    return False

'''
Check that once the asset is bought, the option goes from RENT to PLAY
'''
@pytest.mark.sanity
@pytest.mark.FS_VOD
@pytest.mark.LV_L2
def test_vod_rent():
    test = VeTestApi("test_vod_rent")
    test.begin(screen=test.screens.fullscreen) 

    test.screens.playback.vod_manager.go_to_vod_asset("TVOD", True)
    #going into asset action menu
    test.validate_focused_item(2)
    logging.info("In action menu ")
    test.wait(3)

    status = test.wait_for_screen(5, "action_menu")

    #go to RENT option and rent the asset
    test.appium.key_event("KEYCODE_DPAD_UP")
    test.wait(3)
    elements = test.milestones.getElements()
    logging.info("getElements ActionMenu "+str(elements))
	
    #deactivate this test until milestones are corrected
    #entitlement = test.ve_test.milestones.get_value_by_key(elements, "prog_time")
    #logging.info("entitlement "+str(entitlement))
    #check = ("$" in entitlement)
    #logging.info("check "+str(check))
    #test.log_assert("$" in entitlement, "expected $ price, instead "+str(entitlement))

    action = test.milestones.get_value_by_key(elements, "focused_item")
    logging.info("focused_item "+str(action))
    test.log_assert(action == 'RENT', "expected action RENT, actual action "+str(action))
    test.appium.key_event("KEYCODE_DPAD_CENTER")
    test.wait(5)
	
#   enter correct pincode
    test.screens.pincode.enter_correct_pincode()

    if test.screens.playback.vod_manager.is_tvod_playable(test) :
        test.wait(10)

        #stop asset
        #launch action menu

        test.appium.key_event("KEYCODE_DPAD_CENTER")
        test.wait(5)
        #go on STOP
        test.appium.key_event("KEYCODE_DPAD_UP")
        test.wait(5)
        #select stop
        test.appium.key_event("KEYCODE_DPAD_CENTER")
        test.wait(5)

        #select asset
        test.appium.key_event("KEYCODE_DPAD_CENTER")
        test.wait(5)
        elements = test.milestones.getElements()
        logging.info("getElements ActionMenu "+str(elements))
        test.wait(5)

        #go on PLAY
        test.appium.key_event("KEYCODE_DPAD_UP")
        test.wait(5)

        elements = test.milestones.getElements()
        logging.info("getElements ActionMenu "+str(elements))
        test.wait(5)

        newaction = test.milestones.get_value_by_key(elements, "focused_item")
        test.log_assert(newaction in ['PLAY', 'RESUME'], "expected action PLAY or RESUME, actual action "+str(newaction))
        logging.info("focused_item "+str(newaction))
    else:
        status = test.wait_for_screen(CONSTANTS.SCREEN_TIMEOUT, 'notification')
        test.log_assert(status, "expected notification error screen , actual screen "+str(test.milestones.get_current_screen()))

    test.end()

'''
Check that adult contents are filtered in search screen
'''
@pytest.mark.sanity
@pytest.mark.FS_VOD
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_search
@pytest.mark.QA_search_selection
def test_vod_adult_contents_filtering_in_search():
    '''
    step 1 - Extract adult content from cmdc
    step 2 - Check vod adult asset exists in cmdc
    step 3 - Enter store search screen
    step 4 - Typing adult asset keywork
    step 5 - Get keywords list
    step 6 - Check adult asset title is not in keyword list
    '''

    VOD_ADULT_ASSET_CONTENT_ID = 'EROS0000000000000003~EROS0000000000000003'
    VOD_ADULT_ASSET_TITLE = 'Wild Orchid'
    VOD_ADULT_KEY_WORD = 'WIL'

    test = VeTestApi(title="test_vod_adult_contents")
    test.begin(screen=test.screens.fullscreen) 

    # step 1 - Extract adult content from cmdc
    he_utils = test.he_utils
    adult_contents = he_utils.get_vod_adult_contents_from_cmdc(adult="true",erotic="false")
    logging.info("adult_contents "+str(adult_contents) )

    # step 2 - Check vod adult asset exists in cmdc
    found = False
    for content in adult_contents:
        if VOD_ADULT_ASSET_CONTENT_ID == content:
            if VOD_ADULT_ASSET_TITLE == adult_contents[content]['title']:
                found = True

    test.log_assert(found, "Adult asset %s with title %s has not been found" %(VOD_ADULT_ASSET_CONTENT_ID,VOD_ADULT_ASSET_TITLE))

    # step 3 - Enter store search screen
    test.log_assert(test.screens.search.navigate(), "Moving to search screen from hub has failed")

    # step 4 - Typing adult asset keywork (part of the asset title)
    test.screens.filter.search_keyword_typing(VOD_ADULT_KEY_WORD)

    # step 5 - Get keywords list
    suggestions_list = test.milestones.get_value_by_key(test.milestones.getElements(),'suggestions_list')
    logging.info("Suggestions_list: %s" % suggestions_list)

    # step 6 - Check adult asset title is not in keyword list
    test.log_assert(not VOD_ADULT_ASSET_TITLE in suggestions_list, "Title %s should not appear in %s" %(VOD_ADULT_ASSET_TITLE,str(suggestions_list)))

    test.end()

'''
Check that erotic contents are filtered in search screen
'''
@pytest.mark.sanity
@pytest.mark.FS_VOD
@pytest.mark.LV_L3
def test_vod_erotic_contents_filtering_in_search():
    '''
    step 1 - Extract erotic content from cmdc
    step 2 - Check vod erotic asset exists in cmdc
    step 3 - Enter store search screen
    step 4 - Typing erotic asset keywork
    step 5 - Get keywords list
    step 6 - Check erotic asset title is not in keyword list
    '''

    VOD_EROTIC_ASSET_CONTENT_ID = 'EROS0000000000000001~EROS0000000000000001'
    VOD_EROTIC_ASSET_TITLE = 'Emmanuelle'
    VOD_EROTIC_KEY_WORD = 'EMM'

    test = VeTestApi("test_vod_erotic_contents_filtering_in_search")
    test.begin(screen=test.screens.fullscreen) 

    # step 1 - Extract erotic content from cmdc
    he_utils = test.he_utils
    adult_contents = he_utils.get_vod_adult_contents_from_cmdc(adult="false",erotic="true")
    logging.info("erotic_contents " + str(adult_contents))

    # step 2 - Check vod erotic asset exists in cmdc
    found = False
    for content in adult_contents:
        if VOD_EROTIC_ASSET_CONTENT_ID == content:
            if VOD_EROTIC_ASSET_TITLE == adult_contents[content]['title']:
                found = True

    test.log_assert(found, "Erotic asset %s with title %s has not been found" %(VOD_EROTIC_ASSET_CONTENT_ID,VOD_EROTIC_ASSET_TITLE))

    # step 3 - Enter store search screen
    test.log_assert(test.screens.search.navigate(), "Moving to search screen from hub has failed")
    # step 4 - Typing erotic asset keywork (part of the asset title)
    test.screens.filter.search_keyword_typing(VOD_EROTIC_KEY_WORD)

    # step 5 - Get keywords list
    suggestions_list = test.milestones.get_value_by_key(test.milestones.getElements(),'suggestions_list')
    logging.info("Suggestions_list: %s" % suggestions_list)

    # step 6 - Check erotic asset title is not in keyword list
    test.log_assert(not VOD_EROTIC_ASSET_TITLE in suggestions_list, "Title %s should not appear in %s" %(VOD_EROTIC_ASSET_TITLE,str(suggestions_list)))

    test.end()

'''
Check that adult contents are filtered in storeMenu screen
'''
@pytest.mark.sanity
@pytest.mark.FS_VOD
@pytest.mark.LV_L3
def test_vod_adult_contents_filtering_in_storeMenu():
    '''
    step 1 - Extract adult content from cmdc
    step 2 - Check vod adult asset exists in cmdc
    step 3 - Enter related classification in store
    step 4 - Get Asset list and Check adult assets are not there

    :return:
    '''

    VOD_ADULT_ASSET_CONTENT_ID = 'EROS0000000000000003~EROS0000000000000003'
    VOD_ADULT_ASSET_TITLE = 'Wild Orchid'
    VOD_ADULT_ASSET_CLASSIFICATION = 'TESTS'

    test = VeTestApi("test_vod_adult_contents")

    test.begin(screen=test.screens.fullscreen) 

    # step 1 - Extract adult content from cmdc
    he_utils = test.he_utils
    adult_contents = he_utils.get_vod_adult_contents_from_cmdc(adult="true",erotic="false")
    logging.info("adult_contents "+ str(adult_contents))

    test.log_assert(adult_contents is not None and len(adult_contents)>0, "There's no adult content in cmdc")

    # step 2 - Check vod adult asset used by this test exists in cmdc
    found = False
    for content in adult_contents:
        if VOD_ADULT_ASSET_CONTENT_ID == content:
            for i in range(0, len(adult_contents[content]['classificationKeys'])):
                if VOD_ADULT_ASSET_CLASSIFICATION in adult_contents[content]['classificationKeys'][i]:
                    found = True
                    break

    test.log_assert(found, "Adult asset %s with classification %s has not been found" %(VOD_ADULT_ASSET_CONTENT_ID,VOD_ADULT_ASSET_CLASSIFICATION))

    # step 3 - Enter related classification in store
    test.log_assert(test.screens.mainhub.navigate_to_store(), "Navigate to store has failed")
    test.screens.playback.vod_manager.go_to_vod_asset("TVOD", True)

    # step 4 - Get Asset list and  Check adult assets are not there
    elements = test.milestones.getElements()
    logging.info("elements "+str(elements))
    asset_list = test.milestones.get_value_by_key(elements, "asset_list")
    logging.info("asset_list "+str(asset_list))
    test.log_assert(not VOD_ADULT_ASSET_TITLE in asset_list, "Title %s should not appear in %s" %(VOD_ADULT_ASSET_TITLE,str(asset_list)))

    test.end()

'''
Check that erotic contents are filtered in storeMenu screen
'''
@pytest.mark.sanity
@pytest.mark.FS_VOD
@pytest.mark.LV_L3
def test_vod_erotic_contents_filtering_in_storeMenu():
    '''
    step 1 - Extract erotic content from cmdc
    step 2 - Check vod erotic asset exists in cmdc
    step 3 - Enter related classification in store
    step 4 - Get Asset list and Check adult assets are not there

    :return:
    '''

    VOD_EROTIC_ASSET_CONTENT_ID = 'EROS0000000000000001~EROS0000000000000001'
    VOD_EROTIC_ASSET_TITLE = 'Emmanuelle'
    VOD_EROTIC_ASSET_CLASSIFICATION = 'Kinder-Ecke:Kinder-Mediathek:CartoonNetwork:StevenUniverse'

    test = VeTestApi("test_vod_erotic_contents")
    test.begin(screen=test.screens.fullscreen) 

    # step 1 - Extract erotic content from cmdc
    he_utils = test.he_utils
    adult_contents = he_utils.get_vod_adult_contents_from_cmdc(adult="false",erotic="true")
    logging.info("erotic_contents " + str(adult_contents))

    test.log_assert(adult_contents is not None and len(adult_contents)>0, "There's no erotic content in cmdc")

    # step 2 - Check vod erotic asset used by this test exists in cmdc
    found = False
    for content in adult_contents:
        if VOD_EROTIC_ASSET_CONTENT_ID == content:
            for i in range(0, len(adult_contents[content]['classificationKeys'])):
                if VOD_EROTIC_ASSET_CLASSIFICATION in adult_contents[content]['classificationKeys'][i]:
                    found = True
                    break

    test.log_assert(found, "Erotic asset %s with classification %s has not been found" %(VOD_EROTIC_ASSET_CONTENT_ID,VOD_EROTIC_ASSET_CLASSIFICATION))

    # step 3 - Enter related classification in store
    test.screens.main_hub.navigate()
    test.log_assert(test.screens.main_hub.navigate_to_store(), "to_store_from_hub has failed")
    test.screens.playback.vod_manager.go_to_vod_asset("TVOD", True)

    # step 4 - Get Asset list and  Check erotic asset is not there
    elements = test.milestones.getElements()
    asset_list = test.milestones.get_value_by_key(elements, "asset_list")
    logging.info("asset_list "+str(asset_list))
    test.log_assert(not VOD_EROTIC_ASSET_TITLE in asset_list, "Title %s should not appear in %s" %(VOD_EROTIC_ASSET_TITLE,str(asset_list)))

    test.end()
