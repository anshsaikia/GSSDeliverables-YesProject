import pytest
import time
import random
import logging
import copy
import requests
import json
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KSTB.error import *

WAIT_TIME = 5
WAIT_TIME_LONG = 20
MAX_CONTENT = 2


setupResponseTemplate ={
    'streamingSession':
    {
        'smSessionId' : 'TEMPLATE',
        'contentType' : 'TEMPLATE',
        'contentIdType' : 'TEMPLATE',
        'contentId' : 'TEMPLATE',
        'activity' : 'TEMPLATE',
        'playbackURL' : 'TEMPLATE',
        'keepAliveRate' : 'TEMPLATE',
        'drmType' : 'TEMPLATE',
        'catalogId' : 'TEMPLATE'
    }
}

defaultSetupParamsVod = {
    'deviceId':'2222',
    'contentType':'VOD',
    'contentIdType':'CONTENT_ID',
    'contentId':'programid://536870914~programid://1073741845',
    'catalogId' : '2000',
    'householdId' : 'HH'
}

defaultSetupParamsLinear = {
    'deviceId':'2222',
    'contentType':'LINEAR',
    'contentIdType':'SERVICE_ID',
    'contentId':'101',
    'householdId' : 'HH'
}

smHeaders = {'Content-Type': 'application/json',
    'X-Forwarded-For': '110.78.131.21'
}

defaultIdentity = {"cmdcRegion":"16384~16385","upId":"2_HH_0","hhId":"2_HH","devId":"619FDF82A2E5FF35","deviceFeatures":["COMPANION","ABR"],"tenant":"k","sessionId":"158f4a2d-e84e-404e-8e63-04a69aa2ad68","region":"1"}


def streaming_session_setup( contentType, contentId, HHid=None, deviceId=None,ve_test = None):

    global setupParams
    he_utils = ve_test.he_utils

    url = he_utils.PrmUrl + he_utils.StreamingSessionPath
    expectedResponse = copy.deepcopy(setupResponseTemplate)

    if contentType == "LINEAR" :
        setupParams = dict(defaultSetupParamsLinear)
        content = he_utils.getChannel(contentId)

    elif contentType == "VOD" :
        setupParams = dict(defaultSetupParamsVod)
        content = he_utils.assets[contentId]
        expectedResponse['streamingSession']['catalogId'] = setupParams["catalogId"]
    else:
        ve_test.log_assert(False, "Content Type is undefined")

    setupParams["contentId"] = contentId
    setupParams["householdId"] = HHid
    setupParams["deviceId"] = deviceId

    defaultIdentity['hhId'] = HHid
    defaultIdentity['devId'] = deviceId

    smHeaders['x-cisco-vcs-identity'] = json.dumps(defaultIdentity)

    jData = json.dumps(setupParams, indent = 2)
    r = requests.post(url, data = jData, headers=smHeaders)

    return r

