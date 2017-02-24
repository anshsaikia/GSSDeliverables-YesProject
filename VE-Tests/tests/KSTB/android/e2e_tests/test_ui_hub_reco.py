__author__ = 'sbernada'

import pytest
import logging
from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS


def cleanFixedhhID(test,fixed_hhID):
    # Do not cleanup fixed householdId
    for hhId in test.he_utils.houseHolds:
        if hhId == fixed_hhID:
            logging.info("hhId found:  %s" % hhId)
            test.he_utils.houseHolds.remove(hhId)
            break

'''
Check that erotic and/or adult contents are filtered in Hub TV screen
'''
@pytest.mark.non_regression
@pytest.mark.FS_HUB
@pytest.mark.F_Recos
@pytest.mark.LV_L2
def test_erotic_adult_contents_filtering_from_reco_HubTVMenu():
    '''
    step 1 - select fixed householdID
    step loop :
        step 2 - Enter Hub TV Menu
        step 3 - Get related assets list
        step 4 - if no recommended assets zap to another service
    step 5 - ask asset detail from cmdc
    step 6 - Check assets are not adult and/or erotic
    :return:
    '''
    # we need to use an existing household, for now TA default profile doesnt work properly, so no preference recommendations for fresh household
    # Define fixed householdId 
    fixed_hhID = ""
    fixed_password = "123"

    test = VeTestApi("test_erotic_adult_contents_filtering_from_reco_HubTVMenu")

    # check for an existing household
    for n in range(1, 20):
        if test.he_utils.isHouseHoldExist("h-iptv"+str(n)):
            fixed_hhID="h-iptv"+str(n)
            test.is_fixed_household = True
            test.configuration["he"]["household"] = fixed_hhID
            test.configuration["he"]["username"] = fixed_hhID
            test.configuration["he"]["password"] = fixed_password
            break

    test.log_assert(fixed_hhID!="", "There's no existing 'h-iptv' household available")

    test.begin(screen=test.screens.main_hub)

    TV_recommended_assets_list=[]
    for i in range (3, 6):
        # step 3 - Enter related classification in Hub TV
        status = test.screens.main_hub.focus_tvfilter_item_in_hub()
        if status==False: 
            cleanFixedhhID(test,fixed_hhID)
        test.log_assert(status, "focus_tvfilter_item_in_hub has failed")
    
        assetName = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_asset")
        logging.info("TV assetName: %s" % assetName)
    
        #move to recommended asset
        test.move_towards('right',1)
        asset = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_asset")
        logging.info("asset: %s" % asset)
        #check if recommended asset exist
        if asset!=assetName:
            while asset not in TV_recommended_assets_list:  # loop to count assets
                logging.info("asset: %s" % asset)
                TV_recommended_assets_list.append(asset)
                test.move_towards('right',1)        # next asset
                asset = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_asset")   # next asset

        #check if we need to zap
        if TV_recommended_assets_list!=[]:
            break
        else:
            #go to fullscreen from Hub to zap then go back to hub
            test.key_press("KEYCODE_BACK")
            test.wait(CONSTANTS.GENERIC_WAIT)
            #zap to service i
            test.screens.playback.dca(i)
            test.wait_for_screen(CONSTANTS.SCREEN_TIMEOUT, "fullscreen")
            #go back to Hub
            test.wait(CONSTANTS.GENERIC_WAIT)
            status = test.screens.main_hub.navigate()
            if status==False: 
                cleanFixedhhID(test,fixed_hhID)
            
            

    cleanFixedhhID(test,fixed_hhID)

    # Check recommended assets are not adult and/or eroctic 
    logging.info("number of recommended assets found : %d" % len(TV_recommended_assets_list))
    for asset in TV_recommended_assets_list:
        #replace : with %3A
        assetName = asset.replace(':','%3A')
        contents = test.he_utils.get_content_list_from_search(assetName.replace(' ','%20'),"ltv","true")
        contentsNum = len(contents)
        #if len=0 it means that we have a title concatenated with serie data
        if contentsNum==0:
            assetString = []
            assetString = assetName.split()
            for n in range(1, len(assetString)):
                assetName = ' '.join(assetString[:-n])
                #logging.info("assetName : %s" % assetName)
                contents = test.he_utils.get_content_list_from_search(assetName.replace(' ','%20'),"ltv","true")
                contentsNum = len(contents)
                #logging.info("len(assetString):%d, n:%d" % (len(assetString),n))
                if contentsNum==1:
                    break

        test.log_assert(contentsNum==1, "Warning %d assets have same title : %s" % (contentsNum,asset))
        test.log_assert(contents[0]['adult']==False,  "Recommended asset '%s' is adult"  % asset)
        test.log_assert(contents[0]['erotic']==False,  "Recommended asset '%s' is erotic"  % asset)
    
    test.end()


