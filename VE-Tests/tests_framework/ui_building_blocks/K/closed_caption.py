___author__ = 'mtlais'

from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.he_utils.he_utils import ServiceDeliveryType
import logging

# CC can be reported asynchronously after the playback has started
CC_MIN_PERIOD = 5

class ClosedCaption(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "ClosedCaption")

    def play_live_cc(self,ccfilter):
        id = self.test.he_utils.getContent("LINEAR", ccfilter, ServiceDeliveryType.ABR, 0)
        sek = self.test.he_utils.services[id]['serviceEquivalenceKey']

        zaplist = self.test.screens.zaplist
        zaplist.tune_to_channel_by_sek(sek, True)
        self.test.wait(CC_MIN_PERIOD)