def concurrency(contentType, policy, maxApcSessions, happy_path = True):

    ve_test = VeTestApi("main_hub:test_verify_concurrency")
    he_utils = ve_test.he_utils

    hhid  = he_utils.default_credentials[0]
    login = he_utils.default_credentials[1]

    if contentType=='VOD':
        policyContent = he_utils.getVodContent(policy)
        nonPolicyContent = he_utils.getVodContent('encrypted')

    else:
        policyContent,tmp = he_utils.getLinearContentABR(policy)
        nonPolicyContent,tmp = he_utils.getLinearContentABR('encrypted')

    if happy_path == True:
        channel_num = nonPolicyContent
    else :
        channel_num = policyContent

    he_utils.deleteApcSessions(hhid)
    time.sleep(WAIT_TIME)
    sessionIds = []

    try:
        for i in range(0,maxApcSessions):
            deviceId = str(random.randint(100, 10000))
            he_utils.addHouseHoldDevices(hhid, [deviceId], deviceFullType = "Android-Phone",drmDeviceType = None)

            logging.info('Sending streaming session setup request on device %s on content with policy %s maxApcSessions=%s' %  (deviceId,policy,maxApcSessions))

            r = streaming_session_setup(contentType, policyContent, HHid =hhid ,deviceId=deviceId,ve_test = ve_test)
            ve_test.log_assert(r.status_code == 200, ' Post request for streaming session failed')
            response = json.loads(r.text)

            sessionId=response['streamingSession']['smSessionId']
            sessionIds.append(sessionId)

            # with the current lab and offers, there are no created APC sessions
            #apcSession = he_utils.getApcSession(hhid, deviceId)
            #logging.info('APC session CreationTime=%s'%apcSession['lastUpdateTime'])
            #sessionCreationTime = datetime.datetime.strptime(apcSession['lastUpdateTime'], "%Y-%m-%dT%H:%M:%SZ")
            #time.sleep(WAIT_TIME)
            #keepAliveUrl = he_utils.PrmUrl + he_utils.StreamingSessionPath + sessionIds[i] + '/keepAlive'
            #ve_test.log_assert(requests.post(url=keepAliveUrl, headers=smHeaders).status_code == 204,'Keep Alive Request failed')
            #apcSession = he_utils.getApcSession(hhid, deviceId)
            #logging.info('APC session LastUpdateTime=%s'%apcSession['lastUpdateTime'])
            #sessionLastUpdate = datetime.datetime.strptime(apcSession['lastUpdateTime'], "%Y-%m-%dT%H:%M:%SZ")
            #making sure that SM update APC session in keepAlive request
            #ve_test.log_assert(sessionCreationTime < sessionLastUpdate, 'APC session update time didnt change after keep alive')


        # check when the max is reached without UI
        #logging.info("Sending streaming session setup request after max is reached")
        #deviceId = str(random.randint(100, 10000))
        #he_utils.addHouseHoldDevices(hhid, [deviceId], deviceFullType = "Android-Phone",drmDeviceType = None)
        #r = streaming_session_setup(contentType, policyContent, HHid =hhid ,deviceId=deviceId,ve_test = ve_test)
        #ve_test.log_assert(r.status_code == 500, 'Post request for streaming session succeeded after max is reached')
        #response = json.loads(r.text)
        #ve_test.log_assert(str(response["errorResponse"]["errorCode"]) == '603', 'Post request for streaming session succeeded after max is reached')


        # check when the max is reached with UI
        ve_test.begin(screen=ve_test.screens.fullscreen)
        ve_test.wait(WAIT_TIME)

        if  ve_test.milestones.get_current_screen() == "fullscreen":
            logging.info('the fullscreen is shown, tune to the channel that triggers the concurrency problem %s' %channel_num)
            zaplist = ve_test.screens.zaplist
            ve_test.wait(WAIT_TIME)
            status = zaplist.tune_to_channel_by_sek(channel_num, True, False)
            if not status:
                ve_test.log_assert(status, 'Failed to tune by the Zaplist')
            ve_test.wait(WAIT_TIME)
        else:
            logging.info('the fullscreen is NOT shown, maybe the concurency problem has occured on the current channel %s' %channel_num)
            pass

        if happy_path == True:
            ve_test.screens.playback.verify_streaming_playing()

        else :
            logging.info('Current screen is %s' %ve_test.milestones.get_current_screen())

            ve_test.check_notification_screen('shown', msg_code=E_STREAMING_CONCURRENCY_ERROR_CODE,msg_text=E_STREAMING_CONCURRENCY_ERROR_MSG)

            # Verify the playback status of the content
            ve_test.screens.playback.verify_streaming_stopped()

            # realease a session to retry a streaming on the current device
            he_utils.session_release(sessionId)
            ve_test.wait(WAIT_TIME)

            ve_test.appium.key_event("KEYCODE_DPAD_DOWN")
            ve_test.wait(WAIT_TIME)

            ve_test.appium.key_event("KEYCODE_DPAD_UP")
            ve_test.wait(WAIT_TIME)

            ve_test.screens.playback.verify_streaming_playing()
            ve_test.wait(WAIT_TIME_LONG)
    except:
        raise
    finally:
        for sessionId in sessionIds:
            he_utils.session_release(sessionId)
        ve_test.end()


@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_1_concurrency_max_content_encrypted_linear():
    concurrency('LINEAR', 'encrypted', MAX_CONTENT,happy_path=False)
    pass

