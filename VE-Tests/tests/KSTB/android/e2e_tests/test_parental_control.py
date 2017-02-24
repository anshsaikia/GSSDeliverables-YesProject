import pytest
import logging
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from tests_framework.ve_tests.ve_test import VeTestApi


def get_current_event(events_cache):
    current_time = events_cache["currentTime"]
    for event in events_cache["eventsCache"]:
        start_time = event["startTime"]
        duration = event["duration"]
        if (start_time <= current_time) and ((start_time + duration) > current_time):
            return event
    return


def get_next_event(events_cache):
    next_event = False
    current_time = events_cache["currentTime"]
    for event in events_cache["eventsCache"]:
        start_time = event["startTime"]
        duration = event["duration"]
        if next_event:
            return event
        if (start_time <= current_time) and ((start_time + duration) > current_time):
            next_event = True

    return


def get_next_event_time(current_time, current_event):
    start_time = current_event["startTime"]
    duration = current_event["duration"]
    delay = 0
    if start_time <= current_time:
        delay = duration - (current_time - start_time)

    return int(delay / 1000)


def check_av_blanking(audio_mute_state, video_blanking_state, event_rating, pc_threshold):
    status_audio = True
    status_video = True
    ''' check AV blanking status according their state and current PC threshold and rating'''
    '''  if the blanking and mute states are proper it returns True otherwise False'''
    if pc_threshold != CONSTANTS.NO_PC_THRESHOLD:
        if event_rating >= pc_threshold:
            # should be blanked
            if not audio_mute_state:
                status_audio = False
            if not video_blanking_state:
                status_video = False
        else:
            # should NOT be blanked
            if audio_mute_state:
                status_audio = False

            if video_blanking_state:
                status_video = False
    else:
        # Parental control threshold = -1 => No threshold
        # should NOT be blanked
        if audio_mute_state:
                status_audio = False
        if video_blanking_state:
                status_video = False
    return status_audio, status_video


def check_av_status(ve_test):
    playback_status = ve_test.milestones.getPlaybackStatus()
    events_cache = ve_test.milestones.getPcEventsCache()
    event = get_current_event(events_cache)
    ve_test.log_assert(event, "Current event not found in cache")
    status_av = check_av_blanking(playback_status["hiddenVideo"], playback_status["muted"], event["parentalRating"], events_cache["pcThreshold"])
    logging.info("Video blanking: " + str(playback_status["hiddenVideo"]) + " rating=" + str(event["parentalRating"]) + ". threshold=" + str(events_cache["pcThreshold"]))
    logging.info("Audio blanking: " + str(playback_status["muted"]) + " rating=" + str(event["parentalRating"]) + ". threshold=" + str(events_cache["pcThreshold"]))
    return status_av

@pytest.mark.FS_ParentalRating
@pytest.mark.F_Live
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_tv_locked():
    ve_test = VeTestApi("test_tv_locked")
    he_utils = ve_test.he_utils
    ve_test.begin(screen=ve_test.screens.fullscreen)
    credentials = he_utils.get_default_credentials()
    hhid = credentials[0]

    '''------------------------------------------------------ '''
    ''' 1: NO TV Locked, Live only                                '''
    '''------------------------------------------------------ '''

    ''' Go to fullscreen'''
    ''' Set Parent Control threshold very high to make sure no Blocked TV'''
    rating = CONSTANTS.HIGH_RATING
