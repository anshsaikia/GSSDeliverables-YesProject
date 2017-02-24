__author__ = 'gmaman'

from time import sleep
from tests_framework.ui_building_blocks.screen import Screen
import logging


class BookingRecording(Screen):
    def __init__(self, test):
        Screen.__init__(self, test)

    # Verify whether the given event is recordable
    def is_event_recordable(self, event_id):
        result = False
        payload = {"event_id": event_id}
        response = self.test.ctap_data_provider.send_request('ACTION_MENU', payload)

        if "contentFlags" in response and response["contentFlags"][0] == "recordableWithoutInteractive":
            result = True
        return result

    # Verify whether the given event is already booked
    def is_event_booked(self, event_id):
        result = False
        payload = {"event_id": event_id}
        response = self.test.ctap_data_provider.send_request('ACTION_MENU', payload)

        if "recordingState" in response:
            result = True
        return result

    def book_event(self, event_id, channel_id, screen=None):
        if screen == None:
            screen = self.test.screens.guide

        linear_action_menu = self.test.screens.linear_action_menu

        screen.navigate()
        screen.tap_event(event_id, channel_id)
        linear_action_menu.verify_active()
        linear_action_menu.verify_and_press_record_button()

    def verify_record_icon(self, event_element):
        record_icon_display = ("record_icon_displayed" in event_element) and (event_element["record_icon_displayed"] == True)
        self.test.log_assert(record_icon_display, "Record icon is not shown on event_id: %s" % event_element["event_id"])


