__author__ = 'tchevall'

import logging
from tests_framework.ui_building_blocks.screen import Screen

class Notification(Screen):

    def __init__(self, test):
        Screen.__init__(self, test, "notification")

    def get_notification_message(self, elements=None):
        message = str(self.test.milestones.get_value_by_key(elements, "msg_error")) + " : " + str(self.test.milestones.get_value_by_key(elements, "msg_text"))
        return message

    def dismiss(self):
        return