#    ve_test.begin(screen=ve_test.screens.fullscreen)
    he_utils.setParentalRatingThreshold(hhid, str(rating))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    '''zap to update PC Threshold'''
    ve_test.screens.playback.dca(CONSTANTS.PC_CHANNEL2)
    ve_test.wait(CONSTANTS.SMALL_WAIT)

    '''check AV infolayer is well dismissed'''
    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(status, "info_layer is not shown")
    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
    ve_test.log_assert(status, "info_layer is not dismissed")

    '''check AV status -> Audio not muted and Video not blanked'''
    status = check_av_status(ve_test)
    ve_test.log_assert(status[1], "Video should not blanked issue")
    ve_test.log_assert(status[0], "Audio should not muted issue")

    '''Wait for next event and check that it is Live (AV on)'''
    events_cache = ve_test.milestones.getPcEventsCache()
    event = get_current_event(events_cache)
    ve_test.wait(get_next_event_time(events_cache["currentTime"], event))

    ''' Expected not having Infolayer on Live if PC is not set '''
    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(not status, "info_layer is not shown")

    '''-------------------------------------------------------'''
    ''' 2: TV Locked, No AV and Infolayer ON with PROGRAM LOCKED'''
    '''-------------------------------------------------------'''

    ''' Set Parent Control threshold very low to make sure their is Blocked TV screen'''
    rating = CONSTANTS.LOW_RATING

    '''zap to update PC Threshold'''
    ve_test.screens.playback.dca(CONSTANTS.PC_CHANNEL)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    '''wait a bit longer to get sure the infolayer is removed'''
    ve_test.wait(CONSTANTS.WAIT_TIMEOUT)

    he_utils.setParentalRatingThreshold(hhid, str(rating))
    ve_test.screens.playback.dca(CONSTANTS.PC_CHANNEL2)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    ''' Check that infolayer is shown -> TV Blocked screen '''
    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(status, "info_layer is not shown")
    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
    ve_test.log_assert(not status, "info_layer is dismissed")
    elements = ve_test.milestones.getElements()
    title = ve_test.milestones.get_value_by_key(elements, "focused_event_title")
    ve_test.log_assert(title == "LOCKED PROGRAM", " LOCKED PROGRAM not displayed")

    ''' Check that AV is well muted -> TV Blocked screen '''
    status = check_av_status(ve_test)
    ve_test.log_assert(status[1], "Video should be blanked ")
    ve_test.log_assert(status[0], "Audio should be muted")

    '''Wait the next event and check that it is still locked'''
    events_cache = ve_test.milestones.getPcEventsCache()
    event = get_current_event(events_cache)
    ve_test.wait(get_next_event_time(events_cache["currentTime"], event))

    ''' Check that infolayer is shown -> TV Blocked screen '''
    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(status, "info_layer is not shown")
    elements = ve_test.milestones.getElements()
    title = ve_test.milestones.get_value_by_key(elements, "focused_event_title")
    ve_test.log_assert(title == "LOCKED PROGRAM", " LOCKED PROGRAM not displayed")
    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
    ve_test.log_assert(not status, "info_layer is dismissed")

    ''' Check that AV is well muted -> TV Blocked screen '''
    status = check_av_status(ve_test)
    ve_test.log_assert(status[1], "Video should be blanked ")
    ve_test.log_assert(status[0], "Audio should be muted")

    '''------------------------------------------------------ '''
    ''' 3: Back to TV -> Live and TV Locked alternated        '''
    '''------------------------------------------------------ '''
    ''' Set Parent Control threshold at mid value to make sure their is Blocked TV screen'''
    rating = CONSTANTS.MID_RATING
    he_utils.setParentalRatingThreshold(hhid,  str(rating))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    ''' zap in order to retrieve the new parental threshold'''
    ve_test.screens.playback.dca(CONSTANTS.PC_CHANNEL)
    ve_test.wait(CONSTANTS.WAIT_TIMEOUT)
    ve_test.screens.playback.dca(CONSTANTS.PC_CHANNEL2)
    ve_test.wait(CONSTANTS.WAIT_TIMEOUT)

    '''Go to current event and check that it is Live or Blocked'''
    events_cache = ve_test.milestones.getPcEventsCache()
    event = get_current_event(events_cache)

    ''' check infolayer'''
    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(status, "info_layer is not shown")
    last_event_locked = False

    ''' According to event rating and PC threshold verify the infolayer/fullscreen status: Locked not locked '''
    if (event["parentalRating"] >= rating) and (rating != CONSTANTS.NO_PC_THRESHOLD):
        ''' TV Locked'''
        ve_test.log_assert(status, "info_layer is not shown : parentalRating = "+str(event["parentalRating"]) + " rating="+str(rating))
        elements = ve_test.milestones.getElements()
        title = ve_test.milestones.get_value_by_key(elements, "focused_event_title")
        ve_test.log_assert(title == "LOCKED PROGRAM", " LOCKED PROGRAM not displayed")
        status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
        ve_test.log_assert(not status, "info_layer is dismissed")
        last_event_locked = True

        status = check_av_status(ve_test)
        ve_test.log_assert(status[1], "Video should be blanked ")
        ve_test.log_assert(status[0], "Audio should be muted")
    else:
        ''' Live '''
        ve_test.log_assert(status==False, "info_layer is shown")
        status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
        ve_test.log_assert(status, "info_layer is not dismissed")

        status = check_av_status(ve_test)
        ve_test.log_assert(status[1], "Video should be not blanked ")
        ve_test.log_assert(status[0], "Audio should be not muted")

    '''Wait to next event'''
    events_cache = ve_test.milestones.getPcEventsCache()
    event = get_current_event(events_cache)
    ve_test.wait(get_next_event_time(events_cache["currentTime"], event))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    '''get next current event'''
    event = get_next_event(events_cache)
    '''check infolayer status '''
    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(status, "info_layer is not shown")

    ''' According to event rating and PC threshold verify the infolayer/fullscreen status: Locked not locked '''
    if (event["parentalRating"] >= rating) and (rating != CONSTANTS.NO_PC_THRESHOLD):
        ''' TV Locked'''
        ve_test.log_assert(status, "info_layer is not shown")
        elements = ve_test.milestones.getElements()
        title = ve_test.milestones.get_value_by_key(elements, "focused_event_title")
        ve_test.log_assert(title == "LOCKED PROGRAM", " LOCKED PROGRAM not displayed")
        status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
        ve_test.log_assert(not status, "info_layer is dismissed")
        status = check_av_status(ve_test)
        ve_test.log_assert(status[1], "Video should be  blanked ")
        ve_test.log_assert(status[0], "Audio should be  muted")

    else:
        ''' Live '''
        if last_event_locked:
            status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
            ve_test.log_assert(status, "info_layer is not dismissed")
        else:
            ve_test.log_assert(not status, "info_layer is shown on live")
        status = check_av_status(ve_test)
        ve_test.log_assert(status[1], "Video should be not blanked ")
        ve_test.log_assert(status[0], "Audio should be not muted")

    ve_test.end()


