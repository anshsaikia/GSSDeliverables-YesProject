import json

__author__ = 'ykantema'

import pytest
from tests_framework.he_utils.he_utils import VodContentType
from tests_framework.ve_tests.ve_test import VeTestApi


@pytest.mark.MF265
def test_vod_rental_expired():
    ve_test = VeTestApi("test_vod_rental_expired")

    ve_test.begin(preload="vod")
    
    asset = ve_test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.ENCRYPTED, VodContentType.LOW_RATED], {'policy':'false'})
    ve_test.screens.store_filter.play_vod_by_title(asset['title'])

    status = ve_test.milestones.getPlaybackStatus("playbackState")
    ve_test.log("status:" + status)
    ve_test.log_assert(status == "PLAYING", "expecting video playback")

    # VGDRM event as appears in src\apps\sf_k\libs\vgdrm.jar!\com\nds\vgdrm\api\generic\VGDrmStatusCodes.class
    # e.g  int VGDRM_STATUS_ENTITLEMENT_EXPIRED = -41942916
    ve_test.milestones.post_milestones_request("triggerVGDrmEvent", json.dumps([-41942916, 0]))

    status = ve_test.milestones.getPlaybackStatus("playbackState")
    ve_test.log("status:" + status)
    ve_test.log_assert(status == "STOPPED", "expecting video to be stopped")
    ve_test.log_assert(ve_test.milestones.get_current_screen() == "notification", "no notification is displayed")
    ve_test.log_assert(
            ve_test.screens.notification.get_notification_message() == ve_test.milestones.get_dic_value_by_key(
                    "DIC_ERROR_VOD_RENTAL_PERIOD_EXPIRED"), "wrong message")

    ve_test.end()
