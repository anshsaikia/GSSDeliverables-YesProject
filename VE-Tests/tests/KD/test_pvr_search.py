# -*- coding: utf-8 -*-
import pprint
import logging

import pytest

from tests_framework.ui_building_blocks.screen import ScreenActions


@pytest.mark.MF904
@pytest.mark.skip(reason="Can't run this test until we get the new CMDC fix for the erotic flag")
@pytest.mark.level2
def test_pvr_search(ve_test):

    test = ve_test

    from vgw_test_utils.settings import Settings
    from vgw_test_utils.headend_bulk import simulate_recorded_events

    Settings['household_id'] = test.configuration["he"]["generated_household"]
    Settings['device_id'] = test.device_id

    simulate_recorded_events(20)

    # go to library
    library_screen = test.screens.library
    library_screen.navigate()

    manage_recordings_title = test.milestones.get_dic_value_by_key(
        "DIC_LIBRARY_MANAGE_RECORDINGS", "general", True).upper()
    manage_recordings = test.milestones.getElement([("menu_item_title", manage_recordings_title, "==")])
    test.appium.tap_element(manage_recordings)

    recordings_title = test.milestones.get_dic_value_by_key(
        "DIC_LIBRARY_MANAGE_RECORDINGS_RECORDINGS", "general", True).upper()
    recordings = test.milestones.getElement([("title_text", recordings_title, "=="), ("name", "event_text_view", "==")])
    test.appium.tap_element(recordings)

    # find an event
    full_content_screen = test.screens.full_content_screen

    # verify sort by comparing first displayed asset to ctap
    full_content_screen.scroll_to_edge(direction=ScreenActions.DOWN)

    elements = test.milestones.getElements()
    events_titles = [e['title_text'] for e in elements if e.get("name", "") == "event_view"]

    # search for the event
    first_event = events_titles[0].split(":")[0][:3] + "*"
    logging.info("search for: %s", first_event)

    search = test.screens.search
    search.navigate()
    test.appium.type_keyboard(str(first_event))
    test.wait(2)
    search.tap_on_the_first_result()

    test.wait(2)
    elements = test.milestones.getElementsArray([('name', 'event_view', '==')])
    logging.info(pprint.pformat(elements))

    # check if pvr event or not, pvr event is first
    test.log_assert(elements[0]['event_source'] == "EVENT_SOURCE_TYPE_PVR", "First Event isn't PVR")

    # TODO: icon exist
    # TODO: click to start actionmenu
