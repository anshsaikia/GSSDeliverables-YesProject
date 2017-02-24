from tests_framework.ve_tests.assert_mgr import AssertMgr
from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
import pytest
import logging


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.dummy
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_search
@pytest.mark.QA_search_access
def test_search_from_main_hub():
    '''
    Check that the User can reach 'Search Home' from the Main Hub screen
    '''
    test = VeTestApi("test_search_from_main_hub")
    assertmgr = AssertMgr(test)
    test.begin(screen=test.screens.fullscreen)
    # Access to hub
    status = test.screens.main_hub.navigate()
    assertmgr.addCheckPoint("test_search_from_main_hub", 1, status,
                            "Fail to navigate to Hub. Current screen: %s" % test.milestones.get_current_screen())

    # Access to Search from the Hub
    status = test.screens.search.navigate()
    assertmgr.addCheckPoint("test_search_from_main_hub", 2, status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)
    # Check that default focus is on 'A'
    milestone = test.milestones.getElements()
    selected_char = test.milestones.get_value_by_key(milestone, 'selected_char')
    assertmgr.addCheckPoint("test_search_from_main_hub", 3, selected_char == 'A',
                            "Default focus is NOT on first letter of alphabetical characters but: %s" % selected_char)
    # Come-back to Main-hub
    status = test.screens.main_hub.navigate()
    assertmgr.addCheckPoint("test_search_from_main_hub", 4, status,
                            "Fail to go to Main Hub from Search. Current screen: %s" % test.milestones.get_current_screen())

    assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_search_from_main_hub #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.LV_L2
