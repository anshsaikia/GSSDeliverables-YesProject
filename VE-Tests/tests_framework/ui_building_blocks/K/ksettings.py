___author__ = 'eacarq'

from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ve_tests.tests_conf import DeviceType
import logging


class kSettings(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "ksettings")

    def navigate(self):

        logging.info("Navigate to settings")
        if not self.test.ui.element_exists("settings"):
            if self.test.project != "KD":
                self.test.screens.tv_filter.navigate()
        self.test.ui.tap_element("settings")

    def select(self, setting, value):

        logging.info("setting = %s" %(setting))
        logging.info("value = %s" %(value))

        elements = self.test.milestones.getElements()
        for elem in elements:
            logging.info("elem = %s" %(elem))

        element_to_select = self.test.milestones.getElement([("title_text", value, "==")], elements)

        if element_to_select:
            logging.info("element_to_select = %s" %(element_to_select))
            self.test.appium.tap_element(element_to_select)
        else:
            logging.error("couldn't select %s in %s ..." % (value, setting))
            return False

        return True

    def navigate_and_get_disk_usage(self):
        # Navigate to settings screen
        self.navigate()
        self.test.screens.wait_for_screen(self, is_match=False)

        if self.test.device_type == DeviceType.PHABLET or self.test.device_type == DeviceType.SMARTPHONE:
            elements = self.test.milestones.getElements()
            element = self.test.milestones.getElement([("title_text", "PREFERENCES", "_)")], elements)
            self.test.appium.tap_element(element)

        # Get usage value
        elements = self.test.milestones.getElements()
        element = self.test.milestones.getElement([("id", "disk_space_management", "==")], elements)
        diskPercentage = element['value']

        # Go back
        element = self.test.milestones.getElement([("id", "back", "==")], elements)
        self.test.appium.tap_element(element)

        if self.test.device_type == DeviceType.PHABLET or self.test.device_type == DeviceType.SMARTPHONE:
            self.test.wait(2)
            elements = self.test.milestones.getElements()
            element = self.test.milestones.getElement([("id", "exit", "==")], elements)
            self.test.appium.tap_element(element)

        self.test.screens.wait_for_screen(self.test.screens.main_hub, is_match=False)

        return diskPercentage
