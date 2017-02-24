import time
import random

import pytest
from retrying import retry
from tests_framework.ui_building_blocks.screen import Screen, ScreenActions

from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition
from tests_framework.ui_building_blocks.KD.full_content_screen import SortType
from tests_framework.ui_building_blocks.KD.library import FilterType
from tests_framework.ve_tests.ve_test import VeTestApi
from vgw_test_utils.IHmarks import IHmark

def verify_library_items_by_capabilities(ve_test, pvr_supported=True):
     # go to libray
    library_screen = ve_test.screens.library
    library_screen.navigate()
     # check menu items
    elements= ve_test.milestones.getElementsArrayByDic(element_key="menu_item_title",dict_names= ["DIC_LIBRARY_MANAGE_RECORDINGS", "DIC_LIBRARY_NEXT_TO_SEE"])
    ve_test.log_assert(len(elements) == (2 if pvr_supported else 1) , "Wrong number of menu items in library")


def verify_confirmation_text_and_buttons(ve_test, confirmation_text):
    # first check that the confirmation screen appears
    ve_test.log_assert(ve_test.milestones.get_current_screen() == "notification", "no confirmation screen is displayed")

    ve_test.screens.notification.verify_notification_message_by_key(confirmation_text.value, type="general")

    # check the buttons
    ve_test.screens.notification.verify_notification_button_name_by_key("DIC_GENERIC_YES")
    ve_test.screens.notification.verify_notification_button_name_by_key("DIC_GENERIC_NO")


def verify_confirmation_no(ve_test, expected_screen):
    ve_test.screens.notification.tap_notification_button("DIC_GENERIC_NO")
    ve_test.wait(2)

    ve_test.log_assert(ve_test.milestones.get_current_screen() == expected_screen, "Pressing NO on confirmation screen did not return to %s" %expected_screen)


def verify_confirmation_yes(ve_test, expected_screen, num_events):
    ve_test.screens.notification.tap_notification_button("DIC_GENERIC_YES")
    ve_test.wait(3)

    ve_test.log_assert(ve_test.milestones.get_current_screen() == expected_screen, "Pressing YES on confirmation screen did not return to %s" %expected_screen)

    elements = ve_test.milestones.getElementsArray([("event_type", "EVENT_CONTENT_TYPE_STANDALONE", "==")])
    ve_test.log_assert(len(elements) == num_events, "Unexpected number of events in library: %d" %len(elements))





def verify_library_action(ve_test, recording_filter, action_name, confirmation_text, expected_no_screen, expected_yes_screen, num_events):
    ve_test.screens.library.navigate_to_manage_recording_filter(recording_filter)
    ve_test.screens.library.navigate_to_event(0)

    ve_test.screens.linear_action_menu.verify_and_press_button(action_name)
    verify_confirmation_text_and_buttons(ve_test, confirmation_text)
    verify_confirmation_no(ve_test, expected_no_screen)

    ve_test.screens.linear_action_menu.verify_and_press_button(action_name)
    verify_confirmation_text_and_buttons(ve_test, confirmation_text)
    verify_confirmation_yes(ve_test, expected_yes_screen, num_events)



@retry(stop_max_attempt_number=10, wait_fixed=500)
def set_pvr_device(ve_test):
    hhId = ve_test.he_utils.houseHolds[0]
    ve_test.he_utils.addHouseHoldDevices(hhId,
                                         [str(random.randint(100, 10000))],
                                         deviceFullType = "MANAGED",
                                         drmDeviceType = None,
                                         createPVR=True)

@pytest.mark.MF904
def test_library_no_pvr_capabilities():
    ve_test = VeTestApi("test_library_no_pvr_capabilities")
    @retry(stop_max_attempt_number=50, wait_fixed=1000)
    def wait_for_he_utils():
        assert ve_test.he_utils.heUtilsFinished

    wait_for_he_utils()

    from vgw_test_utils.headend_util import create_hh_with_x_android_devices
    from vgw_test_utils.settings import Settings

    Settings['household_id'] = ve_test.he_utils.default_credentials[0]
    Settings['device_id'] = ve_test.device_id
    create_hh_with_x_android_devices()

    ve_test.begin()

    verify_library_items_by_capabilities(ve_test, pvr_supported= False)

    ve_test.end()


@pytest.mark.MF904
def test_library_empty_library():
    ve_test = VeTestApi("test_library_empty_library")

    ve_test.begin()

    def verify_empty_filter(ve_test, filter_empty_dict_str):
        elements= ve_test.milestones.getElementsArrayByDic(element_key="title_text",dict_names= [filter_empty_dict_str])
        ve_test.log_assert(len(elements) == 1 , "Empty full content %s wrong wording" % filter_empty_dict_str)

    ve_test.screens.library.navigate_to_manage_recording_filter(FilterType.RECORDINGS)
    verify_empty_filter(ve_test,"DIC_LIBRARY_RECORDINGS_NO_RESULTS")
    ve_test.screens.library.navigate_to_manage_recording_filter(FilterType.SCHEDULED)
    verify_empty_filter(ve_test,"DIC_LIBRARY_BOOKINGS_NO_RESULTS")

    ve_test.end()

