
import logging
import pytest
from vgw_test_utils.headend_bulk import simulate_recorded_events
from vgw_test_utils.headend_bulk import simulate_future_events
from vgw_test_utils.settings import Settings
from tests_framework.ve_tests.ve_test import VeTestApi

from tests_framework.he_utils.he_utils import HeUtils
from vgw_test_utils.headend_util import get_all_catalog

GENERIC_WAIT = 2


def check_recorded_events_order(ve_test, milestone):
    recordedItems = get_all_catalog()
    focused_asset_title = ve_test.milestones.get_value_by_key(milestone,"focused_asset")
    next_asset_title = ""
    Itemsfound = 0
    ItemsOnScreen = 0
    itemIndex = 0
    recordedItemsIndex = 0
    while focused_asset_title != next_asset_title:
        ItemsOnScreen = ItemsOnScreen + 1
        itemIndex = itemIndex + 1
        next_asset_title = focused_asset_title
        for rec in recordedItems:
            recordedItemsIndex = recordedItemsIndex + 1
            if rec['title'] == focused_asset_title:
                Itemsfound = Itemsfound + 1
                break
        ve_test.appium.key_event("KEYCODE_DPAD_RIGHT")
        focused_asset_title = ve_test.milestones.get_value_by_key(milestone,"focused_asset")
        assert itemIndex <= recordedItemsIndex

    assert Itemsfound <= ItemsOnScreen

def check_library_item(ve_test, menu_item, expected_actions):
    logging.info("Select %s menu item", menu_item)
    status = ve_test.screens.main_hub.move_to_menu_from_basepos(menu_title=menu_item, direction="horizontal", expected_pos=5, check_pos=False, focused_milestone="focused_asset")

    ve_test.log_assert(status, "finding menu item:" + menu_item + " failed")
    ve_test.wait(GENERIC_WAIT)
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(GENERIC_WAIT)

    logging.info("Check that we are in FullContent page")
    status = ve_test.screens.fullcontent.is_in_full_content()
    ve_test.log_assert(status, "is_in_full_content() failed")
    ve_test.wait(GENERIC_WAIT)

    logging.info("Check Action Menu in focused item")
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "to_actionmenu_from_library() failed")
    ve_test.wait(GENERIC_WAIT)

    logging.info("Check Action Menu items")
    # actions_in_actionmenu = test.get_actions_from_current_actionmenu("")
    elements = ve_test.milestones.getElements()
    titleItems = ve_test.milestones.get_value_by_key(elements, "titleItems")
    actions_in_actionmenu = titleItems[1:-1].split(", ")
    logging.info("actions_in_actionmenu:")
    logging.info(actions_in_actionmenu)
    for action in expected_actions:
        assert action in actions_in_actionmenu, "The requested action ({0}) does not appear in this action menu\nCurrent actions in this action menu are {1}".format(action, actions_in_actionmenu)

    logging.info("Back to Library page")
    status = ve_test.screens.fullcontent.navigate()
    ve_test.log_assert(status, "to_fullcontent_from_actionmenu() failed")
    ve_test.wait(GENERIC_WAIT)
    status = ve_test.screens.library.navigate()
    ve_test.log_assert(status, "to_library_from_fullcontent() failed")
    ve_test.wait(GENERIC_WAIT)

