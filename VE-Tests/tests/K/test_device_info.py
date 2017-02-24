
__author__ = 'nbriskin'

import pytest
import random
from tests_framework.ve_tests.ve_test import VeTestApi
from vgw_test_utils.IHmarks import IHmark


#@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF1878
@IHmark.CF4352
#@pytest.mark.level2
@pytest.mark.MF1878_K_CF4352_device_info
def test_device_info():
    ve_test = VeTestApi("test_device_info")
    ve_test.begin()


    ve_test.wait(1)
    ve_test.screens.settings.device_info(verify=True)


    ve_test.end()


