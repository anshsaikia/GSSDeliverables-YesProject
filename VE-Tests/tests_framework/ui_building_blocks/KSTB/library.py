__author__ = 'yboigenm'

from tests_framework.ui_building_blocks.screen import Screen
import logging
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS

        

class Library(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "filter")


    def navigate(self):
        logging.info("Navigate to library")
        screen = self.test.milestones.get_current_screen()
        if screen == self.screen_name:
            return True

        if screen == "full_content":
            logging.info("In fullcontent")
            self.test.appium.key_event("KEYCODE_BACK")
            self.test.wait(CONSTANTS.GENERIC_WAIT)
            status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
            if not status:
                logging.error("wait for library timed out")
                return False
            logging.info("In library")
            self.verify_active()
            return status

        if screen == "fullscreen":
            self.test.screens.main_hub.navigate()
            screen = "main_hub"

        if screen == "main_hub":
            status = self.test.screens.main_hub.focus_item_in_hub(item_title='LIBRARY')
            logging.info("Going into LIBRARY")
            self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            self.test.wait(CONSTANTS.GENERIC_WAIT)
            status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
            if not status:
                logging.error("to_library failed")
                return False
            self.verify_active()
            return True
        self.verify_active()
        assert True, "Navigation not implemented in this screen : " + screen