def test_search_back_from_main_hub():
    '''
    Check that the User can reach 'Search Home' from the Main Hub screen
    '''
    test = VeTestApi("test_search_from_main_hub")
    assertmgr = AssertMgr(test)
    test.begin(screen=test.screens.fullscreen)
    # access to main_hub
    status = test.screens.main_hub.navigate()
    assertmgr.addCheckPoint("test_search_back_from_Main_hub", 1, status,
                            "Fail to navigate to Hub. Current screen: %s" % test.milestones.get_current_screen())
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    assertmgr.addCheckPoint("test_search_from_main_hub", 2, status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Come-back to Main-hub
    status = test.screens.main_hub.navigate()
    assertmgr.addCheckPoint("test_search_from_main_hub", 3, status,
                            "Fail to go to Main Hub from Search. Current screen: %s" % test.milestones.get_current_screen())

    # check that selected item is still Search
    milestone = test.milestones.getElements()
    focused_item = test.milestones.get_value_by_key(milestone, 'focused_item')
    search_title = test.he_utils.get_hub_menuitem_title_by_item_id("SEARCH")
    assertmgr.addCheckPoint("test_search_from_main_hub", 4, focused_item == search_title,
                            "Focus is NOT on %s but: %s" % (search_title, focused_item))

    assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_search_from_main_hub #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_search
@pytest.mark.QA_search_access
def test_search_from_store():
    '''
    Check that the User can reach 'Search Home' from the Store
    '''
    test = VeTestApi("test_search_from_store")
    assertmgr = AssertMgr(test)
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)

    #Acces to the main hub
    status = test.screens.main_hub.navigate()
    assertmgr.addCheckPoint("test_search_from_store", 1, status,
                            "Fail to navigate to Hub. Current screen: %s" % test.milestones.get_current_screen())

    # Access to Search from Store
    status = test.screens.main_hub.navigate_to_store()
    assertmgr.addCheckPoint("test_search_from_store", 2, status, "Fail to go to Store. Current screen: %s" % test.milestones.get_current_screen())
    status = test.screens.filter.select_item_in_filterscreen_ux('SEARCH')
    assertmgr.addCheckPoint("test_search_from_store", 3, status, "Fail to go to Search. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)
    # Check that default focus is on 'A'
    milestone = test.milestones.getElements()
    selected_char = test.milestones.get_value_by_key(milestone, 'selected_char')
    assertmgr.addCheckPoint("test_search_from_store", 4, selected_char == 'A',
                            "Default focus is NOT on first letter of alphabetical characters but: %s" % selected_char)

    # Come-back to Main-hub
    test.go_to_previous_screen()
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
    assertmgr.addCheckPoint("test_search_back_from_store", 5, status, "Fail to oome-back to STORE. Current screen: %s" % test.milestones.get_current_screen())
    status = test.screens.main_hub.navigate()
    assertmgr.addCheckPoint("test_search_back_from_store", 6, status, "Fail to oome-back to Hub. Current screen: %s" % test.milestones.get_current_screen())

    assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_search_from_store #####")

@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.LV_L2
def test_search_back_from_store():
    '''
    Check that the User can reach 'Search Home' from the Store
    '''
    test = VeTestApi(title="test_search_back_from_store")
    assertmgr = AssertMgr(test)
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)

    #Acces to the mainhub
    status = test.screens.main_hub.navigate()
    assertmgr.addCheckPoint("test_search_back_from_store", 1, status,
                            "Fail to  navigate to the main_hub. Current screen: %s" % test.milestones.get_current_screen())

    # Access to Search from Store
    status = test.screens.main_hub.navigate_to_store()
    assertmgr.addCheckPoint("test_search_back_from_store", 2, status, "Fail to go to Store. Current screen: %s" % test.milestones.get_current_screen())
    status = test.screens.filter.select_item_in_filterscreen_ux('SEARCH')
    assertmgr.addCheckPoint("test_search_back_from_store", 3, status, "Fail to go to Search. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)
    # Check that default focus is on 'A'
    milestone = test.milestones.getElements()
    selected_char = test.milestones.get_value_by_key(milestone, 'selected_char')
    assertmgr.addCheckPoint("test_search_back_from_store", 4, selected_char == 'A',
                            "Default focus is NOT on first letter of alphabetical characters but: %s" % selected_char)

    # Come-back to Main-hub
    test.go_to_previous_screen()
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
    assertmgr.addCheckPoint("test_search_from_store", 5, status,
                            "Fail to oome-back to STORE. Current screen: %s" % test.milestones.get_current_screen())
    # check that selected item is still Search
    milestone = test.milestones.getElements()
    focused_item = test.milestones.get_value_by_key(milestone, 'focused_item')
    search_title = 'SEARCH'
    assertmgr.addCheckPoint("test_search_from_main_hub", 6, focused_item == search_title,
                            "Focus is NOT on %s but: %s" % (search_title, focused_item))

    status = test.screens.main_hub.navigate()
    assertmgr.addCheckPoint("test_search_from_store", 7, status,
                            "Fail to navigate to Hub. Current screen: %s" % test.milestones.get_current_screen())
    # check that selected item is still Store
    milestone = test.milestones.getElements()
    focused_item = test.milestones.get_value_by_key(milestone, 'focused_item')
    store_title = test.he_utils.get_hub_menuitem_title_by_item_id("STORE")
    assertmgr.addCheckPoint("test_search_from_main_hub", 8, focused_item == store_title,
                            "Focus is NOT on %s but: %s" % (store_title, focused_item))

    assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_search_back_from_store #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.LV_L2
def test_search_from_tvfilter():
    '''
    Check that the User can reach 'Search Home' from the TVFilter
    '''
    test = VeTestApi("test_search_from_tvfilter")
    assertmgr = AssertMgr(test)
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Access to Main_hub
    status = test.screens.main_hub.navigate()
    assertmgr.addCheckPoint("test_search_from_tvfilter", 1, status,
                            "Fail to navigate to the hub. Current screen: %s" % test.milestones.get_current_screen())

    # Access to TV Filter
    status = test.screens.main_hub.to_tvfilter_from_hub()
    assertmgr.addCheckPoint("test_search_from_tvfilter", 2, status, "Fail to go to TV Filter. Current screen: %s" % test.milestones.get_current_screen())
    status = test.screens.filter.select_item_in_filterscreen_ux('SEARCH')
    assertmgr.addCheckPoint("test_search_from_tvfilter", 3, status, "Fail to go to Search. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)
    # Check that default focus is on 'A'
    milestone = test.milestones.getElements()
    selected_char = test.milestones.get_value_by_key(milestone, 'selected_char')
    assertmgr.addCheckPoint("test_search_from_tvfilter", 4, selected_char == 'A',
                            "Default focus is NOT on first letter of alphabetical characters but: %s" % selected_char)
    # Come-back to Main-hub
    test.go_to_previous_screen()
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
    assertmgr.addCheckPoint("test_search_from_tvfilter", 5, status, "Fail to come-back to STORE. Current screen: %s" % test.milestones.get_current_screen())
    status = test.screens.main_hub.navigate()
    assertmgr.addCheckPoint("test_search_from_tvfilter", 6, status, "Fail to come-back to Hub. Current screen: %s" % test.milestones.get_current_screen())

    assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_search_from_tvfilter #####")



@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.LV_L2
def test_search_back_from_tvfilter():
    '''
    Check that the User can reach 'Search Home' from the TVFilter
    '''
    test = VeTestApi("test_search_back_from_tvfilter")
    assertmgr = AssertMgr(test)
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)

    # ACccess to the hub
    status = test.screens.main_hub.navigate()
    assertmgr.addCheckPoint("test_search_back_from_tvfilter", 1, status,
                            "Fail to navigate to Hub. Current screen: %s" % test.milestones.get_current_screen())

    # Access to TV Filter
    status = test.screens.main_hub.to_tvfilter_from_hub()
    assertmgr.addCheckPoint("test_search_back_from_tvfilter", 2, status, "Fail to go to TV Filter. Current screen: %s" % test.milestones.get_current_screen())
    status = test.screens.filter.select_item_in_filterscreen_ux('SEARCH')
    assertmgr.addCheckPoint("test_search_back_from_tvfilter", 3, status, "Fail to go to Search. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)
    # Check that default focus is on 'A'
    milestone = test.milestones.getElements()
    selected_char = test.milestones.get_value_by_key(milestone, 'selected_char')
    assertmgr.addCheckPoint("test_search_back_from_tvfilter", 4, selected_char == 'A',
                            "Default focus is NOT on first letter of alphabetical characters but: %s" % selected_char)
    # Come-back to Main-hub
    test.go_to_previous_screen()
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
    assertmgr.addCheckPoint("test_search_back_from_tvfilter", 5, status,
                            "Fail to come-back to STORE. Current screen: %s" % test.milestones.get_current_screen())
    # check that selected item is still Search
    milestone = test.milestones.getElements()
    focused_item = test.milestones.get_value_by_key(milestone, 'focused_item')
    search_title = 'SEARCH'
    assertmgr.addCheckPoint("test_search_back_from_tvfilter", 6, focused_item == search_title,
                            "Focus is NOT on %s but: %s" % (search_title, focused_item))

    status = test.screens.main_hub.navigate()
    assertmgr.addCheckPoint("test_search_back_from_tvfilter", 7, status,
                            "Fail to oome-back to Hub. Current screen: %s" % test.milestones.get_current_screen())
    # check that selected item is still Store
    milestone = test.milestones.getElements()
    focused_item = test.milestones.get_value_by_key(milestone, 'focused_item')
    filter_title = test.he_utils.get_hub_menuitem_title_by_item_id("TELEVISION")
    assertmgr.addCheckPoint("test_search_back_from_tvfilter", 8, focused_item == filter_title,
                            "Focus is NOT on %s but: %s" % (filter_title, focused_item))

    assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_search_back_from_tvfilter #####")

@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Search
@pytest.mark.F_Clock
@pytest.mark.LV_L3
def test_check_clock_in_search_filter():
    test = VeTestApi("test_check_clock_in_search_filter")
    test.begin(screen=test.screens.fullscreen)

    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    clock_time = test.get_clock_time()
    if not clock_time:
        test.log_assert(False, "The Clock is not displayed in Search fullcontent")
    else:
        logging.info("Clock is displayed: %s" % clock_time)

    # wait 1 min and check time is updated
    status = test.check_clock_time_update(clock_time)
    test.log_assert(status, "Clock is not more displayed after 1 min. Current screen: %s" % test.milestones.get_current_screen())

    # Select a letter
    first_letter = 'A'
    logging.info("Select letter %s" % first_letter)
    status = test.screens.search.search_select_char(first_letter, True)
    test.log_assert(status, "Fail to selected character: %s" % first_letter)

    clock_time = test.get_clock_time()
    if not clock_time:
        test.log_assert(False, "The Clock is not displayed in Search fullcontent")
    else:
        logging.info("Clock is displayed: %s" % clock_time)

    # wait 1 min and check time is updated
    status = test.check_clock_time_update(clock_time)
    test.log_assert(status, "Clock is not more displayed after 1 min. Current screen: %s" % test.milestones.get_current_screen())

    test.end()
    logging.info("##### End test_check_clock_in_search_filter #####")