@pytest.mark.FS_ParentalRating
@pytest.mark.F_Live
@pytest.mark.sanity
@pytest.mark.LV_L2
def test_parental_pin_code_ok():
    ve_test = VeTestApi("test_parental_pin_code_ok")
    
    he_utils = ve_test.he_utils
    ve_test.begin(screen=ve_test.screens.fullscreen)
    credentials = he_utils.get_default_credentials()
    hhid = credentials[0]

    '''------------------------------------------------------ '''
    '''  TV Locked, No AV and Infolayer ON with PROGRAM LOCKED'''
    '''------------------------------------------------------ '''
    rating = CONSTANTS.LOW_RATING

#    ve_test.begin(screen=ve_test.screens.fullscreen)
    he_utils.setParentalPin(hhid, "1111")
    he_utils.setParentalRatingThreshold(hhid,  str(rating))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    '''zap to update PC Threshold'''
    ve_test.screens.playback.dca(CONSTANTS.PC_CHANNEL2)
    ve_test.wait(CONSTANTS.SMALL_WAIT)

    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(status, "info_layer is not shown")

    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
    ve_test.log_assert(not status, "info_layer is not dismissed, HH: " + str(he_utils.getHouseHold(hhid) ))

    elements = ve_test.milestones.getElements()
    title = ve_test.milestones.get_value_by_key(elements, "focused_event_title")
    ve_test.log_assert(title == "LOCKED PROGRAM", " LOCKED PROGRAM not displayed")

    status = check_av_status(ve_test)
    ve_test.log_assert(status[1], "Video should be blanked ")
    ve_test.log_assert(status[0], "Audio should be muted")

    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(3)

    '''enter correct pincode'''
    ve_test.screens.pincode.enter_correct_pincode()

    '''check that the live is displayed'''
    status = ve_test.wait_for_screen(CONSTANTS.SMALL_WAIT, 'fullscreen')
    ve_test.log_assert(status, "expected screen fullscreen, actual screen "+str(ve_test.milestones.get_current_screen()))

    ''' Verify that there is not infolayer'''
    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(not status, "info_layer is shown")

    ''' AV check'''
    playback_status = ve_test.milestones.getPlaybackStatus()
    ve_test.log_assert(not playback_status["hiddenVideo"], "Video Blanked")
    ve_test.log_assert(not playback_status["muted"], "Audio Muted")
    ve_test.end()

