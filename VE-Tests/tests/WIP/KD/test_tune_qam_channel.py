__author__ = 'isinitsi'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi


@pytest.mark.MF918_Channel_lineup_Unification
def test_tune_to_qam_channel():
    ve_test = VeTestApi("test_tune_to_qam_channel")

    ve_test.begin()
    channels = ve_test.he_utils.cable_only_services

    ve_test.log_assert(channels and len(channels) > 0,"No QAM channels found")

    ve_test.screens.zaplist.navigate()
    channelId = channels[ 0 ]['serviceEquivalenceKey']
    ve_test.screens.zaplist.tune_to_channel_by_sek(channelId, False)
    ve_test.wait(5)

    notification = ve_test.screens.notification
    notification.verify_notification_message_by_key("DIC_ERROR_PLAYBACK_CONTENT_NOT_PLAYABLE")
    playback_status = ve_test.milestones.getPlaybackStatus()
    state = playback_status["playbackState"]
    ve_test.log_assert(state != "PLAYING", "Playing 'QAM only' channel")
    ve_test.end()
