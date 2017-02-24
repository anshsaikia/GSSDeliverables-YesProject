__author__ = 'bwarshaw'

from time import sleep
from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ui_building_blocks.KD.main_hub import Showcases
import logging
from enum import Enum

'''Constants'''
OPEN_LIBRARY_TIMEOUT = 3

class FilterType(Enum):
    SCHEDULED = "DIC_LIBRARY_MANAGE_RECORDINGS_BOOKINGS"
    RECORDINGS = "DIC_LIBRARY_MANAGE_RECORDINGS_RECORDINGS"

class Library(Screen):
    filter_type = FilterType

    def __init__(self, test):
        Screen.__init__(self, test, "menu_library")

    def navigate(self):
        logging.info("Navigate to menu library")
        screen = self.test.milestones.get_current_screen()
        if screen == "menu_library":
            return
        if screen != "tv_filter":
            self.test.screens.main_hub.navigate()
        is_focused = self.test.screens.main_hub.focus_showcase(Showcases.LIBRARY)

        while (not is_focused):
            self.test.screens.main_hub.navigate()
            is_focused = self.screens.main_hub.focus_showcase(Showcases.LIBRARY)

        library_dic_value = self.test.milestones.get_dic_value_by_key("DIC_MAIN_HUB_LIBRARY","general")
        library_button = self.test.milestones.getElement([("regular_text", library_dic_value, "==")])
        self.test.log_assert(library_button, "Failed making LIBRARY panel selected")

        self.test.appium.tap_element(library_button)
        sleep(OPEN_LIBRARY_TIMEOUT)
        self.test.log_assert(self.test.milestones.get_current_screen() == "menu_library", "Failed navigating to Library")

    def navigate_to_manage_recording_filter(self, filterType):
        logging.info("Navigate to manage recording filter %s" %filterType)
        # go to libray
        self.test.screens.library.navigate()
        # go to manage recordings
        elements= self.test.milestones.getElementsArrayByDic(element_key="menu_item_title",dict_names= ["DIC_LIBRARY_MANAGE_RECORDINGS"])
        self.test.log_assert(elements, "Cannot find DIC_LIBRARY_MANAGE_RECORDINGS element")
        self.test.appium.tap_element(elements[0])
        elements= self.test.milestones.getElementsArrayByDic(element_key="title_text",dict_names= [filterType.value], extra_condition= ('name','event_text_view' , "=="))
        self.test.log_assert(elements, "Cannot find event by filterType %s" % filterType)
        # go to filter
        self.test.appium.tap_element(elements[0])
        self.test.screens.full_content_screen.verify_active()

    def navigate_to_event(self, num):
        logging.info("Navigate to event %d in library" %num)

        elements = self.test.milestones.getElementsArray([("event_type", "EVENT_CONTENT_TYPE_STANDALONE", "==")])
        self.test.log_assert((elements) > num, "Not enough events in the library")

        self.test.appium.tap_element(elements[num])
        self.test.wait(2)
