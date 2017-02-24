__author__ = 'pculembo'

import pytest
import logging
import requests
from tests_framework.ve_tests.ve_test import VeTestApi

	
'''
Check that the channel id at boot is the same as channel id when last rebooted 
get channel id of current channel
zap on another channel and get channel id (check that it is different)
reboot and get channel id and check it is the same
'''
@pytest.mark.FS_Reboot
@pytest.mark.sanity
@pytest.mark.LV_L3
def test_last_played_channel():

    ve_test = VeTestApi("test_last_played_channel")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    elements = ve_test.milestones.getElements()
    first_channel_lcn = ve_test.milestones.get_value_by_key(elements, "current_channel")
    logging.info("first_channel_lcn "+str(first_channel_lcn))
    ve_test.wait(10)
    # DCA to a valid channel
    dca_channel_lcn = int(first_channel_lcn) + 1
    logging.info("dca_channel_lcn "+str(dca_channel_lcn))
    ve_test.appium.key_event("KEYCODE_"+str(dca_channel_lcn))
    ve_test.wait(10)
    elements = ve_test.milestones.getElements()
    logging.info("channels second_channel_lcn elements "+str(elements))
    # Get channel id before rebooting
    second_channel_lcn = ve_test.milestones.get_value_by_key(elements, "current_channel")
    logging.info("second_channel_lcn "+str(second_channel_lcn))
    ve_test.wait(5)
    # Restart the app
    ve_test.appium.restart_app()
    ve_test.wait(15)
    # Press Back to go to fullscreen from Hub
    ve_test.appium.key_event("KEYCODE_BACK")
    ve_test.wait(5)
    logging.info("should be on full screen ")
    elements = ve_test.milestones.getElements()
    logging.info("channels reboot_channel_lcn elements "+str(elements))
    # Get channel id after rebooting
    reboot_channel_lcn = ve_test.milestones.get_value_by_key(elements, "current_channel")
    logging.info("reboot_channel_lcn "+str(reboot_channel_lcn))
    ve_test.wait(5)
    logging.info("channels "+str(second_channel_lcn)+ " "+str(reboot_channel_lcn))
    ve_test.log_assert(second_channel_lcn == reboot_channel_lcn, "expected channels to be the same, "+str(second_channel_lcn)+ " "+str(reboot_channel_lcn))

    ve_test.end()	
	



