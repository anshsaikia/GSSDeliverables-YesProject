__author__ = 'bwarshaw'

from tests_framework.ui_building_blocks.screen import Screen

class Boot(Screen):
    def __init__(self, test):
        if test.platform == "Android":
            Screen.__init__(self, test, "logo")
        else:
            Screen.__init__(self, test, "boot")