@pytest.mark.FS_ParentalRating
@pytest.mark.F_Live
@pytest.mark.sanity
@pytest.mark.LV_L3
def test_parental_pincode_incorrect_correct():
    ve_test = VeTestApi("test_parental_pincode_incorrect_correct")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    he_utils = ve_test.he_utils
    credentials = he_utils.get_default_credentials()
    hhid = credentials[0]
    he_utils.setParentalPin(hhid, "1111")

    '''------------------------------------------------------ '''
    '''  TV Locked, No AV and Infolayer ON with PROGRAM LOCKED'''
    '''------------------------------------------------------ '''
    rating = CONSTANTS.LOW_RATING

#    ve_test.begin(screen=ve_test.screens.fullscreen)

    he_utils.setParentalRatingThreshold(hhid, str(rating))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    '''zap to update PC Threshold'''
    ve_test.screens.playback.dca(CONSTANTS.PC_CHANNEL2)
    ve_test.wait(CONSTANTS.SMALL_WAIT)

    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(status, "info_layer is shown")

    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
    ve_test.log_assert(not status, "info_layer is not dismissed, HH: " + str(he_utils.getHouseHold(hhid) ))

    elements = ve_test.milestones.getElements()
    title = ve_test.milestones.get_value_by_key(elements, "focused_event_title")
    ve_test.log_assert(title == "LOCKED PROGRAM", " LOCKED PROGRAM not displayed")

    status = check_av_status(ve_test)
    ve_test.log_assert(status[1], "Video should be blanked ")
    ve_test.log_assert(status[0], "Audio should be muted")

    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(3)

    '''enter incorrect pincode'''
    ve_test.screens.pincode.enter_incorrect_pincode()

    '''check that the number of tries is decremented'''
    status = ve_test.wait_for_screen(CONSTANTS.SMALL_WAIT, 'action_menu')
    ve_test.log_assert(status, "expected screen Pincode action_menu, actual screen "+str(ve_test.milestones.get_current_screen()))

    elements = ve_test.milestones.getElements()
    logging.info("getElements Error "+str(elements))
    pincode_msg = ve_test.milestones.get_value_by_key(elements, "pincode_message")
    logging.info("getElements pincode_msg1 "+pincode_msg)

    ve_test.log_assert(pincode_msg == 'WRONG PIN\nENTER YOUR PINCODE. 2 ATTEMPTS LEFT', "expected pincode message WRONG PIN\nENTER YOUR PINCODE. 2 ATTEMPTS LEFT. actual message "+str(pincode_msg))

    '''enter correct pincode'''
    ve_test.screens.pincode.enter_correct_pincode()

    '''check that the live is displayed'''
    status = ve_test.wait_for_screen(CONSTANTS.SMALL_WAIT, 'fullscreen')
    ve_test.log_assert(status, "expected screen fullscreen, actual screen "+str(ve_test.milestones.get_current_screen()))

    ''' Verify that there is not infolayer'''
    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(not status, "info_layer is shown")

    ''' AV check'''
    playback_status = ve_test.milestones.getPlaybackStatus()
    ve_test.log_assert(not playback_status["hiddenVideo"], "Video Blanked")
    ve_test.log_assert(not playback_status["muted"], "Audio Muted")

    ve_test.end()

