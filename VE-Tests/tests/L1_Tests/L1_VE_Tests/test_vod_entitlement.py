__author__ = 'abarilan'
#__author__ = 'mibenami'

from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.he_utils.he_utils import VodContentType
import pytest

TIMEOUT = 4

"""Remove authorization and check if the 'play' option is absent"""

@pytest.mark.level2
def test_vod_entitlement():
    ve_test = VeTestApi("test_vod_entitlement")
    ve_test.begin()
    vod_action_menu = ve_test.screens.vod_action_menu
    store = ve_test.screens.store
    svod_offers, tvod_offers = ve_test.he_utils.getAllOffers()
    ve_test.say("removing SVOD offers at head-end by BOA")
    offer_keys = ve_test.he_utils.getOfferKey(svod_offers)
    for offer_key in offer_keys:
        ve_test.he_utils.deleteAuthorizationSubscriptionUsingBoa(ve_test.he_utils.default_credentials[0],offer_key, "KD-SERVICES")

    asset = ve_test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.ENCRYPTED, VodContentType.LOW_RATED, VodContentType.NON_EROTIC], {'policy':'false'})
    store.navigate_to_vod_asset_by_title(asset['title'])
    ve_test.screens.vod_action_menu.verify_play_menu(present=False)

    ve_test.say("restoring offers for user at head-end")
    for offer_key in offer_keys:
        ve_test.he_utils.addAuthorizationSubscriptionUsingBoa(ve_test.he_utils.default_credentials[0],"SUBSCRIPTION",offer_key, "KD-SERVICES")

    store.go_to_previous_screen()
    store.select_event_by_title(asset['title'])
    ve_test.screens.vod_action_menu.verify_play_menu(present=True)
    ve_test.say("removing SVOD offers")
    for offer_key in offer_keys:
        ve_test.he_utils.deleteAuthorizationSubscriptionUsingBoa(ve_test.he_utils.default_credentials[0],offer_key, "KD-SERVICES")
    ve_test.say("Trying to play the non-entitled asset. Expecting an error!")
    ve_test.screens.vod_action_menu.play_asset(verify_streaming=False)
    playback_status = ve_test.screens.playback.get_playback_status()
    ve_test.log_assert(playback_status["playbackState"] == "STOPPED", "content playing after authorization removed. playback_state= % s" % playback_status["playbackState"])

    notification = ve_test.screens.notification
    notification.verify_notification_message_by_key("DIC_ERROR_PLAYBACK_CONTENT_NOT_ENTITLED")
    notification.dismiss_notification()

    vod_action_menu.navigate()
    ve_test.say("verifying WATCH button not existing")
    vod_action_menu.verify_play_menu(present=False)
    ve_test.say("Restoring offers for user at head-end")
    for offer_key in offer_keys:
        ve_test.he_utils.addAuthorizationSubscriptionUsingBoa(ve_test.he_utils.default_credentials[0],"SUBSCRIPTION",offer_key, "KD-SERVICES")
    vod_action_menu.dismiss()
    vod_action_menu.navigate()
    vod_action_menu.play_asset(verify_streaming=True)
    ve_test.end()
