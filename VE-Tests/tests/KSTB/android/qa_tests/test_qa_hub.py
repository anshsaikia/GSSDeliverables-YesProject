__author__ = 'Oceane Team'

import pytest
import logging

from tests_framework.ve_tests.ve_test import VeTestApi
from tests.KSTB.android.e2e_tests.test_light_sanity import display_pretty_current_screen
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS


#########################################################
#                       private Functions                 #
#########################################################

def checkHubItems(test_qa_hub, HUB_ITEM_LIST):
    """
    private function : assuming current screen is hub. This methode browses hub menu and check items/subitems by navigating into them.
    :param test_qa_hub: current test instance
    :param HUB_ITEM_LIST: list of item/sub item to navigate in and to be checked
    :return:
    """

    currentFocusedItem = str(test_qa_hub.screens.action_menu.get_focused_item())
    initialFocusedItem = currentFocusedItem
    FocusedItemCounter = 0
    screen_name = "empty"

    while initialFocusedItem != currentFocusedItem or screen_name == "empty":
        screen_name = test_qa_hub.milestones.get_current_screen()
        logging.info("step 4 : current screen is :" + screen_name)

        # prepare assert log message
        errorMessage = "HUB:NAVIGATION : unknown HUB item: " + currentFocusedItem

        # check current focused item is in expected list of hub menu
        test_qa_hub.log_assert(HUB_ITEM_LIST.has_key(currentFocusedItem), errorMessage)

        # skip navigation in LIBRARY as it is empty (not accessible)
        if currentFocusedItem in CONSTANTS.HUB_LIBRARY_NAMES_BY_LANG:
            logging.info("step 4 : current selected menu is LIBRARY. We do not check navigation into empty LIBRARY as it shall not be accessible. \
                                     A reccord must be done before accessing this menu, but this is another test about cDVR...")
        else:
            # enter into selected item
            test_qa_hub.validate_focused_item(CONSTANTS.GENERIC_WAIT)

            # check we are in selected item
            screen_name = test_qa_hub.milestones.get_current_screen()

            # prepare assert log message
            errorMessage = "HUB:NAVIGATION : Expected navigation in HUB subitem " + currentFocusedItem + " failed, current is = " + screen_name \
                           + " instead of " + HUB_ITEM_LIST[currentFocusedItem]

            # check current screen matches with hUB focused item
            test_qa_hub.log_assert(HUB_ITEM_LIST[currentFocusedItem] == screen_name, errorMessage)

            # exit from selected item with back key
            test_qa_hub.go_to_previous_screen(CONSTANTS.GENERIC_WAIT)

        # check we are in HUB screen
        screen_name = test_qa_hub.milestones.get_current_screen()
        errorMessage = "HUB:NAVIGATION : return to HUB from " + currentFocusedItem + " failed ! current screen name is " + screen_name
        test_qa_hub.log_assert(screen_name == "main_hub", errorMessage)

        # go to next item
        test_qa_hub.move_towards('up', 1, False)
        currentFocusedItem = str(test_qa_hub.screens.action_menu.get_focused_item())

        # count number of items checked to be compared with number of item in expected list
        FocusedItemCounter += 1

    # check all expected HUB items have been found :
    errorMessage = "HUB:NAVIGATION : all expected HUB items have NOT been found !!!"
    test_qa_hub.log_assert(FocusedItemCounter == len(HUB_ITEM_LIST), errorMessage)



