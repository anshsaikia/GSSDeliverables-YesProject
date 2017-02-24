from tests_framework.ve_tests.ve_test import VeTestApi

import pytest

TIMEOUT = 5

@pytest.mark.MF1118_Settings_Deep_Links
def test_settings_help():
    ve_test = VeTestApi("main_hub:test_settings_help")
    ve_test.begin()

    #Navigating to Settings and Choosing Help Menu
    ve_test.screens.settings.open_help()

    ve_test.wait(TIMEOUT)

    milestones = ve_test.milestones
    elements = milestones.getElements()

    #Verifying the presence of HELP Menu Options
    customer_self_care_dic_value = milestones.get_dic_value_by_key("DIC_HELP_SETTINGS_CUSTOMER_SELF_CARE")
    ve_test.log_assert(milestones.getElementContains(elements, customer_self_care_dic_value), \
                       "Customer Self-Care Menu is not present")

    help_tutorials_dic_value = milestones.get_dic_value_by_key("DIC_HELP_SETTINGS_TUTORIALS")
    ve_test.log_assert(milestones.getElementContains(elements, help_tutorials_dic_value), \
                       "Help & Tutorials Menu is not present")

    data_security_dic_value = milestones.get_dic_value_by_key("DIC_HELP_SETTINGS_DATA_SECURITY_INFO")
    ve_test.log_assert(milestones.getElementContains(elements, data_security_dic_value), \
                       "Data Security Information Menu is not present")

    ve_test.end()