@pytest.mark.non_regression
@pytest.mark.FS_Library
def test_library_next_to_see():
    ve_test = VeTestApi("test_library_next_to_see")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    logging.info("Simulating 5 recorded events")
    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    simulate_recorded_events(5)

    logging.info("Navigate to LIBRARY from HUB")
    status = ve_test.screens.library.navigate()
    ve_test.log_assert(status, "Navigation from main hub to library has failed")
    ve_test.wait(GENERIC_WAIT)

    logging.info("Check focused item is NEXT TO SEE")
    milestone = ve_test.milestones.getElements()
    focused_item = ve_test.milestones.get_value_by_key(milestone,"focused_item")
    logging.info("focused_item : %s", focused_item)
    assert focused_item == "NEXT TO SEE"

    logging.info("Check that all recorded events in Library are exist and sorted according to PPS purchesing list")
    check_recorded_events_order(ve_test, milestone)

    logging.info("Check Action Menu in recorded item")
    logging.info("Navigate to ACTION MENU from LIBRARY")
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Navigation from library to action menu has failed")
    ve_test.wait(GENERIC_WAIT)

    logging.info("Check that PLAY item is in ACTION MENU list")
    milestone = ve_test.milestones.getElements()
    titleItems = ve_test.milestones.get_value_by_key(milestone,"titleItems")
    assert "PLAY" in titleItems
    # TBD: Check that recording playback is working

    logging.info("Navigate to LIBRARY from ACTION MENU")
    status = ve_test.screens.library.navigate()
    ve_test.log_assert(status, "Navigation from action menu to library has failed")
    ve_test.wait(GENERIC_WAIT)

    logging.info("Navigate back to HUB from LIBRARY")
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status, "Navigation from library to main_hub has failed")
    ve_test.wait(GENERIC_WAIT)
    
    ve_test.end()


@pytest.mark.non_regression
@pytest.mark.FS_Library
def test_library_manage_recordings():
    ve_test = VeTestApi("test_library_manage_recordings")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    logging.info("Simulating 5 recorded events")
    simulate_recorded_events(5)

    logging.info("Navigate to LIBRARY from HUB")
    status = ve_test.screens.library.navigate()
    ve_test.log_assert(status, "Navigation from main hub to library has failed")
    ve_test.wait(GENERIC_WAIT)

    logging.info("Navigate to MANAGE RECORDINGS menu item")
    status = ve_test.screens.filter.focus_item_in_filterscreen_ux("MANAGE RECORDINGS")
    ve_test.log_assert(status, "focus_item_in_filterscreen_ux() failed")
    ve_test.wait(GENERIC_WAIT)

    expected_actions = ["SUMMARY","PLAY","DELETE","PROTECT","WATCH LIST","RELATED","LIKE"]
    check_library_item(ve_test, "RECORDINGS", expected_actions)

    logging.info("Simulating 5 scheduled events")
    simulate_future_events(5, future_time=10)
    expected_actions = ["SUMMARY","CANCEL BOOKING","PROTECT","MODIFY RECORDING","WATCH LIST","RELATED","LIKE"]
    check_library_item(ve_test, "SCHEDULED RECORDINGS", expected_actions)

    logging.info("Simulating 2 failed events")
    simulate_recorded_events(2, state="Failed")
    expected_actions = ["SUMMARY","PROTECT","WATCH LIST","RELATED","LIKE"]
    check_library_item(ve_test, "FAILED RECORDINGS", expected_actions)

    logging.info("Navigate back to HUB from LIBRARY")
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status, "Navigation from library to main hub has failed")
    ve_test.wait(GENERIC_WAIT)

    ve_test.end()


@pytest.mark.non_regression
@pytest.mark.FS_Library
def test_library_movies_and_shows():
    ve_test = VeTestApi("test_library_movies_and_shows")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    logging.info("Simulating 5 recorded events")
    simulate_recorded_events(5)

    logging.info("Navigate to LIBRARY from HUB")
    status = ve_test.screens.library.navigate()
    ve_test.log_assert(status, "Navigation from main hub to library has failed")
    ve_test.wait(GENERIC_WAIT)

    logging.info("Navigate to MOVIES & SHOWS menu item")
    status = ve_test.screens.filter.focus_item_in_filterscreen_ux("MOVIES & SHOWS")
    ve_test.log_assert(status, "focus_item_in_filterscreen_ux() failed")
    ve_test.wait(GENERIC_WAIT)

    expected_actions = ["SUMMARY", "PLAY", "DELETE", "PROTECT", "WATCH LIST", "RELATED", "LIKE"]
    check_library_item(ve_test, "RECORDINGS", expected_actions)

    logging.info("Navigate back to HUB from LIBRARY")
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status, "Navigation from library to main hub has failed")
    ve_test.wait(GENERIC_WAIT)

    ve_test.end()