@pytest.mark.QA
@pytest.mark.QA_hub
def test_qa_hub():
    """
    TEST: test navigation into HUB

     1st step : enter in HUB with back key
        Action
        - enter HUB
        Checkup
        - check HUB is current UI

     2nd step : exit from hub using back key
        Action
        - press RCU key "back"
        Checkup
        - check hub is not current UI (live)

     3rd step : enter in HUB and wait for expiry (go back to fullscreen after timeout of 10s)
        Action
        - enter HUB
        - wait 15 seconds
        Checkup
        - check HUB is current UI
        - check fullscreen after 15s

     4th step : enter in HUB, then enter into and return from each sub items
        Action
        - enter HUB
        - navigate into and out from each sub menu
        Checkup
        - check sub items and return to HUB

     5th step : change language to DEUTSCH, enter in HUB, then enter into and return from each sub items
        Action
        - change language to DEUTSCH
        - enter HUB
        - navigate into and out from each sub menu
        Checkup
        - check sub items and return to HUB

    """
    logging.info("##### BEGIN test_qa_hub #####")

    ############
    # init test
    test_qa_hub = VeTestApi("test_qa_hub")
    test_qa_hub.begin(screen=test_qa_hub.screens.fullscreen)

    hhid = test_qa_hub.he_utils.get_default_credentials()[0]
    logging.info("current hhid is : " + hhid)

    ############
    ''' 1st step : enter in HUB with back key
        Action
        - enter HUB
        Checkup
        - check HUB is current UI
    '''
    # navigate to HUB
    logging.info("step 1 : navigate to hub with back key")
    status = test_qa_hub.screens.main_hub.navigate()
    
    errorMessage = "HUB:ACCESS/EXIT : Navigation to Hub failed, current screen = " + str(display_pretty_current_screen(test_qa_hub))
    test_qa_hub.log_assert(status, errorMessage)

    ############
    ''' 2nd step : exit from hub using back key
        Action
        - press RCU key "back"
        Checkup
        - check hub is not current UI (live)
    '''
    # back to previous screen using back key
    logging.info("step 2 : exit from hub with back key")
    test_qa_hub.go_to_previous_screen(CONSTANTS.SMALL_WAIT)

    # check fullscreen is displayed
    status = test_qa_hub.wait_for_screen(CONSTANTS.GENERIC_WAIT, "fullscreen")
    errorMessage = "HUB:ACCESS/EXIT : Navigation from Hub to fullscreen with back key failed, current screen = " + str(display_pretty_current_screen(test_qa_hub))
    test_qa_hub.log_assert(status, errorMessage)

    ############
    ''' 3rd step : enter in HUB and wait for expiry (go back to fullscreen after timeout of 10s)
        Action
        - enter HUB
        - wait 15 seconds
        Checkup
        - check HUB is current UI
        - check fullscreen after 15s
    '''
    # navigate to HUB again
    logging.info("step 3 : navigate to hub with back again and wait for expiry")
    status = test_qa_hub.screens.main_hub.navigate()
    errorMessage = "HUB:ACCESS/EXIT : Navigation to Hub failed, current screen = " + str(display_pretty_current_screen(test_qa_hub))
    test_qa_hub.log_assert(status, errorMessage)

    logging.info("step 3 : waiting_for_fullscreen ...")
    # wait for fullscreen after 15s (CONSTANTS.SCREEN_TIMEOUT)
    status = test_qa_hub.wait_for_screen(CONSTANTS.SCREEN_TIMEOUT, "fullscreen")
    errorMessage = "HUB:ACCESS/EXIT : Navigation to fullscreen from HUB after HUB expiry failed, current screen = " + str(display_pretty_current_screen(test_qa_hub))
    test_qa_hub.log_assert(status, errorMessage)

    ############
    ''' 4th step : enter in HUB, then enter into and return from each sub items
        Action
        - enter HUB
        - navigate into and out from each sub menu
        Checkup
        - check sub items and return to HUB
    '''
    # navigate to HUB again
    logging.info("step 4 : navigate to hub and each sub items")
    status = test_qa_hub.screens.main_hub.navigate()
    
    elements = test_qa_hub.milestones.getElements()
    logging.info("qa_hub: milestones= %s"%(elements))
    cur_scr =  test_qa_hub.milestones.get_current_screen(elements)
    errorMessage = "HUB:ACCESS/EXIT : Navigation to Hub failed, current screen = " + str(cur_scr)
    test_qa_hub.log_assert(status, errorMessage)
    logging.info("on screen %s"%(cur_scr))
    
    # navigate into hub to check all items
    checkHubItems(test_qa_hub, CONSTANTS.HUB_ITEMS_NAME_ENG)

    logging.info("step 4 : back to fullscreen")
    test_qa_hub.screens.fullscreen.navigate()



    ############
    ''' 5th step : change language to DEUTSCH, enter in HUB, then enter into and return from each sub items
        Action
        - change language to DEUTSCH
        - enter HUB
        - navigate into and out from each sub menu
        Checkup
        - check sub items and return to HUB
    '''

    # navigate to HUB again
    logging.info("step 5 : navigate to hub to change language")
    test_qa_hub.wait(CONSTANTS.GENERIC_WAIT)
    status = test_qa_hub.screens.main_hub.navigate()
    errorMessage = "HUB:ACCESS/EXIT : Navigation to Hub failed, current screen = " + str(
        display_pretty_current_screen(test_qa_hub))
    test_qa_hub.log_assert(status, errorMessage)

    # switch in German
    status = test_qa_hub.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES")
    test_qa_hub.wait(CONSTANTS.GENERIC_WAIT)
    errorMessage = "HUB:NAVIGATION : Navigation to Preferences sub-menu failed, current screen = " + str(
        display_pretty_current_screen(test_qa_hub))
    test_qa_hub.log_assert(status, errorMessage)

    status = test_qa_hub.screens.filter.modify_uilanguage(ui_language='DEUTSCH')
    errorMessage = "HUB:NAVIGATION: changing language to DEUTSCH failed, current screen = " + str(
        display_pretty_current_screen(test_qa_hub))
    test_qa_hub.log_assert(status, errorMessage)
    test_qa_hub.wait(CONSTANTS.GENERIC_WAIT)
    logging.info("step 6 : Switched in German")

    test_qa_hub.screens.fullscreen.navigate()

    # Update cookie
    test_qa_hub.he_utils.updateCookies()

    # navigate to HUB again
    logging.info("step 5 : navigate to hub and each sub items")
    status = test_qa_hub.screens.main_hub.navigate()
    errorMessage = "HUB:ACCESS/EXIT : Navigation to Hub failed, current screen = " + str(
                     display_pretty_current_screen(test_qa_hub))
    test_qa_hub.log_assert(status, errorMessage)

    # navigate to HUB again
    logging.info("step 5 : navigate to hub to check sub menu in DEUTSCH")
    status = test_qa_hub.screens.main_hub.navigate()
    errorMessage = "HUB:ACCESS/EXIT : Navigation to Hub failed, current screen = " + str(
        display_pretty_current_screen(test_qa_hub))
    test_qa_hub.log_assert(status, errorMessage)

    checkHubItems(test_qa_hub, CONSTANTS.HUB_ITEMS_NAME_DEU)

    logging.info("step 5 : back to fullscreen")
    test_qa_hub.screens.fullscreen.navigate()

    logging.info("##### End test_qa_hub #####")
    test_qa_hub.end()