@pytest.mark.FS_ParentalRating
@pytest.mark.F_Live
@pytest.mark.sanity
@pytest.mark.LV_L2
def test_parental_pincode_incorrect():
    ve_test = VeTestApi("test_parental_pincode_incorrect")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    he_utils = ve_test.he_utils
    credentials = he_utils.get_default_credentials()
    hhid = credentials[0]

    '''------------------------------------------------------ '''
    '''  TV Locked, No AV and Infolayer ON with PROGRAM LOCKED'''
    '''------------------------------------------------------ '''
    rating = CONSTANTS.LOW_RATING

#    ve_test.begin(screen=ve_test.screens.fullscreen)

    he_utils.setParentalRatingThreshold(hhid,  str(rating))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    '''zap to update PC Threshold'''
    ve_test.screens.playback.dca(CONSTANTS.PC_CHANNEL2)
    ve_test.wait(CONSTANTS.SMALL_WAIT)

    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(status, "info_layer is shown")

    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
    ve_test.log_assert(not status, "info_layer is not dismissed, HH: " + str(he_utils.getHouseHold(hhid) ))

    elements = ve_test.milestones.getElements()
    title = ve_test.milestones.get_value_by_key(elements, "focused_event_title")

    ve_test.log_assert(title == "LOCKED PROGRAM", " LOCKED PROGRAM not displayed")
    logging.info("title %s", title)

    status = check_av_status(ve_test)
    ve_test.log_assert(status[1], "Video should be blanked ")
    ve_test.log_assert(status[0], "Audio should be muted")

    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(3)

    '''enter incorrect pincode'''
    ve_test.screens.pincode.enter_incorrect_pincode()

    '''check that the number of tries is decremented'''
    status = ve_test.wait_for_screen(CONSTANTS.SMALL_WAIT, 'action_menu')
    ve_test.log_assert(status, "expected screen Pincode action_menu, actual screen "+str(ve_test.milestones.get_current_screen()))

    elements = ve_test.milestones.getElements()
    logging.info("getElements Error "+str(elements))
    pincode_msg = ve_test.milestones.get_value_by_key(elements, "pincode_message")
    logging.info("getElements pincode_msg1 "+pincode_msg)
    ve_test.log_assert(pincode_msg == 'WRONG PIN\nENTER YOUR PINCODE. 2 ATTEMPTS LEFT', "expected pincode message WRONG PIN ENTER YOUR PINCODE. 2 ATTEMPTS LEFT, actual message "+str(pincode_msg))

    '''enter incorrect pincode'''
    ve_test.screens.pincode.enter_incorrect_pincode()

    '''check that the number of tries is decremented'''
    status = ve_test.wait_for_screen(CONSTANTS.SMALL_WAIT, 'action_menu')
    ve_test.log_assert(status, "expected screen Pincode action_menu, actual screen "+str(ve_test.milestones.get_current_screen()))

    elements = ve_test.milestones.getElements()
    logging.info("getElements Error "+str(elements))
    pincode_msg = ve_test.milestones.get_value_by_key(elements, "pincode_message")
    logging.info("getElements pincode_msg1 "+pincode_msg)
    ve_test.log_assert(pincode_msg == 'WRONG PIN\nENTER YOUR PINCODE. 1 ATTEMPT LEFT', "expected pincode message WRONG PIN\nENTER YOUR PINCODE. 1 ATTEMPT LEFT, actual message "+str(pincode_msg))

    '''enter incorrect pincode'''
    ve_test.screens.pincode.enter_incorrect_pincode()

    '''check that the number of tries is decremented'''
    status = ve_test.wait_for_screen(CONSTANTS.SMALL_WAIT, 'action_menu')
    ve_test.log_assert(status, "expected screen Pincode action_menu, actual screen "+str(ve_test.milestones.get_current_screen()))

    elements = ve_test.milestones.getElements()
    logging.info("getElements Error "+str(elements))
    pincode_msg = ve_test.milestones.get_value_by_key(elements, "pincode_message")
    logging.info("getElements pincode_msg1 "+pincode_msg)

    ve_test.log_assert(pincode_msg == 'WRONG PIN\nPIN BLOCKED, 15 MINUTES left', "expected pincode message: WRONG PIN\nPIN BLOCKED, 15 MINUTES left, actual message "+str(pincode_msg))
    '''check that the AV status'''
    status = check_av_status(ve_test)
    ve_test.log_assert(status[1], "Video should be blanked ")
    ve_test.log_assert(status[0], "Audio should be muted")

    ve_test.end()