@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Library
@pytest.mark.F_Clock
@pytest.mark.LV_L3
def test_check_clock_in_library_filter():
    ve_test = VeTestApi("test_check_clock_in_library_filter")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    logging.info("Navigate to LIBRARY from HUB")
    status = ve_test.screens.library.navigate()
    ve_test.log_assert(status, "to_library_from_hub() failed")
    ve_test.wait(GENERIC_WAIT)

    clock_time = ve_test.get_clock_time()
    if not clock_time:
        ve_test.log_assert(False, "The Clock is not displayed in Library filter")
    else:
        logging.info("Clock is displayed: %s" % clock_time)

    # wait 1 min and check time is updated
    status = ve_test.check_clock_time_update(clock_time)
    ve_test.log_assert(status,
                    "Clock is not more displayed after 1 min. Current screen: %s" % ve_test.milestones.get_current_screen())

    ve_test.end()
    logging.info("##### End test_check_clock_in_library_filter #####")

@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Library
@pytest.mark.F_Clock
@pytest.mark.LV_L3
def test_check_clock_in_library_fullcontent_recordings():
    ve_test = VeTestApi("test_check_clock_in_library_fullcontent_recordings")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    logging.info("Navigate to LIBRARY from HUB")
    status = ve_test.screens.library.navigate()
    ve_test.log_assert(status, "Navigation from main hub to library has failed")
    ve_test.wait(GENERIC_WAIT)

    # Check Recordings and Rental (separate in CTAP)
    logging.info("Navigate to MOVIES & SHOWS menu item")
    status = ve_test.screens.filter.focus_item_in_filterscreen_ux("MOVIES & SHOWS")
    ve_test.log_assert(status, "Fail to access to MOVIES & SHOWS item")
    ve_test.wait(GENERIC_WAIT)

    # RECORDINGS
    status = ve_test.screens.main_hub.move_to_menu_from_basepos(menu_title='RECORDINGS', direction="horizontal", focused_milestone="focused_asset")
    ve_test.log_assert(status, "Fail to select RECORDINGS")
    ve_test.validate_focused_item()
    clock_time = ve_test.get_clock_time()
    if not clock_time:
        ve_test.log_assert(False, "The Clock is not displayed in RECORDINGS fullcontent")
    else:
        logging.info("Clock is displayed: %s" % clock_time)

    # wait 1 min and check time is updated
    status = ve_test.check_clock_time_update(clock_time)
    ve_test.log_assert(status,
                    "Clock is not more displayed after 1 min. Current screen: %s" % ve_test.milestones.get_current_screen())

    ve_test.end()
    logging.info("##### End test_check_clock_in_library_fullcontent_recordings #####")

@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Library
@pytest.mark.F_Clock
@pytest.mark.LV_L3
def test_check_clock_in_library_fullcontent_rentals():
    ve_test = VeTestApi("test_check_clock_in_library_fullcontent_rentals")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    logging.info("Navigate to LIBRARY from HUB")
    status = ve_test.screens.library.navigate()
    ve_test.log_assert(status, "Navigation from main hub to library has failed")
    ve_test.wait(GENERIC_WAIT)

    # Check Recordings and Rental (separate in CTAP)
    logging.info("Navigate to MOVIES & SHOWS menu item")
    status = ve_test.screens.filter.focus_item_in_filterscreen_ux("MOVIES & SHOWS")
    ve_test.log_assert(status, "Fail to access to MOVIES & SHOWS item")
    ve_test.wait(GENERIC_WAIT)

    # RECORDINGS
    status = ve_test.screens.main_hub.move_to_menu_from_basepos(menu_title='RENTALS', direction="horizontal",
                                            focused_milestone="focused_asset")
    ve_test.log_assert(status, "Fail to select RENTALS")
    ve_test.validate_focused_item()
    clock_time = ve_test.get_clock_time()
    if not clock_time:
        ve_test.log_assert(False, "The Clock is not displayed in RENTALS fullcontent")
    else:
        logging.info("Clock is displayed: %s" % clock_time)

    # wait 1 min and check time is updated
    status = ve_test.check_clock_time_update(clock_time)
    ve_test.log_assert(status,
                    "Clock is not more displayed after 1 min. Current screen: %s" % ve_test.milestones.get_current_screen())

    ve_test.end()
    logging.info("##### End test_check_clock_in_library_fullcontent #####")