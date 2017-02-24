__author__ = 'ljusseau'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KSTB.error import E_STREAMING_NOT_ENTITLED_ERROR_CODE, E_STREAMING_NOT_ENTITLED_ERROR_MSG


TIME_BETWEEN_ZAP = 7
NB_LOOP_ZAP = 5
TIME_BETWEEN_INACTIVITY_STATUS = 30
NB_LOOP_INACTIVITY = 20
NO_ERROR_DISPLAYED=False
ERROR_DISPLAYED=True

def getListOfClearScrambledServices(services):
    nbClear = 0
    nbScrambled = 0
    listClear = {}
    listScrambled = {}
    offers = []

    for service in services:
        if(services[service]['drmType']=='none'):
            if nbClear<2:
                listClear[nbClear] = services[service]['logicalChannelNumber']
                nbClear=nbClear+1
        else:
            if nbScrambled<2:
                listScrambled[nbScrambled] = services[service]['logicalChannelNumber']
                nbScrambled=nbScrambled+1

        offers += services[service]['offers']
        if nbScrambled >= 2 and nbClear >=2:
            break
    return listClear, listScrambled, offers

def zapToChannel(test, list, id):
    print "Zapp to channel no " + str(list[id])
    #ve_test.screens.zaplist.tune_to_channel_by_sek(list[id],nbr_services, handle_pincode_screen=False,verify_streaming_started =False)
    test.screens.playback.dca(list[id])
    test.wait(TIME_BETWEEN_ZAP)
    playback_status = test.milestones.getPlaybackStatus()
    url = playback_status['sso']['sessionPlaybackUrl']
    print "    --> "+ url + " : " + playback_status['playbackState']
    return list[id]



def getCurrentUrl(test):
    return test.milestones.getPlaybackStatus()['sso']['sessionPlaybackUrl']

''' This usefull function check the current service playback status, and if expected the message error displayed
    Parameters :
      - previous_url : The url of the previous played service
      - expect_not_entitlement_error : True if a Not Entitlement Message Error should be displayed, False otherwise
    Return : The url of the new played service, empty string if a Not Entitlement Message Error is displayed
'''
def check_channel_and_not_entitlement(ve_test, previous_url, expect_not_entitlement_error):
    ve_test.check_notification_screen(shown=expect_not_entitlement_error,
                                      msg_text=E_STREAMING_NOT_ENTITLED_ERROR_MSG,
                                      msg_code=E_STREAMING_NOT_ENTITLED_ERROR_CODE)
    return ve_test.screens.playback.verify_playing_url(previous_url, 0, playing=(expect_not_entitlement_error == NO_ERROR_DISPLAYED) , compare="!=")



''' Unitary test entitlement error message :
      - 0. Zapp to a clear service
      - 1. Zapp to a DRM service with entitlement OK
           --> Expected :
                . The video is playing
                . No error message is displayed
      - 2. Zapp back to a clear channel. Remove offers and go back to the same DRM service
           --> Expected :
                . The video should not be playing.
                . A error message is displayed (ERR_013)
      - 3. Press Back, in order to go back to MainHub. Check the error message is no more displayed.
      - 4. Press Ok, in order to go back to fullscreen with the DRM not entitled service.
           --> Expected :
                . The video should not be playing.
                . A error message is displayed (ERR_013)
'''
@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_entitlement():
    test = VeTestApi("test_entitlement")
    test.begin(screen=test.screens.fullscreen)
  
    services = test.he_utils.get_abr_linear_services_from_cmdc()

    listClear, listScrambled, offers = getListOfClearScrambledServices(services)

    ''' Step 0. Zapp to a clear service'''
    zapToChannel(test, listClear, 0)
    '''Check the clear service is playing, and no notification error is displayed '''
    clear_url = check_channel_and_not_entitlement(test, "", NO_ERROR_DISPLAYED)

    ''' Step 1. Zapp to a DRM service with entitlement OK'''
    zapToChannel(test, listScrambled, 0)
    check_channel_and_not_entitlement(test,clear_url, NO_ERROR_DISPLAYED)

    ''' Step 2. Zapp back to the previous service (clear service), remove offers, and go back to the same drm service '''
    zapToChannel(test, listClear, 0)
    test.he_utils.setHouseHoldAuthorization(test.configuration["he"]["generated_household"], offers, remove=True)
    zapToChannel(test, listScrambled, 0)
    check_channel_and_not_entitlement(test, clear_url, ERROR_DISPLAYED)

    ''' Step 3. Press Back, in order to go back to MainHub.'''
    test.appium.key_event("KEYCODE_BACK")
    test.wait(TIME_BETWEEN_ZAP)

    ''' Step 4. Press BACK, in order to go back to fullscreen with the DRM not entitled service'''
    test.appium.key_event("KEYCODE_BACK")
    test.wait(TIME_BETWEEN_ZAP)
    check_channel_and_not_entitlement(test,clear_url, ERROR_DISPLAYED)

    test.end()

