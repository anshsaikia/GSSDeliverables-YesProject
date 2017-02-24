import pytest
import logging
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from tests_framework.ve_tests.ve_test import VeTestApi

def to_fullcontent_from_store(ve_test):
    category = "GENRES"
    sub_category = "DRAMA"
    logging.info("Access to a fullcontent from Store")

    status = ve_test.screens.filter.focus_item_in_filterscreen_ux(category)
    ve_test.log_assert(status, "Fail to go to %s" % category)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status = ve_test.screens.filter.select_sub_item_in_filterscreen_ux(sub_category)
    ve_test.log_assert(status, "Fail to go to %s" % sub_category)

    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # check we are in full_content
    status = ve_test.wait_for_screen(10, "full_content")
    ve_test.log_assert(status, "Wait FullContent time-out")
    logging.info("In full_content")

@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Store
@pytest.mark.dummy
@pytest.mark.LV_L2
def test_store_navigation_in_fullcontent():
    ve_test = VeTestApi("test_store_navigation_in_fullcontent")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    ve_test.screens.main_hub.navigate()
    status = ve_test.screens.main_hub.navigate_to_store()
    ve_test.log_assert(status, "Fail to go to Store")

    # go in fullcontent
    to_fullcontent_from_store(ve_test)

    # check assets part is focussed by default
    status = ve_test.screens.fullcontent.fullcontent_check_assets_are_focused()
    ve_test.log_assert(status, "Focus is not on the Assets part")
    # check first asset is focussed by default
    status = ve_test.screens.fullcontent.fullcontent_check_asset_n_is_focused(0)
    ve_test.log_assert(status, "Focus is not on the 1rst asset")

    # check assets are properly displayed
    status = ve_test.screens.fullcontent.fullcontent_check_assets_displayed_respect_model('2_by_3')
    ve_test.log_assert(status, "Assets displayed are not respecting the datamodel (2_by_3)")

    ve_test.end()
    logging.info("##### End test_store_navigation_in_fullcontent #####")


@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Store
@pytest.mark.LV_L2
def test_store_fullcontent_actionmenu():
    ve_test = VeTestApi("test_store_fullcontent_actionmenu")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    ve_test.screens.main_hub.navigate()
    status = ve_test.screens.main_hub.navigate_to_store()
    ve_test.log_assert(status, "Fail to go to Store")

    # go in fullcontent
    to_fullcontent_from_store(ve_test)

    # check assets part is focussed by default
    status = ve_test.screens.fullcontent.fullcontent_check_assets_are_focused()
    ve_test.log_assert(status, "Focus is not on the assets part")

    # going into asset action menu
    ve_test.validate_focused_item(2)
    status = ve_test.wait_for_screen(10, "action_menu")

    # logging.info(test.ve_test.milestones.getElements())
    ve_test.log_assert(status, "wait for action_menu screen timed out")
    logging.info("In action_menu")

    # check that fullcontent is displayed after exiting from ActionMenu
    ve_test.go_to_previous_screen()
    status = ve_test.wait_for_screen(10, "full_content")
    ve_test.log_assert(status, "wait for fullcontent screen timed out")
    logging.info("In full_content")

    ve_test.end()
    logging.info("##### End test_store_fullcontent_actionmenu #####")


@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Store
@pytest.mark.LV_L3
def test_store_focus_stays_on_asset_from_action_menu():
    ve_test = VeTestApi("test_store_fullcontent_actionmenu")
    ve_test.begin(screen=ve_test.screens.fullscreen)


    ve_test.screens.main_hub.navigate()
    status = ve_test.screens.main_hub.navigate_to_store()
    ve_test.log_assert(status, "Fail to go to Store")

    # go in fullcontent
    to_fullcontent_from_store(ve_test)

    # Select another asset than the first one
    ve_test.wait(5)
    ve_test.move_towards("right")
    status = ve_test.screens.fullcontent.fullcontent_check_asset_n_is_focused(1)
    ve_test.log_assert(status, "Could not focus the second asset")

    ve_test.validate_focused_item()
    status = ve_test.wait_for_screen(10, "action_menu")
    ve_test.log_assert(status, "wait for action_menu screen timed out")
    logging.info("In action_menu")

    ve_test.go_to_previous_screen()

    # check we are in full_content
    status = ve_test.wait_for_screen(10, "full_content")
    ve_test.log_assert(status, "Not in Fullcontent")
    logging.info("In full_content")
    status = ve_test.screens.fullcontent.fullcontent_check_asset_n_is_focused(1)
    ve_test.log_assert(status, "Wrong Back key management: Focus is no more on the second asset")

    ve_test.end()
    logging.info("##### End test_store_focus_stays_on_asset_from_action_menu #####")


