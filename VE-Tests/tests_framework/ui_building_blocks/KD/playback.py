__author__ = 'bwarshaw'

from time import sleep
from enum import Enum
from tests_framework.ui_building_blocks.screen import Screen
import logging
from  retrying import retry
from datetime import datetime


''' Constants '''
START_STREAMING_TIMEOUT = 15
FILTER_KEY = 0
FILTER_VALUE = 1

#TODO change that after channels will be assigned and delivered to campnou
class SpecialChannels(Enum):
    HOTSPOT = 'xxx'
    VODAFONE = 'xxx'
    GEOLOCATION = 'xxx'
    OUT_OF_HOME='160'

class Playback(Screen):
    def __init__(self, test):
        Screen.__init__(self, test)
        self.stored_streaming_session_id = None

    def play_linear_encrypted_content(self, playback_time, verification_units=5, screen=None):
        self.play_linear_content(playback_time, verification_units, screen, "encrypted")

    def play_linear_clear_content(self, playback_time, verification_units=5, screen=None):
        self.play_linear_content(playback_time, verification_units, screen, "clear")

    def play_linear_content(self, playback_time, verification_units, screen, contentType):
        channel_id, channel_prop = self.test.he_utils.getLinearContentABR(contentType)
        self.test.log("playing linear content on channel %s of type %s" % (channel_id, contentType))

        if screen == None:
            screen = self.test.screens.zaplist
        screen.navigate()
        screen.tune_to_channel_by_sek(channel_id)
        self.test.wait(5)
        playback_status = self.test.milestones.getPlaybackStatus()
        if contentType == "encrypted":
            playback_drm_type = self.test.milestones.get_value(playback_status, 'sso', 'sessionDrmType')
            self.test.log_assert(playback_drm_type.lower()=='vgdrm', "playback type is not vgdrm. type=%s" % playback_drm_type)
        playback_buffer_prev = playback_status['playbackBufferCurrent']

        for retry in range(playback_time/verification_units):
            self.test.wait(verification_units)
            playback_status = self.test.screens.playback.verify_streaming_playing(url=channel_prop['url'])
            self.test.log_assert(playback_status['playbackBufferCurrent'] > playback_buffer_prev, "Playback is not in progress. prev_buffer = %s, current_buffer = %s" % (playback_buffer_prev, playback_status['playbackBufferCurrent']))

    def verify_streaming_stopped(self, previouslyTuned=None):
        playback_status = self.test.milestones.getPlaybackStatus()
        state = playback_status["playbackState"]
        if state == "STOPPED" or state == "UNKNOWN":
            return playback_status
        currentTuned = self.get_current_tuned()
        self.test.log_assert(currentTuned != previouslyTuned, "Still playing same stream")
        logging.info('playbackState is ' + state + ' and the playing object is ' + currentTuned)
        return playback_status

    def verify_streaming_paused(self):
        playback_status = self.test.milestones.getPlaybackStatus()
        state = playback_status["playbackState"]
        self.test.log_assert(state == "PAUSED" or state == "UNKNOWN", "Pause streaming failed, state is {}".format(state))
        logging.info('playbackState is PAUSED')
        return playback_status

    def channel_is_qam_only(self, chennelId):
        qam_channels = self.test.he_utils.cable_only_services
        for channel in qam_channels:
            if(channel['serviceEquivalenceKey'] == chennelId):
                return True
        return False

    def verify_streaming_playing(self, url=None, skip_not_playable_channel = False, verify_position = False):
        check_completed = not (skip_not_playable_channel)
        channelId = "Unknown"
        playback_status={}

        for i in range(START_STREAMING_TIMEOUT):
            notification = self.test.screens.notification.get_notification_message()
            in_notification_screen = self.test.milestones.get_current_screen(overrideIfNotification=False)
            in_error = in_notification_screen and notification
            self.test.log_assert(not in_error, "Error displayed : %s" % notification)
            playback_status = self.test.milestones.getPlaybackStatus()
            state = playback_status["playbackState"]
            if 'currentChannelId' in playback_status:
                channelId = playback_status['currentChannelId']
            # if state == "PLAYING" and  playback_status['sso']:
            if state == "PLAYING" and playback_status.has_key('sso'):
                break
            else:
                if(state == "STOPPED" and check_completed == False):
                    check_completed = True
                    if playback_status['playbackType'] == "LINEAR":
                        if(not self.isChannelPlayable(playback_status['currentChannelId'])):
                            return playback_status
            sleep(1)

        if playback_status['playbackType'] == "LINEAR":
            self.test.log_assert(state == "PLAYING", "Linear Playback streaming failed playing. channelId: %s \n playback status: %s" % (channelId, playback_status))
        else:
             self.test.log_assert(state == "PLAYING", "VOD Playback streaming failed playing. \n playback status: %s " % playback_status)

        if url is not None:
            sessionPlaybackUrl = self.test.milestones.get_value(playback_status, 'sso', 'sessionPlaybackUrl')
            self.test.log_assert(sessionPlaybackUrl == url, "Not playing expected url. expected=%s  actual=%s"%(url, playback_status['sso']['sessionPlaybackUrl']))

        if verify_position:
            @retry(wait_fixed=500, stop_max_delay=30000)
            def check_position(old_playback_status):
                new_playback_status = self.test.milestones.getPlaybackStatus()
                logging.info("old_playback_position: %s, new_playback_position: %s" %(old_playback_status['playbackBufferCurrent'], new_playback_status['playbackBufferCurrent']))
                assert old_playback_status['playbackBufferCurrent'] != new_playback_status['playbackBufferCurrent']
                return new_playback_status
            try:
                playback_status = check_position(playback_status)
            except AssertionError:
                self.test.log_assert(False, "Playback position check fail")

        return playback_status

    def isChannelPlayable(self, channelId):
        #QAM check
        if(self.channel_is_qam_only(channelId)):
            return False
        #channels we cannot tunning right now
        if channelId in [SpecialChannels.VODAFONE.value, SpecialChannels.HOTSPOT.value, SpecialChannels.GEOLOCATION.value, SpecialChannels.OUT_OF_HOME.value]:
            return False
        #known channels with errors
        if channelId in ['53007','50707']:
            return False
        return True

    def get_playback_status(self):
        return self.test.milestones.getPlaybackStatus()

    def get_streaming_session_id(self):
        return self.test.milestones.getPlaybackStatus('sso', 'sessionId')

    def get_current_tuned(self):
        playbackStatus = self.get_playback_status()

        if 'currentAssetId' in playbackStatus:
            return playbackStatus['currentAssetId']
        if 'currentEventId' in playbackStatus:
            return playbackStatus['currentEventId']
        if 'currentChannelId' in playbackStatus:
            return playbackStatus['currentChannelId']
        return None

    def get_current_channel(self):
        playbackStatus = self.get_playback_status()

        if 'currentChannelId' in playbackStatus:
            return playbackStatus['currentChannelId']
        return None

    def is_video_hidden(self):
        return self.test.milestones.getPlaybackStatus('hiddenVideo')

    def store(self):
        self.stored_streaming_session_id = self.get_streaming_session_id()

    def verify_not_stored(self):
        current_session_id = self.get_streaming_session_id()
        sameSessionId = self.stored_streaming_session_id == current_session_id
        self.test.log_assert(not sameSessionId, "Playback has not changed, current: " + str(current_session_id) + " stored: " + str(self.stored_streaming_session_id))

    def keep_alive(self, minutes):
        self.test.wait(60*minutes)
        playback_status = self.test.milestones.getPlaybackStatus()
        self.test.log_assert(playback_status, "No playback status")
        self.test.log_assert("playbackState" in playback_status, "Cannot find playback status")
        self.test.log_assert(playback_status["playbackState"] == "PLAYING", "After " + str(minutes) + " of playback status is " + playback_status["playbackState"])

    def findChannelWithoutOfferX(self,services, offers):
        for offer in offers:
            for channel in services:
                if self.isChannelPlayable(services[channel]['serviceEquivalenceKey']):
                    if offer not in services[channel]['offers']:
                        offerId = offer
                        channelWithoutOffer = services[channel]
                        return offerId, channelWithoutOffer
        return None, None


    def findChannelWithOfferX(self,services, channelX):
        for channel in services:
            if (self.isChannelPlayable(services[channel]['serviceEquivalenceKey'])) and (channelX['serviceEquivalenceKey'] != services[channel]['serviceEquivalenceKey']):
                if channelX['offers'] == services[channel]['offers']:
                    channelWithOffer = services[channel]
                    return channelWithOffer
        return None


    def findTwoChannelsWithDifferentOffers(self):
        services = self.test.he_utils.get_abr_linear_services_from_cmdc()
        channelWithOfferX = None
        channelWithOfferY = None
        for service in services:
            if self.isChannelPlayable(services[service]['serviceEquivalenceKey']):
                channelWithOfferX = services[service]
                offerId,channelWithOfferY = self.findChannelWithoutOfferX(services, channelWithOfferX['offers'])
                if offerId is not None:
                    return channelWithOfferX, channelWithOfferY
        return channelWithOfferX, channelWithOfferY


    def findTwoChannelsWithSameOffers(self):
        services = self.test.he_utils.get_abr_linear_services_from_cmdc()
        channelX = None
        channelY = None
        for service in services:
            if self.isChannelPlayable(services[service]['serviceEquivalenceKey']):
                channelX = services[service]
                channelY = self.findChannelWithOfferX(services, channelX)
                return channelX, channelY
        return channelX, channelY

    def getChannelsByFilters(self, filters):
        services = self.test.he_utils.get_abr_linear_services_from_cmdc()
        filteredServices = {};
        for service in services:
            diffCounter = 0
            for filter in filters:
                if services[service][filter[FILTER_KEY]] != filter[FILTER_VALUE]:
                    diffCounter += 1

            if diffCounter == 0:
                filteredServices[service] = services[service].copy()

        return filteredServices

    def stop_playback(self):
        self.test.screens.trick_bar.navigate()
        self.test.wait(2)
        element = self.test.milestones.getElement([('id', 'exit', '==')])
        self.test.log_assert(element is not None, "no exit element on trick_bar screen")
        self.test.appium.tap_element(element)
        self.test.screens.action_menu.verify_active()

    def pause_playback(self, verify=True):
        self.test.screens.trick_bar.navigate()
        self.test.wait(2)
        element = self.test.milestones.getElement([('id', 'playPauseButton', '==')])
        self.test.log_assert(element is not None, 'no pause element on trick_bar screen')
        self.test.appium.tap_element(element)
        self.test.screens.trick_bar.verify_active()
        if verify:
            self.verify_streaming_paused()

    def rewind_playback(self, verify=True, rewind_time=15, verification_time=3):
        self.test.screens.trick_bar.navigate()
        self.test.wait(2)
        if verify:
            time_before = self.test.milestones.getElement([('id', 'startTime', '==')])[u'title_text']
        element = self.test.milestones.getElement([('id', 'rewind15SecButton', '==')])
        self.test.log_assert(element is not None, 'no rewind element on trick_bar screen')
        self.test.appium.tap_element(element)
        self.test.screens.trick_bar.verify_active()
        if verify:
            self.test.wait(1)  # It takes few milliseconds until the rewind actually happens
            time_after = self.test.milestones.getElement([('id', 'startTime', '==')])[u'title_text']
            # verify rewind succeed
            logging.info('Verify rewind succeed on event')
            delta = datetime.strptime(time_before, '%M:%S') - datetime.strptime(time_after, '%M:%S')
            if (delta.seconds < rewind_time - verification_time) or (delta.seconds > rewind_time + verification_time):
                self.test.log_assert(False,
                                'Failed to rewind 15 seconds! rewind was {} seconds. Time before rewind: {}, time after rewind: {}'.format(
                                    delta.seconds, time_before, time_after))
            logging.info('Rewind was {} seconds'.format(delta.seconds))

            # verify still playing (in new position)
            logging.info('Verify playback still running on event after rewind')
            self.test.screens.playback.verify_streaming_playing()

    # TODO: implement verification for position rario different than 0
    def jump_playback(self, position_ratio=0, verify=True, playback_time=30, verification_time=10):
        self.test.screens.trick_bar.navigate()
        self.test.wait(2)
        if verify:
            time_before = self.test.milestones.getElement([('id', 'startTime', '==')])[u'title_text']
        element = self.test.milestones.getElement([('id', 'playBackScrubberBar', '==')])
        self.test.log_assert(element is not None, 'no playback scrubber bar element on trick_bar screen')
        self.test.appium.tap(int(element['x_pos'])+int(element['width']*position_ratio), int(element['y_pos']))
        self.test.screens.trick_bar.verify_active()
        if verify:
            self.test.wait(1)  # It takes few milliseconds until the rewind actually happens
            time_after = self.test.milestones.getElement([('id', 'startTime', '==')])[u'title_text']
            # verify jump succeed
            logging.info('Verify jump succeed on event')
            delta = datetime.strptime(time_before, '%M:%S') - datetime.strptime(time_after, '%M:%S')
            if (delta.seconds < playback_time - verification_time) or (delta.seconds > playback_time + verification_time) or (
                int(datetime.strptime(time_after, '%M:%S').strftime('%S')) > verification_time) or (
                int(datetime.strptime(time_after, '%M:%S').strftime('%M')) != 0):
                self.test.log_assert(False,
                                "Failed to jump to begining! After playback jump to begin was {} seconds. Time before jump: {}, time after jump: {}".format(
                                    delta.seconds, time_before, time_after))
            logging.info("Jump was {} seconds".format(delta.seconds))

            # verify still playing (in new position)
            logging.info('Verify playback still running on event after jump')
            self.test.screens.playback.verify_streaming_playing()

    def actionMenuToggle(self):
        self.test.ui.center_tap()
        element = self.test.milestones.getElement([('id', 'playPauseButton', '==')])
        if element is None:
            logging.info('Toggled OFF full screen action menu')
        else:
            logging.info('Toggled ON full screen action menu')


    def actionMenuShow(self):
        element = self.test.milestones.getElement([('id', 'playPauseButton', '==')])
        if element is None:
            self.toggleFullscreenActionMenu()
            element = self.test.milestones.getElement([('id', 'playPauseButton', '==')])
            self.test.log_assert(element is not None, "Could not show full screen action menu")

    def actionMenuHide(self):
        element = self.test.milestones.getElement([('id', 'playPauseButton', '==')])
        if element is not None:
            self.toggleFullscreenActionMenu()
            element = self.test.milestones.getElement([('id', 'playPauseButton', '==')])
            self.test.log_assert(element is None, "Could not hide full screen action menu")

    def play_live_multi_audio(self,multi_audio_filter):
        id = self.test.he_utils.getContent("LINEAR", multi_audio_filter, ServiceDeliveryType.ABR, 0)
        sek = self.test.he_utils.services[id]['serviceEquivalenceKey']

        zaplist = self.test.screens.zaplist
        zaplist.tune_to_channel_by_sek(sek, True)
        self.test.wait(5)

    # return a tuple (boolean status, string lang)
    # status is whether the player is playing the given stream/lang
    # lang is the current lang
    def playback_streams_played(self, stream_type, lang):
        playbackStatus = self.test.milestones.getPlaybackStatus()
        stream_played = [stream['language'] for stream in playbackStatus['playbackStreams'] if stream['type'] == stream_type]
        if len(stream_played) > 0:
            stream_lang = stream_played[0]
        else:
            stream_lang = ""

        if lang == "none":
            return (len(stream_played) == 0 or stream_lang == lang , stream_lang)
        else:
            return (len(stream_played) == 1 and stream_lang == lang, stream_lang)
