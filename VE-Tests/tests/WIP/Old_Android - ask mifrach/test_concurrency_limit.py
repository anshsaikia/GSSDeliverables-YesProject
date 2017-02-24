import pytest
import datetime
import time
import random
import os
import logging
import copy
import json
import httplib
from tests_framework.ve_tests.ve_test import VeTestApi

WAIT_TIME = 3
NUMBER_OF_CONCURRENT_SESSION = 2
INIT_TIME = 60


setupResponseTemplate ={
    'streamingSession' :
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
    'contentIdType':'CONTENT_ID',
    'contentId':'101',
    'householdId' : 'HH'
}
smHeaders = {'Content-Type': 'application/json',
    'X-Forwarded-For': '110.78.131.21'
}

defaultIdentity = {"cmdcRegion":"16384~16385","upId":"2_HH_0","hhId":"2_HH","devId":"619FDF82A2E5FF35","deviceFeatures":["COMPANION","ABR"],"tenant":"kd","sessionId":"158f4a2d-e84e-404e-8e63-04a69aa2ad68","region":"1"}

script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, 'pdsPolicy.json')
pds_policy = json.loads(open(file_path).read())

pds_headers = {'Content-Type': 'application/json'}

def streaming_session_setup( contentType, contentId, HHid=None, deviceId=None,ve_test = None):

    he_utils = ve_test.he_utils

    url = he_utils.PrmUrl + he_utils.StreamingSessionPath
    expectedResponse = copy.deepcopy(setupResponseTemplate)

    if contentType == "LINEAR" :
        setupParams = dict(defaultSetupParamsLinear)
        content = he_utils.services[contentId]

    elif contentType == "VOD" :
        setupParams = dict(defaultSetupParamsVod)
        content = he_utils.assets[contentId]
        expectedResponse['streamingSession'] ['catalogId'] = setupParams["catalogId"]

    else:
        ve_test.log_assert(False,"Content Type is undefined")

    setupParams["contentId"] = contentId
    setupParams["householdId"] = HHid
    setupParams["deviceId"] = deviceId

    defaultIdentity['hhId'] = HHid
    defaultIdentity['devId'] = deviceId

    smHeaders['x-cisco-vcs-identity'] = json.dumps(defaultIdentity)

    jData = json.dumps(setupParams, indent = 2)
    r = ve_test.requests.post(url, data = jData, headers=smHeaders)
    ve_test.log_assert(r.status_code == 200, ' Post request for streaming session failed')
    logging.info('server response: %s' % r)
    return r

def update_local_pds_policy(pdsPolicyName,maxApcSessions):
    global pds_policy
    pds_policy[0]["contentType"]="SUBSCRIPTION"
    pds_policy[0]["definition"]["AND-1"]["LE-1"][0] = pdsPolicyName
    pds_policy[0]["definition"]["AND-1"]["LE-1"][1] = str(maxApcSessions)

    if pdsPolicyName == "sd" or pdsPolicyName == "hd":

        #Update VideoFormat outside defination section
        pds_policy[0]['videoFormat'] = pdsPolicyName

    elif pdsPolicyName == "ANDROID":

        #Update DeviceCategory outside defination section
        pds_policy[0]['deviceCategory'] = pdsPolicyName
    else:

        # Update ProviderId outside defination section
        pds_policy[0]['providerId'] = pdsPolicyName