@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Store
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_store_alphabetical_order():
    ve_test = VeTestApi("test_store_alphabetical_order")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    ve_test.screens.main_hub.navigate()
    status = ve_test.screens.main_hub.navigate_to_store()
    ve_test.log_assert(status, "Fail to go to Store")

    # go in fullcontent
    to_fullcontent_from_store(ve_test)

    # focus category part
    ve_test.move_towards("up")

    # select alphabetical order
    status = ve_test.screens.fullcontent.fullcontent_select_alphabetical_order()
    ve_test.log_assert(status, "Could not focus Alphabetical Order")
    logging.info("alphabetical order is selected")
    # focus assets part
    ve_test.move_towards("down")
    logging.info("Assets are focussed")
    # Check alphabetical order
    status = ve_test.screens.fullcontent.fullcontent_assets_are_in_alphabetical_order()
    ve_test.log_assert(status, "Assets are not in alphabetical order")
    logging.info("Assets are in alphabetical order")

    ve_test.end()
    logging.info("##### End test_store_alphabetical_order #####")


@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Store
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_store_alphabetical_fullcontent():
    ve_test = VeTestApi("test_store_alphabetical_fullcontent")

    ve_test.begin(screen=ve_test.screens.fullscreen)

    ve_test.screens.main_hub.navigate()
    status = ve_test.screens.main_hub.navigate_to_store()
    ve_test.log_assert(status, "Fail to go to Store")

    # go in fullcontent
    to_fullcontent_from_store(ve_test)

    # focus category part
    ve_test.move_towards("up")

    # select alphabetical order
    status = ve_test.screens.fullcontent.fullcontent_select_alphabetical_order()
    ve_test.log_assert(status, "Could not focus Alphabetical Order")
    logging.info("alphabetical order is selected")
    # focus assets
    ve_test.move_towards("down")
    logging.info("Assets are focussed")
    # check assets are properly displayed
    status = ve_test.screens.fullcontent.fullcontent_check_assets_displayed_respect_model('2_by_3')
    ve_test.log_assert(status, "Assets displayed are not respecting the datamodel (2_by_3)")

    ve_test.end()
    logging.info("##### End test_store_alphabetical_order #####")


@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Store
@pytest.mark.dummy
@pytest.mark.LV_L2
def test_check_store_first_level():
    ve_test = VeTestApi("test_check_store_first_level")

    ve_test.begin(screen=ve_test.screens.fullscreen)

    ve_test.screens.main_hub.navigate()
    # Retrieve the classification names from CMDC in order to compare it to the display ones
    cat_id = ve_test.he_utils.getCatalogueId(ve_test.he_utils.platform)
    # logging.info("cat_id: %s" % cat_id)
    root_class_id = ve_test.he_utils.get_rootClassificationID_from_catalogId(cat_id)
    class_with_content_list = ve_test.he_utils.get_classificationWithContent_from_catId_rootclassId(cat_id, root_class_id)
    # logging.info("\nclass_with_content_list: %s\n" % class_with_content_list)
    ve_test.log_assert((class_with_content_list is not None), "Class class_with_content_list is empty")

    cmdc_category_list = []
    for item in class_with_content_list:
        for key in item:
            if key == 'name':
                if 'hidden' in item:
                    if not item['hidden']:
                        cmdc_category_list.append((item['name'], item['orderNum']))
                else:
                    cmdc_category_list.append((item['name'], item['orderNum']))
    # Add SEARCH items
    cmdc_category_list.append(('SEARCH', 99))
    # logging.info("cmdc list: %s" % cmdc_category_list)

    # Access to the STORE first level and retrive the categories names
    status = ve_test.screens.main_hub.navigate_to_store()
    if not status:
        ve_test.log_assert(status, "Unable to access to STORE")
    category_list_display = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),'item_list')
    # logging.info("--> category_list_display:  %s" % category_list_display)

    # Compare the Categories
    if len(category_list_display) != len(cmdc_category_list):
        ve_test.log_assert(" The number of category is not correct:  cmdc: %s   display: %s" % (cmdc_category_list, category_list_display))
    else:
        logging.info("Nb categories is the same")
        sorted(cmdc_category_list, key=lambda colon: colon[1])
        # logging.info("cmdc_category_list: %s" % cmdc_category_list)
        cmdc_category_name_list = []
        for i in cmdc_category_list:
            # logging.info("i:  %s" % str(i))
            cmdc_category_name_list.append(i[0])
            # logging.info("cmdc_category_name_list:  %s" % cmdc_category_name_list)

        # logging.info("cmdc_category_name_list %s" % cmdc_category_name_list)

        if category_list_display != cmdc_category_name_list:
            ve_test.log_assert("Store Category List displayed is not the correct one. cmdc: %s  display: %s" % (cmdc_category_name_list, category_list_display))
        else:
            logging.info("1rst level Store Category List is the same: %s" % category_list_display)
    ve_test.wait(CONSTANTS.SMALL_WAIT)
    ve_test.end()
    logging.info("##### End test_check_Store_first_level #####")


