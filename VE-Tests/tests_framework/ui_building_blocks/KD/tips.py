__author__ = 'tmelamed'
from tests_framework.ui_building_blocks.screen import Screen

class KDTips(Screen):

    def __init__(self, test):
        Screen.__init__(self, test, "tips")

    def dismiss(self, elements=None):
        self.test.log("Removing tips")
        self.test.ui.center_tap(elements)
