
import json
import os
import logging
from time import sleep
import commands
import calendar
import time

from tests_framework.milestones.milestones_kpi_request_parser import KpiRequestParserAPI
from requests import get

' Global constants '
FIRST_LAUNCH_TIMEOUT = 5
START_STREAMING_TIMEOUT = 10

def getstatusoutput(cmd):
    if os.name == 'nt' or os.name == 'posix':
        "windows usage"
        pipe = os.popen(cmd + ' 2>&1', 'r')
        text = pipe.read()
        pipe.close()
        return 0, text
    else:
        "UNIX usage"
        return commands.getstatusoutput(cmd)

def getoutput(cmd):
    if os.name == 'nt' or os.name == 'posix':
        "windows usage"
        pipe = os.popen(cmd, 'r')
        text = pipe.read()
        pipe.close()
        return text
    else:
        "UNIX usage"
        return commands.getoutput(cmd)

def getListElementByKey(elements,  key):
        for element in elements:
            for current_key in element.keys():
                if key in current_key:
                    return element[ current_key ]
        return False


def create_sessionGuardHeader(configuration, deviceId, hhid):
    sessionInfo = json.dumps({'hhId':hhid, 'upId':hhid+'_0', 'sessionId':'1234', 'devId':deviceId})
    sessionGuardHeader = {"x-cisco-vcs-identity" :  sessionInfo}
    return sessionGuardHeader

def getJsonFromUrl(vetest, utils, directLink, hhid):
    start = directLink.find('/ctap')
    if (start < 0):
        start = directLink.find('/sf14')
    vetest.log_assert(start >= 0, "no /ctap or /sf14 in url")
    directLink = directLink[start:len(directLink)]
    directLink = 'http://' + utils.configuration["he"]["applicationServerIp"] + directLink
    device_details = utils.milestones.getDeviceDetails()
    deviceId = device_details['drm-device-id']
    resp = get(directLink, headers=create_sessionGuardHeader(utils.configuration, deviceId, hhid))
    data = json.loads(resp.text)
    return data


def getElementInBorders(elements, panel, strict=False, name="event_view"):
    x = panel["x_pos"]
    y = panel["y_pos"]
    width = panel["width"]
    height = panel["height"]

    result = list()
    for element in elements:
        if(element["name"] == name):
            if(strict):
                if(element["x_pos"] >= x and element["x_pos"] + element["width"] <= x + width and element["y_pos"] >= y and element["y_pos"] + element["height"] <= y + height):
                    result.append(element)
            else:
                if(element["x_pos"] >= x and element["x_pos"]  <= x + width and element["y_pos"] >= y and element["y_pos"] <= y + height):
                    result.append(element)
    return result




def verify_streaming_paused(vetest, milestones):
    playback_status = milestones.getPlaybackStatus()
    state = playback_status["playbackState"]
    vetest.log_assert(state == "PAUSED", "Pause streaming failed")
    logging.info('playbackState is PAUSED')
    return playback_status

def verify_streaming_stopped(vetest, milestones):
    playback_status = milestones.getPlaybackStatus()
    state = playback_status["playbackState"]
    vetest.log_assert(state == "STOPPED" or state == "UNKNOWN", "Stop streaming failed")
    logging.info('playbackState is STOPPED')
    return playback_status

import pprint
def dump(obj):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(obj)




def verify_streaming_playing(vetest, milestones, url=None):
    for i in range(START_STREAMING_TIMEOUT):
        playback_status = milestones.getPlaybackStatus()
        state = playback_status["playbackState"]
        if state == 'PLAYING':
            break
        sleep(1)
        
    if "sso" in playback_status:
        vetest.log_assert(state == 'PLAYING', ("Start streaming failed : url is not playing",playback_status['sso']['sessionPlaybackUrl']) )
        if url is not None:
             vetest.log_assert(playback_status['sso']['sessionPlaybackUrl'] == url, "Not playing expected url. expected=%s  actual=%s"%(url, playback_status['sso']['sessionPlaybackUrl']))
    else:
        current_screen=vetest.get_current_screen()
        vetest.log_assert("sso" in playback_status, "sso session not created - (current_screen=%s)"%current_screen)

    return playback_status
    




def start_app_signin(utils, hh_test):
    utils.appium.reset_app()
    utils.appium.turn_on_device()
    "Launch applicaiton"
    utils.appium.launch_app()
    sleep(FIRST_LAUNCH_TIMEOUT)
    "print app info"
    device_details = utils.milestones.getDeviceDetails()
    logging.info('%s', json.dumps(device_details))

    if utils.configuration["general"]["dummyApp"] == "True":
        hh_id = hh_test
        user_name = "dummy"
    else:
        hh_id, user_name = utils.he_utils.createDefaultHouseHoldForTests(hh_test)
    utils.building_blocks.sign_in(hh_id, user_name)

    return hh_id


def getInternetTime():
    resp = get("http://www.google.com")
    print "Google date/time: {0}".format(resp.headers['date'])
    return int(calendar.timegm((time.strptime(resp.headers['date'], '%a, %d %b %Y %H:%M:%S %Z'))) * 1000)


