__author__ = 'zhamilto'

import logging
from tests_framework.ui_building_blocks.screen import Screen,ScreenActions
import logging

from enum import Enum

class FilterType(Enum):
    MANAGE_RECORDINGS = "DIC_LIBRARY_MANAGE_RECORDINGS"
    SCHEDULED = "DIC_LIBRARY_MANAGE_RECORDINGS_BOOKINGS"
    RECORDINGS = "DIC_LIBRARY_MANAGE_RECORDINGS_RECORDINGS"
    NEXT_TO_SEE = "DIC_FILTER_LIBRARY_NEXT_TO_SEE_RECORDINGS"
    MOVIES_AND_SHOWS = "DIC_FILTER_LIBRARY_MOVIES_AND_SHOWS_RECORDINGS"
    SERIES = "DIC_FILTER_LIBRARY_SERIES_RECORDINGS"


class LibraryFilter(Screen):
    filter_type = FilterType

    def __init__(self, test):
        Screen.__init__(self, test, "library_filter")

    def get_events_by_section(self, name):
        section_name = self.test.milestones.get_dic_value_by_key(name.value).upper()
        elements = self.test.milestones.getElements()
        events = self.test.ui.get_sorted_elements("event_view", 'x_pos', elements, "section", section_name)
        return events

    def wait_for_events_by_selection(self, name):
        events = None
        for wait in range(0, 30):
            events = self.get_events_by_section(name)
            if events:
                break
            self.test.wait(1)
        self.test.log_assert(events, "Cannot find events for section " + str(name))
        return events

    def section_exists(self, name):
        section_title = self.test.milestones.get_dic_value_by_key(name.value).upper()
        self.test.log("section_title:" + section_title)
        element = self.test.milestones.getElement([("title_text", section_title, "==")])
        return element is not None

    def get_see_all_of_section(self, name):
        see_all_title = self.test.milestones.get_dic_value_by_key("DIC_FILTER_SEE_ALL").upper()
        section_name = self.test.milestones.get_dic_value_by_key(name.value).upper()
        element = self.test.milestones.getElement([("title_text", see_all_title, "=="), ("title_section", section_name, "==")])
        return element

    def scroll_and_return_events (self, section):
        events = []
        new_event = None
        sections_events = self.wait_for_events_by_selection(section)
        last_event = None
        while last_event is None or last_event["event_id"] != new_event["event_id"]:
            last_event = sections_events[0]
            events.append(last_event)
            self.test.appium.swipe_element(last_event, last_event["width"] + 15, ScreenActions.LEFT, 2500)
            self.test.wait(2)
            sections_events = self.wait_for_events_by_selection(section)
            new_event = sections_events[0]

        if len(sections_events) > 1:
            for i in range(1, len(sections_events)):
                events.append(sections_events[i])
        return events


    def navigate(self):
        if not self.test.screens.header.item_exists("DIC_MAIN_HUB_LIBRARY"):
            self.test.screens.tv_filter.navigate()
        if not self.is_active():
            self.test.screens.header.tap_item("DIC_MAIN_HUB_LIBRARY")
        self.verify_active()

    def navigate_to_manage_recording_filter(self, filterType):
        self.navigate()
        logging.info("Navigate to manage recording filter %s" %filterType)
        # go to libray
        elements= self.test.milestones.getElementsArrayByDic(element_key="title_text",dict_names= [filterType.value])
        self.test.log_assert(elements, "Cannot find event by filterType %s" % filterType)
        # go to filter
        self.test.appium.tap_element(elements[0])
        self.test.screens.full_content_screen.verify_active()


    def navigate_to_event(self, num, event_type = "EVENT_CONTENT_TYPE_STANDALONE"):
        logging.info("Navigate to event %d in library" %num)

        elements = self.test.milestones.getElementsArray([("event_type", event_type, "==")])
        self.test.log_assert(len(elements) > num, "Not enough events in the library")

        self.test.appium.tap_element(elements[num])

    def navigate_to_series_Android(self):
        logging.info("Navigate to series filter")
        elements = self.test.milestones.getElements()
        series_element = self.test.milestones.getElementsArrayByDic(element_key="section",dict_names= ["DIC_FILTER_LIBRARY_SERIES_RECORDINGS"])
        self.test.log_assert(series_element, "Cannot find section DIC_FILTER_LIBRARY_SERIES_RECORDINGS element")

    def navigate_to_see_all_filter(self, filter_type):
        logging.info("Navigate to 'SEE ALL' of filter %s" %filter_type)
        # go to 'SEE ALL'
        see_all_title = self.test.milestones.get_dic_value_by_key("DIC_FILTER_SEE_ALL").upper()
        section_name = self.test.milestones.get_dic_value_by_key(filter_type.value).upper()
        element = self.test.milestones.getElement([("title_text", see_all_title, "=="), ("title_section", section_name, "==")])
        self.test.log_assert(element, "Cannot find event by filterType %s" % filter_type)
        # go to filter
        self.test.appium.tap_element(element)
        self.test.screens.full_content_screen.verify_active()

    def navigate_to_series(self):

        logging.info("Navigate to series filter")

        elements = self.test.milestones.getElementsArrayByDic(element_key="section",
                                                              dict_names=["DIC_FILTER_LIBRARY_SERIES_RECORDINGS"])

        self.test.log_assert(elements, "Cannot find DIC_FILTER_LIBRARY_SERIES_RECORDINGS element")
        self.test.appium.tap_element(elements[0])

