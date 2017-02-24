___author__ = 'zhamilto'

from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ve_tests.tests_conf import DeviceType

class Header(Screen):
    def __init__(self, test):
        Screen.__init__(self, test)

    def tap_item(self, label):
        if (self.test.device_type != DeviceType.TABLET) and (self.test.device_type != DeviceType.PHABLET):
            self.test.ui.tap_localized_id(label)
        else:
            self.test.ui.tap_localized_label(label)

    def item_exists(self, label):
        if (self.test.device_type != DeviceType.TABLET) and (self.test.device_type != DeviceType.PHABLET):
            return self.test.ui.localized_id_exists(label)
        else:
            return self.test.ui.localized_label_exists(label)