@pytest.mark.FS_ParentalRating
@pytest.mark.F_Live
@pytest.mark.sanity
@pytest.mark.LV_L2
def test_parental_pin_code_pin_grace_time():
    ve_test = VeTestApi("test_parental_pin_code_pin_grace_time")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    he_utils = ve_test.he_utils
    credentials = he_utils.get_default_credentials()
    hhid = credentials[0]

    '''------------------------------------------------------ '''
    '''  TV Locked, No AV and Infolayer ON with PROGRAM LOCKED'''
    '''------------------------------------------------------ '''
    rating = CONSTANTS.LOW_RATING

    he_utils.setParentalPin(hhid, "1111")
    he_utils.setParentalRatingThreshold(hhid,  str(rating))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    '''zap to update PC Threshold'''
    ve_test.screens.playback.dca(CONSTANTS.PC_CHANNEL2)
    ve_test.wait(CONSTANTS.SMALL_WAIT)

    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(status, "info_layer is not shown")

    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
    ve_test.log_assert(not status, "info_layer is not dismissed, HH: " + str(he_utils.getHouseHold(hhid) ))

    elements = ve_test.milestones.getElements()
    title = ve_test.milestones.get_value_by_key(elements, "focused_event_title")
    ve_test.log_assert(title == "LOCKED PROGRAM", " LOCKED PROGRAM not displayed")

    status = check_av_status(ve_test)
    ve_test.log_assert(status[1], "Video should be blanked ")
    ve_test.log_assert(status[0], "Audio should be muted")

    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(3)

    '''enter correct pincode'''
    ve_test.screens.pincode.enter_correct_pincode()

    '''check that the live is displayed'''
    status = ve_test.wait_for_screen(CONSTANTS.SMALL_WAIT, 'fullscreen')
    ve_test.log_assert(status, "expected screen fullscreen, actual screen "+str(ve_test.milestones.get_current_screen()))

    ''' Verify that there is not infolayer'''
    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(not status, "info_layer is shown")

    ''' AV check'''
    playback_status = ve_test.milestones.getPlaybackStatus()
    ve_test.log_assert(not playback_status["hiddenVideo"], "Video Blanked")
    ve_test.log_assert(not playback_status["muted"], "Audio Muted")
	
    '''zap to another channel'''
    ve_test.screens.playback.dca(CONSTANTS.PC_CHANNEL)
    ve_test.wait(CONSTANTS.WAIT_TIMEOUT)

    '''come back to the previous channel'''
    ve_test.screens.playback.dca(CONSTANTS.PC_CHANNEL2)
    ve_test.wait(CONSTANTS.SMALL_WAIT)
	
    '''check that the live is displayed'''
    status = ve_test.wait_for_screen(CONSTANTS.SMALL_WAIT, 'fullscreen')
    ve_test.log_assert(status, "expected screen fullscreen, actual screen "+str(ve_test.milestones.get_current_screen()))

    ''' Verify that there is no infolayer'''
    ve_test.wait(CONSTANTS.WAIT_TIMEOUT)
    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(not status, "info_layer is shown")

    ''' AV check'''
    playback_status = ve_test.milestones.getPlaybackStatus()
    ve_test.log_assert(not playback_status["hiddenVideo"], "Video Blanked")
    ve_test.log_assert(not playback_status["muted"], "Audio Muted")
    ve_test.end()
	