@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_entitlement_transition_clear_scrambled():
    test = VeTestApi("test_entitlement_transition_clear_scrambled")
    test.begin(screen=test.screens.fullscreen)

    services = test.he_utils.get_abr_linear_services_from_cmdc()

    #parse the list of services and make a list of two scrambled services and a list of two clear services
    #add only services with logical channel number of 1 digit (easier to zap : only one RC key to press)
    listClear, listScrambled, offers = getListOfClearScrambledServices(services)

    print "First zapping : Auth Scrambled"
    zapToChannel(test, listScrambled, 0)
    previous_url = check_channel_and_not_entitlement(test, "", NO_ERROR_DISPLAYED)

    print "Transition Auth Scrambled --> Unauth Clear"
    test.he_utils.setHouseHoldAuthorization(test.configuration["he"]["generated_household"], offers, remove=True)
    zapToChannel(test, listClear, 0)
    previous_url = check_channel_and_not_entitlement(test, previous_url, ERROR_DISPLAYED)

    print "Transition UnAuth Clear --> Auth Scrambled"
    test.he_utils.setHouseHoldAuthorization(test.configuration["he"]["generated_household"], offers)
    zapToChannel(test, listScrambled, 1)
    previous_url = check_channel_and_not_entitlement(test, previous_url, NO_ERROR_DISPLAYED)

    print "Transition Auth Scrambled  --> Auth Clear"
    zapToChannel(test, listClear, 0)
    previous_url = check_channel_and_not_entitlement(test, previous_url, NO_ERROR_DISPLAYED)

    print "Transition Auth Clear --> Unauth Scrambled"
    test.he_utils.setHouseHoldAuthorization(test.configuration["he"]["generated_household"], offers, remove=True)
    zapToChannel(test, listScrambled, 1)
    previous_url = check_channel_and_not_entitlement(test, previous_url, ERROR_DISPLAYED)

    print "Transition UnAuth scrambled --> Auth Scrambled"
    test.he_utils.setHouseHoldAuthorization(test.configuration["he"]["generated_household"], offers)
    zapToChannel(test, listScrambled, 0)
    previous_url = check_channel_and_not_entitlement(test, previous_url, NO_ERROR_DISPLAYED)

    print "Transition Auth Scrambled --> Unauth Scrambled"
    test.he_utils.setHouseHoldAuthorization(test.configuration["he"]["generated_household"], offers, remove=True)
    zapToChannel(test, listScrambled, 1)
    previous_url = check_channel_and_not_entitlement(test, previous_url, ERROR_DISPLAYED)

    print "Transition Unauth Scrambled  --> Auth Clear"
    test.he_utils.setHouseHoldAuthorization(test.configuration["he"]["generated_household"], offers)
    zapToChannel(test, listClear, 0)
    previous_url = check_channel_and_not_entitlement(test, previous_url, NO_ERROR_DISPLAYED)

    print "Transition Auth Clear --> Unauth Clear"
    test.he_utils.setHouseHoldAuthorization(test.configuration["he"]["generated_household"], offers, remove=True)
    zapToChannel(test, listClear, 1)
    previous_url = check_channel_and_not_entitlement(test, previous_url, ERROR_DISPLAYED)

    print "Transition UnAuth Clear --> Auth Scrambled"
    test.he_utils.setHouseHoldAuthorization(test.configuration["he"]["generated_household"], offers)
    zapToChannel(test, listScrambled, 0)
    previous_url = check_channel_and_not_entitlement(test, previous_url, NO_ERROR_DISPLAYED)

    print "Transition Auth Scrambled --> Unauth Clear"
    test.he_utils.setHouseHoldAuthorization(test.configuration["he"]["generated_household"], offers, remove=True)
    zapToChannel(test, listClear, 1)
    previous_url = check_channel_and_not_entitlement(test, previous_url, ERROR_DISPLAYED)

    print "AAA Transition Unauth Clear  --> Auth Clear"
    test.he_utils.setHouseHoldAuthorization(test.configuration["he"]["generated_household"], offers)
    zapToChannel(test, listClear, 0)
    previous_url = check_channel_and_not_entitlement(test, previous_url, NO_ERROR_DISPLAYED)

    print "Transition Auth Clear --> UnAuth Scrambled"
    test.he_utils.setHouseHoldAuthorization(test.configuration["he"]["generated_household"], offers, remove=True)
    zapToChannel(test, listScrambled, 0)
    previous_url = check_channel_and_not_entitlement(test, previous_url, ERROR_DISPLAYED)

    print "Transition UnAuth Scrambled --> UnAuth Scrambled"
    zapToChannel(test, listScrambled, 1)
    previous_url = check_channel_and_not_entitlement(test, previous_url, ERROR_DISPLAYED)

    print "Transition UnAuth Scrambled --> UnAuth Clear"
    zapToChannel(test, listClear, 1)
    previous_url = check_channel_and_not_entitlement(test, previous_url, ERROR_DISPLAYED)

    print "Transition UnAuth Clear --> UnAuth Scrambled"
    zapToChannel(test, listScrambled, 0)
    previous_url = check_channel_and_not_entitlement(test, previous_url, ERROR_DISPLAYED)

    print "Transition Unauth Scrambled  --> Auth Clear"
    test.he_utils.setHouseHoldAuthorization(test.configuration["he"]["generated_household"], offers)
    zapToChannel(test, listClear, 1)
    print "Transition Auth Clear  --> Auth Scrambled"
    zapToChannel(test, listScrambled, 0)

    print "Transition Auth Scrambled --> Unauth Clear"
    test.he_utils.setHouseHoldAuthorization(test.configuration["he"]["generated_household"], offers, remove=True)
    zapToChannel(test, listClear, 0)
    previous_url = check_channel_and_not_entitlement(test, previous_url, ERROR_DISPLAYED)

    print "Transition UnAuth Clear --> UnAuth Clear"
    zapToChannel(test, listClear, 1)
    previous_url = check_channel_and_not_entitlement(test, previous_url, ERROR_DISPLAYED)

    test.end()