@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Store
@pytest.mark.F_Clock
@pytest.mark.LV_L3
def test_check_clock_in_store_filter():
    ve_test = VeTestApi("test_check_clock_in_store_filter")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    ve_test.screens.main_hub.navigate()
    status = ve_test.screens.main_hub.navigate_to_store()
    ve_test.log_assert(status, "Fail to go to Store")
    clock_time = ve_test.get_clock_time()
    if not clock_time:
        ve_test.log_assert(False, "The Clock is not displayed in Store filter")
    else:
        logging.info("Clock is displayed: %s" % clock_time)

    # wait 1 min and check time is updated
    status = ve_test.check_clock_time_update(clock_time)
    ve_test.log_assert(status, "Clock is not more displayed after 1 min. Current screen: %s" % ve_test.milestones.get_current_screen())

    status, classification_id = ve_test.screens.filter.to_filter_leaf_from_filter(filter_path=("TV-MEDIATHEK", "ANIMAX"))
    ve_test.log_assert(status, "Failed to select TV-MEDIATHEK->ANIMAX")
    clock_time = ve_test.get_clock_time()
    if not clock_time:
        ve_test.log_assert(False, "The Clock is not displayed in Store filter")
    else:
        logging.info("Clock is displayed: %s" % clock_time)

    # wait 1 min and check time is updated
    status = ve_test.check_clock_time_update(clock_time)
    ve_test.log_assert(status, "Clock is not more displayed after 1 min. Current screen: %s" % ve_test.milestones.get_current_screen())

    ve_test.end()
    logging.info("##### End test_check_clock_in_store_filter #####")


@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Store
@pytest.mark.F_Clock
@pytest.mark.LV_L3
def test_check_clock_in_store_fullcontent():
    ve_test = VeTestApi("test_check_clock_in_store_filter")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    ve_test.screens.main_hub.navigate()
    status = ve_test.screens.main_hub.navigate_to_store()
    ve_test.log_assert(status, "Fail to go to Store")

    # go in fullcontent
    to_fullcontent_from_store(ve_test)

    clock_time = ve_test.get_clock_time()
    if not clock_time:
        ve_test.log_assert(False, "The Clock is not displayed in Store filter")
    else:
        logging.info("Clock is displayed: %s" % clock_time)

    # wait 1 min and check time is updated
    status = ve_test.check_clock_time_update(clock_time)
    ve_test.log_assert(status, "Clock is not more displayed after 1 min. Current screen: %s" % ve_test.milestones.get_current_screen())

    ve_test.end()
    logging.info("##### End test_check_clock_in_store_fullcontent #####")


@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Store
@pytest.mark.LV_L2
def test_store_editorial_assets():
    """
    Verify that the assets displayed in store menu come from editorial-content classification
    """
    test_name = "test_store_editorial_assets"
    test = VeTestApi(test_name)
    classification_id = ""
    cmdc_assets_list = []
    store_assets_list = []
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()

    status = test.screens.main_hub.focus_store_item_in_hub()
    test.log_assert(status,"Fail to go to Store")

    # Retrieve editorial contents from CMDC request:
    #Get CatalogId
    catId = test.he_utils.getCatalogueId(test.he_utils.platform)
    logging.info("CatalogueId : %s" % catId)
    test.log_assert((catId is not 0),"No Cat ID Found by CMDC")

    #Get Root ClassificationId from CatalogId
    rootclassId = test.he_utils.get_rootClassificationID_from_catalogId(catId)
    logging.info("rootclassId : %s" % rootclassId)
    test.log_assert((rootclassId!=0),"No rootclassID Found by CMDC")

    #Get Classification Type 41 in root classification from CatalogID and Root CatalogId
    #editorial classification type is 41
    classType41List = test.he_utils.get_classification_from_catId_rootclassId_typeId(catId,rootclassId,41)
    test.log_assert((classType41List!=[]), "No Classification type41 in catalog")

    #Get all assets ID & InstanceID of all 41 type classificationId from Classification List
    diccmdcassetsids,cmdc_assets_list = test.he_utils.get_assetIds_from_classif_list(catId, classType41List)
    test.log_assert((diccmdcassetsids!={}), "No assets typed type41 in catalog")
    
    # Retrieve assets displayed to Store Menu
    #TECHNICAL DEBT: currently we cannot get contentId and contentInstanceId from UI. So we are going to use title instead
    assetName = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_asset")
    
    while assetName not in store_assets_list:  # loop to count assets
        logging.info("assetName: %s" % assetName)
        store_assets_list.append(assetName)
        test.move_towards('right',1)        # next asset
        assetName = test.milestones.get_value_by_key(test.milestones.getElements(),  "focused_asset")   # next asset

    #Hub Store should contain editorial assets, but if not any, we also use toplist assets
    #So if cmdc assets list is bigger than the one displayed, it means that all assets displayed should belong to cmdc assets list
    #in the opposite, all items from cmdc assets list should be displayed on store
    if len(cmdc_assets_list) > len(store_assets_list):
        for asset in store_assets_list:
            status = asset in cmdc_assets_list
            test.log_assert(status,"%s does not belong to cmdc editorial assets list" % asset)
    else:
        for asset in cmdc_assets_list:
            status = asset in store_assets_list
            test.log_assert(status,"%s does not belong to Hub Store assets list" % asset)

    logging.info("##### End %s #####" % test_name)
    test.end()

