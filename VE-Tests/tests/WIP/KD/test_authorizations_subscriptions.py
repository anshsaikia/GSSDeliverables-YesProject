from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition
from tests_framework.ve_tests.ve_test import VeTestApi
import pytest

timeout = 10

def verify_notification_screen(ve_test, dic_error):
    screen_name = ve_test.milestones.get_current_screen()
    if(screen_name == 'notification'):
        screenElements = ve_test.milestones.getElements()
        element = ve_test.milestones.getElement([("name","NotificationView", "==")],screenElements)
        errorString = ve_test.milestones.get_dic_value_by_key(dic_error,"error")
        ve_test.log("the error appeared is" + element["text_0"])
        if errorString in element["text_0"]:
           return True
        else:
            return False
    return False

def verify_linear_playback(ve_test):
    playback_status = ve_test.milestones.getPlaybackStatus()
    state = playback_status["playbackState"]
    screen_name = ve_test.milestones.get_current_screen()
    if(screen_name == 'notification'):
        screenElements = ve_test.milestones.getElements()
        element = ve_test.milestones.getElement([("name","NotificationView", "==")],screenElements)
        ve_test.log("the error appeared is" + element["text_0"])
    if state == "PLAYING":
        return True
    else:
        return False

def verify_enable_service_list(ve_test, hh_id, providerId):
    services = ve_test.he_utils.getEnabledServicesUsingBoa(hh_id)
    if providerId in services.values():
        return True
    else:
        return False

@pytest.mark.MF1579_authorization_subscription
#@pytest.mark.level2 - the test always fail. 
def test_verify_authorization_suspension():
    ve_test = VeTestApi("auth:test_verify_authorization_suspension")
    ve_test.begin()
    hh_id = ve_test.configuration["he"]["generated_household"]
    error_cases = {}
    count =0
    abr_services = ve_test.he_utils.get_abr_linear_services_from_cmdc()
    offerId  = 0
    channelId = 0
    for value in abr_services.values():
        if len(value['offers']) > 0:
            offerId = value['offers'][0]
            channelId = value['serviceEquivalenceKey']
            break

    res = ve_test.he_utils.getOfferDetails(offerId)
    subscription = res['offers'][0]['externalKey']

    ve_test.log("Suspend KD-SERVICES and get the list of services again and check if KD-SERVICES is removed")
    ve_test.he_utils.suspendProviderServiceUsingBoa(hh_id, "KD-SERVICES")
    if verify_enable_service_list(ve_test, hh_id, "KD-SERVICES") is not False:
        error_cases[count] = "Disable provider case failed"
        count = count + 1

    ve_test.log("Resume KD-SERVICES and get the list of services again and check if KD-SERVICES is added")
    ve_test.he_utils.resumeProviderServicesUsingBoa(hh_id, "KD-SERVICES")
    if verify_enable_service_list(ve_test, hh_id, "KD-SERVICES") is  False:
        error_cases[count] = "Enable provider case failed"
        count = count + 1

    svod_offers, tvod_offers = ve_test.he_utils.getAllOffers()
    ve_test.log("removing s-v-o-d offers at head-end")
    ve_test.he_utils.setHouseHoldAuthorization(ve_test.he_utils.default_credentials[0], svod_offers,remove=True)
    ve_test.wait(5)
    ve_test.screens.notification.dismiss_notification()

    #No - yes case
    ve_test.log("Disable provider , Enable authorization case")
    r = ve_test.he_utils.addAuthorizationSubscriptionUsingBoa(hh_id,"SUBSCRIPTION",subscription,"KD-SERVICES")
    ve_test.log("Authorization added successfully , return code : " + str(r))
    r = ve_test.he_utils.suspendProviderServiceUsingBoa(hh_id, "KD-SERVICES")
    ve_test.log("provider suspended successfully , return code : " + str(r))
    ve_test.screens.zaplist.tune_to_channel_by_sek(channelId,verify_streaming_started=False)
    ve_test.wait(5)
    returnVal = verify_notification_screen(ve_test, "DIC_ERROR_PLAYBACK")
    if(returnVal is False):
        error_cases[count] = "Disable provider , Enable authorization case  failed"
        count = count + 1

    #No - No case
    ve_test.log("Disable provider , Disable authorization case")
    r = ve_test.he_utils.deleteAuthorizationSubscriptionUsingBoa(hh_id, subscription, "KD-SERVICES")
    ve_test.log("Authorization deleted successfully , return code : " + str(r))
    ve_test.wait(5)
    ve_test.screens.zaplist.tune_to_channel_by_sek(channelId, verify_streaming_started=False)
    ve_test.wait(5)
    returnVal = verify_notification_screen(ve_test, "DIC_ERROR_PLAYBACK")
    if(returnVal is False):
        error_cases[count] = "Disable provider , Disable authorization case failed"
        count = count + 1

    #yes - no case
    ve_test.log("Enable provider , Disable authorization case")
    r = ve_test.he_utils.resumeProviderServicesUsingBoa(hh_id, "KD-SERVICES")
    ve_test.log("provider added successfully , return code : " + str(r))
    ve_test.screens.zaplist.tune_to_channel_by_sek(channelId,verify_streaming_started=False)
    ve_test.wait(10)
    returnVal = verify_notification_screen(ve_test, "DIC_ERROR_PLAYBACK_CONTENT_NOT_ENTITLED")
    if(returnVal is False):
        error_cases[count] = "Enable provider , Disable authorization case failed"
        count = count + 1

    #yes - yes case
    ve_test.log("Enable provider , Enable authorization case")
    r = ve_test.he_utils.addAuthorizationSubscriptionUsingBoa(hh_id,"SUBSCRIPTION",subscription,"KD-SERVICES")
    ve_test.log("Authorization added successfully , return code : " + str(r))
    ve_test.screens.zaplist.tune_to_channel_by_sek(channelId,verify_streaming_started=False)
    ve_test.wait(7)
    returnVal = verify_linear_playback(ve_test)
    if(returnVal is False):
        error_cases[count] = "Enable provider , Enable authorization case failed"
        count = count + 1

    ve_test.wait(5)
    ve_test.log_assert(len(error_cases) == 0,"The following error cases Failed" + str(error_cases))
