import json
import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
import logging
__author__ = 'ftoubas'

' Global constants '
GENERIC_WAIT = 2

def is_rent_action_displayed(ve_test):
    current_screen = ve_test.milestones.get_current_screen()
    logging.info("current_screen: "+ current_screen)
    elements = ve_test.milestones.getElements()
    items_list = ve_test.milestones.get_value_by_key(elements, "titleItems")
    logging.info(' titleItems: {}' .format(json.dumps(items_list, indent=2)))
    return "RENT" in items_list

def check_rent_action(test_title="test_ui_vod_actionMenu",is_displayed=True):
    """
     Check RENT action is present in the action menu
     when PURCHASE-TVOD service is enabled in the hh
    """
    ve_test = VeTestApi("test_ui_vod_actionMenu")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    he_utils = ve_test.he_utils
    credentials = he_utils.get_default_credentials()
    hh_id = credentials[0]
    logging.info("test_check_rent_action hhid " + hh_id)

    # Enable PURCHASE-TVOD service
    if is_displayed:
        if not ve_test.he_utils.isServiceEnabled(hh_id, "PURCHASE-TVOD"):
            ve_test.he_utils.enableService(hh_id, "PURCHASE-TVOD")

        ve_test.log_assert(ve_test.he_utils.isServiceEnabled(hh_id, "PURCHASE-TVOD"),
                            "PURCHASE-TVOD service should be enabled")
    else:
        if ve_test.he_utils.isServiceEnabled(hh_id, "PURCHASE-TVOD"):
            ve_test.he_utils.disableService(hh_id, "PURCHASE-TVOD")

        ve_test.log_assert(not ve_test.he_utils.isServiceEnabled(hh_id, "PURCHASE-TVOD"),
                            "PURCHASE-TVOD service should be enabled")


    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Should be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)

    #go in fullcontent
    ve_test.screens.playback.vod_manager.go_to_vod_asset("TVOD", True)

    #going into asset action menu
    ve_test.validate_focused_item(2)
    logging.info("In action menu ")
    ve_test.wait(3)

    status = ve_test.wait_for_screen(5, "action_menu")
		
    # check rent action is displayed
    ve_test.log_assert(True if is_rent_action_displayed(ve_test) == is_displayed else False ,
                        "RENT action is missing in actions list")

    ve_test.end()

@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L2
def test_check_rent_action_is_displayed():

    """
     Check RENT action is present in the action menu
     when PURCHASE-TVOD service is enabled in the hh
    """
    check_rent_action();

@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_check_rent_action_is_not_displayed():
    """
     Check RENT action is not present in the action menu
     when PURCHASE-TVOD service is not enabled in the HH
    """
    check_rent_action(is_displayed=False);