def concurrency(contentType, policy,happy_path = True, nonPolicy = 'encrypted', pdsPolicyName="Netflix"):

    ve_test = VeTestApi("main_hub:test_verify_concurrency")
    he_utils = ve_test.he_utils
    hhid,login = he_utils.createTestHouseHold()
    maxApcSessions = NUMBER_OF_CONCURRENT_SESSION
    ve_test.wait(INIT_TIME)

    policyChannel,tmpPolicy= he_utils.getLinearContentABR(policy)
    policyContent = tmpPolicy['id']
    nonPolicyChannel,tmpNonPolicy = he_utils.getLinearContentABR(nonPolicy)
    nonPolicyContent = tmpNonPolicy['id']
    offers = ve_test.he_utils.services[nonPolicyContent]['offers'] +  ve_test.he_utils.services[policyContent]['offers']

    ve_test.he_utils.setHouseHoldAuthorization(hhid, offers)
    if happy_path == True:
        channel_num = nonPolicyChannel
    else :
        channel_num = policyChannel


    #Update New Policy in PDS

    pdsUrl = 'http://' + ve_test.configuration['he']['pdsIP'] + '/cp/pds/v1/policies/concurrency'
    currentPolicy = ve_test.requests.get(pdsUrl);
    policy = json.loads(currentPolicy.text)
    update_local_pds_policy(pdsPolicyName,maxApcSessions)

    r = ve_test.requests.put(pdsUrl,json.dumps(pds_policy),headers = pds_headers)
    assert r.status_code == httplib.NO_CONTENT, "Failed to Update PDS Policy\n%s" %r.text

    ve_test.wait(WAIT_TIME)
    he_utils.deleteApcSessions(hhid)
    ve_test.wait(WAIT_TIME)
    sessionIds = []
    try:
        for i in range(0,maxApcSessions):
            deviceId = str(random.randint(100, 10000))
            he_utils.addHouseHoldDevices(hhid, [deviceId], deviceFullType = "Android-Phone",drmDeviceType = None)

            logging.info('Sending streaming session setup request on device %s on content with policy %s maxApcSessions=%s' %  (deviceId,policy,maxApcSessions))

            r = streaming_session_setup(contentType, policyContent, HHid =hhid ,deviceId=deviceId,ve_test = ve_test)
            response = json.loads(r.text)

            sessionIds.append(response['streamingSession']['smSessionId'])
            apcSession = he_utils.getApcSession(hhid, deviceId)
            logging.info('APC session CreationTime=%s'%apcSession['lastUpdateTime'])
            sessionCreationTime = datetime.datetime.strptime(apcSession['lastUpdateTime'], "%Y-%m-%dT%H:%M:%SZ")
            ve_test.wait(WAIT_TIME)
            keepAliveUrl = he_utils.PrmUrl + he_utils.StreamingSessionPath + sessionIds[i] + '/keepAlive'
            ve_test.log_assert(ve_test.requests.post(url=keepAliveUrl, headers=smHeaders).status_code == 204,'Keep Alive Request failed')
            apcSession = he_utils.getApcSession(hhid, deviceId)
            logging.info('APC session LastUpdateTime=%s'%apcSession['lastUpdateTime'])
            sessionLastUpdate = datetime.datetime.strptime(apcSession['lastUpdateTime'], "%Y-%m-%dT%H:%M:%SZ")
            #making sure that SM update APC session in keepAlive request
            ve_test.log_assert(sessionCreationTime < sessionLastUpdate, 'APC session update time didnt change after keep alive')

        ve_test.begin(login=ve_test.login_types.custom)
        if ve_test.platform == "Android":
            ve_test.screens.login_screen.sign_in(hh_id=hhid,user_name=login)

        zaplist = ve_test.screens.zaplist
        ve_test.wait(WAIT_TIME*4)

        # IF first Channel is our channel, then we might get Notification Window : Hence Check n Disable It
        if ve_test.milestones.get_current_screen() == "notification":
            ve_test.screens.notification.dismiss_notification()


        zaplist.tune_to_channel_by_sek(channel_num,verify_streaming_started=False)
        ve_test.wait(WAIT_TIME)


        if happy_path == True:
            ve_test.screens.playback.verify_streaming_playing()

        else :
            element = ve_test.milestones.getElement([("name", "NotificationView", "==")])
            if "maximum" in element['text_0']:
                pass

    except:
        raise
    finally:
        for sessionId in sessionIds:
            he_utils.session_release(sessionId)

        #Update PDS with old policy
        r = ve_test.requests.put(pdsUrl,json.dumps(policy),headers = pds_headers)
        ve_test.end()

@pytest.mark.MF514_MAX_content_resolution_sd_linear
@pytest.mark.export_regression_chn
def test_1_concurrency_max_content_resolution_sd_linear():
    concurrency('LINEAR', 'SD',happy_path=False, nonPolicy = 'HD', pdsPolicyName="sd")
    pass

@pytest.mark.MF514_MAX_content_linear
def test_2_concurrency_max_content_linear():
    concurrency('LINEAR', 'PHX-RDK-Lab',happy_path=False, nonPolicy = 'HD', pdsPolicyName="PHX-RDK-Lab")
    pass

@pytest.mark.MF514_MAX_device_type_linear
def test_3_concurrency_device_type_limit_linear():
    concurrency('LINEAR', 'DeviceType',happy_path=False, nonPolicy = 'HD', pdsPolicyName="ANDROID")
    pass

