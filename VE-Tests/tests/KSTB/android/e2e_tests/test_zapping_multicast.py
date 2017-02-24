__author__ = 'mtlais'

import pytest
import requests
import json

from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KSTB.error import *

' Global constants '
MULTICAST_CHANNEL_ID = "100"
ABR_CHANNEL_ID = "7"
HEADERS = {'Source-Type':'STB', 'Source-ID':'123', 'Content-Type':'application/json','Data-Type':'array'}
USER_LOGIN = "a-mcast4"
HOUSEHOLD = "h-mcast4"
WAIT_TIME = 3


def launch_config_session():
    ve_test = VeTestApi("config_unitary_zapping_to_multicast_channel_ethernet")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    deviceId = ve_test.milestones.getDeviceDetails()['drm-device-id']
    ve_test.log_assert(deviceId != "null", "drm-device-id is null")

    url=ve_test.he_utils.upmUrl+ "households/"+HOUSEHOLD+"/devices/"+deviceId+"/streamingEnvironment" 
    r = requests.put(url, data = json.dumps(['MULTICAST']), headers=HEADERS)
    ve_test.log_assert((r.status_code == 200) or (r.status_code == 201), "[status code is %s] [test is %s]" % (str(r.status_code), r.text))

    ve_test.end()

def launch_test_session():
    test = VeTestApi("test_unitary_zapping_to_multicast_channel_ethernet")
    test.begin(screen=test.screens.fullscreen)
    
    test.screens.playback.dca(MULTICAST_CHANNEL_ID)
    test.wait(WAIT_TIME)
    test.screens.playaback.verify_streaming_playing(test, test.milestones)

    test.screens.playback.dca(ABR_CHANNEL_ID)
    test.wait(WAIT_TIME)
    test.screens.playback.verify_streaming_stopped(test, test.milestones)
    test.check_notification_screen('shown', msg_code=E_STREAMING_CHANNEL_NOTPLAYABLE_ERROR_CODE, msg_text=E_STREAMING_CHANNEL_NOTPLAYABLE_ERROR_MSG)
 
    test.end()


@pytest.mark.FS_Live
@pytest.mark.non_regression
@pytest.mark.F_Multicast
@pytest.mark.sanity
@pytest.mark.LV_L3
def test_unitary_zapping_to_multicast_channel_ethernet():
    # this test launches two ve_test sessions
    
    # the first one is to configure the UPM with multicast configuration,
    # this configuration is not active in the same session, thus we need to create another ve_test session to restart the application
    launch_config_session()

    # The second session is to effectively launch the zapping test
    launch_test_session()

