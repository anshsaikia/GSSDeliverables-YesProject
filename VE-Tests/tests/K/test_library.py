__author__ = 'gekatz'


import pytest
import time
import pprint
import logging

from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.K.library_filter import FilterType
from vgw_test_utils.headend_bulk import simulate_future_events, simulate_recorded_events
from vgw_test_utils.settings import Settings
from vgw_test_utils.headend_util import get_channel_list
from tests_framework.ve_tests.tests_conf import DeviceType
from vgw_test_utils.IHmarks import IHmark

# @IHmark.LV_L2
# @IHmark.O_iOS
@pytest.mark.MF2153_display_basic_library
def test_library_fullcontent_screen():
    test = VeTestApi("test_library_fullcontent_screen")
    library_screen = test.screens.library_filter
    test.begin(screen=library_screen)

    test.log_assert(library_screen.section_exists(FilterType.MANAGE_RECORDINGS), "'MANAGE RECORDINGS' section is not displayed!")
    test.log_assert(library_screen.section_exists(FilterType.NEXT_TO_SEE) is False, "'NEXT TO SEE RECORDINGS' should not be displayed!")
    test.log_assert(library_screen.section_exists(FilterType.MOVIES_AND_SHOWS) is False, "'MOVIES AND SHOWS' should not be displayed!")

    Settings['household_id'] = test.configuration["he"]["generated_household"]
    upmDeviceId = test.he_utils.getDeviceIdFromHHByManufacturer(Settings['household_id'], "Apple")
    Settings["device_id"] = upmDeviceId
    channel_list = [int(i['serviceEquivalenceKey']) for i in get_channel_list()]

    simulate_recorded_events(1, not_to_use_channels=channel_list[1:len(channel_list)])
 #   simulate_future_events(1, channels=channel_list[1:2], future_time=10)
    time.sleep(3)

    test.screens.tv_filter.navigate()
    library_screen.navigate()
    test.log_assert(library_screen.section_exists(FilterType.NEXT_TO_SEE) is True, "'NEXT TO SEE RECORDINGS' should be displayed!")
    test.log_assert(library_screen.section_exists(FilterType.MOVIES_AND_SHOWS) is True, "'MOVIES AND SHOWS' should be displayed!")
    test.log_assert(len(library_screen.get_events_by_section(FilterType.NEXT_TO_SEE)) == 1, "Unexpected number of 'NEXT TO SEE RECORDINGS'!")
    test.log_assert(len(library_screen.get_events_by_section(FilterType.MOVIES_AND_SHOWS)) == 1, "Unexpected number of 'MOVIES AND SHOWS RECORDINGS'!")
    #library_screen.navigate_to_manage_recording_filter(FilterType.SCHEDULED)

    test.log_assert(library_screen.get_see_all_of_section(FilterType.NEXT_TO_SEE) is None, "'SEE ALL' should not be displayed on 'NEXT TO SEE RECORDINGS'")
    test.log_assert(library_screen.get_see_all_of_section(FilterType.MOVIES_AND_SHOWS) is None, "'SEE ALL' should not be displayed on 'NEXT TO SEE RECORDINGS'")

    simulate_recorded_events(10, not_to_use_channels=channel_list[0:1]+channel_list[15:len(channel_list)])