@pytest.mark.FS_ParentalRating
@pytest.mark.F_Live
@pytest.mark.sanity
@pytest.mark.LV_L3
def test_parental_pin_code_pin_grace_time_exceed():
    ve_test = VeTestApi("test_parental_pin_code_pin_grace_time_exceed")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    he_utils = ve_test.he_utils
    credentials = he_utils.get_default_credentials()
    hhid = credentials[0]

    '''------------------------------------------------------ '''
    '''  TV Locked, No AV and Infolayer ON with PROGRAM LOCKED'''
    '''------------------------------------------------------ '''
    rating = CONSTANTS.LOW_RATING

    he_utils.setParentalPin(hhid, "1111")
    he_utils.setParentalRatingThreshold(hhid,  str(rating))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    '''zap to update PC Threshold'''
    ve_test.screens.playback.dca(CONSTANTS.PC_CHANNEL2)
    ve_test.wait(CONSTANTS.SMALL_WAIT)

    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(status, "info_layer is not shown")

    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
    ve_test.log_assert(not status, "info_layer is not dismissed, HH: " + str(he_utils.getHouseHold(hhid) ))

    elements = ve_test.milestones.getElements()
    title = ve_test.milestones.get_value_by_key(elements, "focused_event_title")
    ve_test.log_assert(title == "LOCKED PROGRAM", " LOCKED PROGRAM not displayed")

    status = check_av_status(ve_test)
    ve_test.log_assert(status[1], "Video should be blanked ")
    ve_test.log_assert(status[0], "Audio should be muted")

    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(3)

    '''enter correct pincode'''
    ve_test.screens.pincode.enter_correct_pincode()

    '''check that the live is displayed'''
    status = ve_test.wait_for_screen(CONSTANTS.SMALL_WAIT, 'fullscreen')
    ve_test.log_assert(status, "expected screen fullscreen, actual screen "+str(ve_test.milestones.get_current_screen()))

    ''' Verify that there is not infolayer'''
    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(not status, "info_layer is shown")

    ''' AV check'''
    playback_status = ve_test.milestones.getPlaybackStatus()
    ve_test.log_assert(not playback_status["hiddenVideo"], "Video Blanked")
    ve_test.log_assert(not playback_status["muted"], "Audio Muted")
	
    '''zap to another channel'''
    ve_test.screens.playback.dca(CONSTANTS.PC_CHANNEL)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
	
    '''wait 10 minutes'''
    ve_test.wait(CONSTANTS.TEN_MINUTES_WAIT)
	
    '''come back to the previous channel'''
    ve_test.screens.playback.dca(CONSTANTS.PC_CHANNEL2)
    ve_test.wait(CONSTANTS.SMALL_WAIT)

    ''' Verify that there is infolayer'''
    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(status, "info_layer is not shown")

    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
    ve_test.log_assert(not status, "info_layer is not dismissed, HH: " + str(he_utils.getHouseHold(hhid) ))

    elements = ve_test.milestones.getElements()
    title = ve_test.milestones.get_value_by_key(elements, "focused_event_title")
    ve_test.log_assert(title == "LOCKED PROGRAM", " LOCKED PROGRAM not displayed")

    ''' AV check'''
    status = check_av_status(ve_test)
    ve_test.log_assert(status[1], "Video should be blanked ")
    ve_test.log_assert(status[0], "Audio should be muted")
	
    ve_test.end()
	
