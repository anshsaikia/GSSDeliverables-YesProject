__author__ = 'bwarshaw'

from requests import get
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition

import pytest
FIRST_LAUNCH_TIMEOUT = 15

@pytest.mark.MF1164_Boot_flow
@pytest.mark.MF1173_Boot_flow
@pytest.mark.commit
def test_create_destroy_play_session_linear():
    ve_test = VeTestApi("test_create_destroy_play_session")
    ve_test.begin()

    sm_streaming_session_url = ve_test.configuration["he"]["smStreamingSession"]
    ve_test.screens.main_hub.tune_to_linear_channel_by_position(EventViewPosition.right_event)
    ve_test.wait(10)
    "Verify with SM that the sessionId created successfully"
    sm_session_id = ve_test.milestones.getPlaybackStatus("sso","sessionId")
    sm_status = get(sm_streaming_session_url + "/" + sm_session_id)
    ve_test.log_assert(sm_status.status_code == 200, "Failed to get sessionId %s of tuned channel from session manger" % sm_session_id)

    ve_test.screens.main_hub.tune_to_linear_channel_by_position(EventViewPosition.right_event)
    ve_test.wait(10)
    "Verify that the sessionId of the previous channel is closed"
    sm_status = get(sm_streaming_session_url + "/" + sm_session_id)
    ve_test.log_assert(sm_status.status_code == 404, "sessionId %s was not closed after channel change" % sm_session_id)

    "Verify that the sessionId of the current playing channel is removed after restart"
    sm_session_id = ve_test.milestones.getPlaybackStatus()["sso"]["sessionId"]
    ve_test.appium.restart_app()
    ve_test.screens.main_hub.verify_active(timeout=FIRST_LAUNCH_TIMEOUT)
    sm_status = get(sm_streaming_session_url + "/" + sm_session_id)
    ve_test.log_assert(sm_status.status_code == 404, "sessionId %s was not closed after restart, sm status: %s" % (sm_session_id,sm_status.status_code))

    ve_test.end()