@pytest.mark.MF904
def test_library_manage_recording_fullcontent(num_recorded=10, num_scheduled=10):
    # vgw test ithils must be installed for running this test
    from vgw_test_utils.settings import Settings
    from vgw_test_utils.headend_bulk import simulate_future_events, simulate_recorded_events

    ve_test = VeTestApi("test_library_manage_recording_fullcontent")
    ve_test.begin()




    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    simulate_recorded_events(num_recorded)
    simulate_future_events(num_scheduled)
    time.sleep(5)

    ve_test.screens.library.navigate_to_manage_recording_filter(FilterType.SCHEDULED)
    ve_test.screens.full_content_screen.verify_full_content_and_sort( FilterType.SCHEDULED)

    ve_test.screens.library.navigate_to_manage_recording_filter(FilterType.RECORDINGS)
    ve_test.screens.full_content_screen.verify_full_content_and_sort(FilterType.RECORDINGS)

    ve_test.end()

@pytest.mark.MF904
@pytest.mark.US25544
def test_library_pagination():
    test_library_manage_recording_fullcontent(num_recorded=100, num_scheduled=100)


@pytest.mark.MF904
def test_library_manage_recording_stop_delete_cancel():
    # vgw test ithils must be installed for running this test
    from vgw_test_utils.settings import Settings
    from vgw_test_utils.headend_bulk import simulate_future_events, simulate_recorded_events
    from vgw_test_utils.headend_util import update_pps_status, get_all_catalog


    ve_test = VeTestApi("tv:test_library_manage_recording_stop_delete_cancel")

    ve_test.begin()

    action_menu = ve_test.screens.linear_action_menu

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings['device_id'] = upmDeviceId

    simulate_recorded_events(1, state="Capturing")
    verify_library_action(ve_test, FilterType.RECORDINGS, action_menu.button_type.STOP, action_menu.button_confirmation_text.STOP, "action_menu", "action_menu", 1)

    events = get_all_catalog()
    ve_test.log_assert(len(events) == 1, "Wrong number of events")

    update_pps_status(events[0], 'Partial')
    verify_library_action(ve_test, FilterType.RECORDINGS, action_menu.button_type.DELETE, action_menu.button_confirmation_text.DELETE, "action_menu", "full_content_screen", 0)

    events = get_all_catalog()
    ve_test.log_assert(len(events) == 0, "Wrong number of events")

    simulate_future_events(1)
    verify_library_action(ve_test, FilterType.SCHEDULED, action_menu.button_type.CANCEL, action_menu.button_confirmation_text.CANCEL, "action_menu", "full_content_screen", 0)

    events = get_all_catalog()
    ve_test.log_assert(len(events) == 0, "Wrong number of events")

#@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF904
@pytest.mark.MF904
#@pytest.mark.level2
def test_library_recently_added():

    from vgw_test_utils.headend_util import get_all_vod_assets_from_uxapi
    from vgw_test_utils.settings import Settings

    ve_test = VeTestApi("library:test_library_recently_added")
    ve_test.begin()
    hhId = ve_test.he_utils.houseHolds[0]
    ve_test.he_utils.addHouseHoldDevices(hhId,
                                         [str(random.randint(100, 10000))],
                                         deviceFullType = "MANAGED",
                                         drmDeviceType = None,
                                         createPVR=True)

    # restart app in order to get the DVR option in HH settings
    ve_test.appium.restart_app()
    ve_test.wait(8)
    "Navigation"
    print str(ve_test.configuration)
    Settings["household_id"] = ve_test.configuration['he']['generated_household']
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, hhId)
    Settings["device_id"] = upmDeviceId
    assetslist = get_all_vod_assets_from_uxapi()
    ve_test.wait(4)
    '''check if screen is on action menu screen'''
    ve_test.screens.library.navigate()
    elements = ve_test.milestones.getElements()
    tap_event = ve_test.milestones.getElementsArray([("name", "event_view", "_)")],elements)
    ve_test.log_assert(tap_event and len(tap_event) > 0, "Can't find the result item on the screen")
    ve_test.appium.tap_element(tap_event[0])
    ve_test.wait(2)
    elements = ve_test.milestones.getElements()
    screen_name = ve_test.milestones.get_current_screen(elements)
    ve_test.log_assert((screen_name == "action_menu"), screen_name + "!=" + "action menu")

    ve_test.wait(2)
    main_hub = ve_test.screens.main_hub
    main_hub.verify_vod_metadata(False, "LIBRARY")
    main_hub.open_vod_action_menu_by_position(EventViewPosition.left_event, "LIBRARY")

    elements = ve_test.milestones.getElements()
    screen_name = ve_test.milestones.get_current_screen(elements)
    ve_test.log_assert((screen_name == "action_menu"), screen_name + "!=" + "action menu")
    ve_test.end()