#    simulate_future_events(1, channels=channel_list[0:1]+channel_list[2:15], future_time=20)
    time.sleep(3)

    test.screens.tv_filter.navigate()
    library_screen.navigate()

    number_of_highlights = 10

    test.log_assert(library_screen.section_exists(FilterType.NEXT_TO_SEE) is True, "'NEXT TO SEE RECORDINGS' should be displayed!")
    test.log_assert(library_screen.section_exists(FilterType.MOVIES_AND_SHOWS) is True, "'MOVIES AND SHOWS' should be displayed!")
    test.log_assert(len(library_screen.scroll_and_return_events(FilterType.NEXT_TO_SEE)) == number_of_highlights, "Unexpected number of 'NEXT TO SEE RECORDINGS'!" + str(len(library_screen.get_events_by_section(FilterType.NEXT_TO_SEE))))
    test.log_assert(len(library_screen.scroll_and_return_events(FilterType.MOVIES_AND_SHOWS)) == number_of_highlights, "Unexpected number of 'MOVIES AND SHOWS RECORDINGS'!" + str(len(library_screen.get_events_by_section(FilterType.MOVIES_AND_SHOWS))))

    test.log_assert(library_screen.get_see_all_of_section(FilterType.NEXT_TO_SEE) is not None, "'SEE ALL' should be displayed on 'NEXT TO SEE RECORDINGS'")
    test.log_assert(library_screen.get_see_all_of_section(FilterType.MOVIES_AND_SHOWS) is not None, "'SEE ALL' should be displayed on 'NEXT TO SEE RECORDINGS'")

    library_screen.navigate_to_see_all_filter(FilterType.NEXT_TO_SEE)
    test.screens.full_content_screen.verify_active()

    full_content_screen = test.screens.full_content_screen
    number_of_recordings = 0

    while number_of_recordings < (number_of_highlights + 1):
        recording = full_content_screen.get_first_event( asset_type="pvr")
        test.log_assert(recording, "'NEXT TO SEE RECORDINGS' has " + str(number_of_recordings + 1) + " items")
        full_content_screen.tap_event_by_title(recording["title_text"])
        test.screens.pvr_action_menu.verify_and_press_delete_button()
        test.log_assert(test.milestones.get_current_screen() == "full_content_screen", "Pressing YES on confirmation screen did not return to full_content_screen")
        number_of_recordings += 1

    test.log_assert(test.screens.full_content_screen.screen_empty(), "'NEXT TO SEE RECORDINGS' has more than " + str(number_of_recordings) + " items")

    elements = test.milestones.getElementsArrayByDic(element_key="title_text",dict_names= ["DIC_LIBRARY_RECORDINGS_NO_RESULTS"])
    test.log_assert(len(elements) == 1 , "Empty full content DIC_LIBRARY_RECORDINGS_NO_RESULTS wrong wording")

    test.screens.full_content_screen.go_to_previous_screen()
    test.log_assert(library_screen.section_exists(FilterType.MANAGE_RECORDINGS), "'MANAGE RECORDINGS' section is not displayed!")
    test.log_assert(library_screen.section_exists(FilterType.NEXT_TO_SEE) is False, "'NEXT TO SEE RECORDINGS' should not be displayed!")
    test.log_assert(library_screen.section_exists(FilterType.MOVIES_AND_SHOWS) is False, "'MOVIES AND SHOWS' should not be displayed!")

    test.end()

@pytest.mark.MF2153_display_basic_library
def test_library_recording_filters():
    from vgw_test_utils.headend_util import update_pps_status, get_all_catalog
    test = VeTestApi("test_library_recording_filters")
    library_screen = test.screens.library_filter
    test.begin(screen=library_screen)

    test.log_assert(library_screen.section_exists(FilterType.MANAGE_RECORDINGS), "'MANAGE RECORDINGS' section is not displayed!")
    test.log_assert(library_screen.section_exists(FilterType.NEXT_TO_SEE) is False, "'NEXT TO SEE RECORDINGS' should not be displayed!")
    test.log_assert(library_screen.section_exists(FilterType.MOVIES_AND_SHOWS) is False, "'MOVIES AND SHOWS' should not be displayed!")

    Settings['household_id'] = test.configuration["he"]["generated_household"]
    upmDeviceId = test.he_utils.getDeviceIdFromHHByManufacturer(Settings['household_id'], "Apple")
    Settings["device_id"] = upmDeviceId
    channel_list = [int(i['serviceEquivalenceKey']) for i in get_channel_list()]

    simulate_recorded_events(1, not_to_use_channels=channel_list[1:len(channel_list)], state="Capturing")
    time.sleep(5)
    test.screens.tv_filter.navigate()
    library_screen.navigate()
    test.log_assert(library_screen.section_exists(FilterType.NEXT_TO_SEE) is True, "'NEXT TO SEE RECORDINGS' should be displayed!")
    test.log_assert(library_screen.section_exists(FilterType.MOVIES_AND_SHOWS) is True, "'MOVIES AND SHOWS' should not be displayed!")
    test.log_assert(len(library_screen.get_events_by_section(FilterType.NEXT_TO_SEE)) == 1, "Unexpected number of 'NEXT TO SEE RECORDINGS'!")
    test.log_assert(len(library_screen.get_events_by_section(FilterType.MOVIES_AND_SHOWS)) == 1, "Unexpected number of 'NEXT TO SEE RECORDINGS'!")

    simulate_recorded_events(1, not_to_use_channels=channel_list[0:1]+channel_list[15:len(channel_list)])
    time.sleep(5)

    events = get_all_catalog()
    test.log_assert(len(events) == 2, "Wrong number of events")
    update_pps_status(events[0], 'Capturing')

    test.screens.tv_filter.navigate()
    library_screen.navigate()
    test.log_assert(library_screen.section_exists(FilterType.NEXT_TO_SEE) is True, "'NEXT TO SEE RECORDINGS' should be displayed!")
    test.log_assert(library_screen.section_exists(FilterType.MOVIES_AND_SHOWS) is True, "'MOVIES AND SHOWS' should be displayed!")
    test.log_assert(len(library_screen.get_events_by_section(FilterType.NEXT_TO_SEE)) == 2, "Unexpected number of 'NEXT TO SEE RECORDINGS'!")
    test.log_assert(len(library_screen.get_events_by_section(FilterType.MOVIES_AND_SHOWS)) == 2, "Unexpected number of 'MOVIES AND SHOWS RECORDINGS'!")

    test.end()
