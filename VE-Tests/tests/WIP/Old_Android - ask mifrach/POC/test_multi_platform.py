__author__ = 'bwarshaw'

from tests_framework.ve_tests.ve_test import VeTestApi


def test_multi_platform_test():
    ve_test = VeTestApi("test_multi_platform_test")

    ve_test.begin()

    zaplist = ve_test.screens.zaplist
    fullscreen = ve_test.screens.fullscreen

    zaplist.tune_to_channel_by_sek(103)

    zaplist.navigate(zaplist.actionTypes.up)

    fullscreen.navigate()

    zaplist.navigate(zaplist.actionTypes.down)

    fullscreen.navigate()

    ve_test.end()
