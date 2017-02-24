__author__ = 'bwarshaw'

from tests_framework.ui_building_blocks.screen import Screen

class Boot(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "boot")
