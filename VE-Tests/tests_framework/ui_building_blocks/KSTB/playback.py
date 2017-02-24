__author__ = 'bwarshaw'

from tests_framework.ui_building_blocks.screen import Screen
from datetime import datetime, timedelta
from time import sleep, time, strftime
import logging
from math import *
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from StringIO import StringIO
import json
import time
import sys
from tests_framework.milestones.milestones_kpi_request_parser import KpiRequestParserAPI

''' Constants '''
START_STREAMING_TIMEOUT = 10
LIVE_PLAYBACK_TYPE="live_playback"
LIVE_INACTIVITY_TYPE="live_inactivity"
VOD_PLAYBACK_TYPE="vod_playback"
VOD_INACTIVITY_TYPE="vod_inactivity"
HAN_VOD_TEST_FILTER_PATH = ('TESTS',)
DEFAULT_VOD_TEST_FILTER_PATH = ('KINDER-ECKE', 'KINDER-MEDIATHEK', 'CARTOONNETWORK', 'STEVENUNIVERSE')
TVOD_ASSET_NAME = "AVATAR HD"
SVOD_ASSET_NAME = "SVOD DIE HARD"

class VODManager(object):
    def __init__(self, ve_test):
        self.ve_test = ve_test



    def navigate_to_next_item(self, key, former_selected_item):
        """
            :param test:
            :param key: keycode to go to the next item.
            :param former_selected_item: The currently selected item.
            :return: True is the selection has succeded and return the newly selected item.
        """
        self.ve_test.repeat_key_press(key, 1, 2)
        elements = self.ve_test.milestones.getElements()
        new_selected_item = self.ve_test.milestones.get_value_by_key(elements, "selected_item")
        if not new_selected_item:
            logging.error("No selected item")
            return False,new_selected_item
        else:
            return new_selected_item != former_selected_item, new_selected_item

    def get_vod_asset(self, filter_path, asset_type, asset_title=False):

        status,error_message = self.ve_test.screens.filter.to_filter_leaf_from_filter(filter_path)
        if not status:
            logging.error(error_message)
            return False

        self.ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 2)

        if "SVOD" == asset_type:
            source_type = "vodEntitled"
        else:
            source_type = "vodUnEntitled"

        elements = self.ve_test.milestones.getElements()
        selected_item = self.ve_test.milestones.get_value_by_key(elements, "selected_item")
        asset_list = self.ve_test.milestones.get_value_by_key(elements, "asset_list")
        selected_index = -1
        vod_asset_index = -1
        for i in range(len(asset_list)):
            if "source" in asset_list[i] and source_type in asset_list[i]["source"]:
                logging.info("{} title {} at index {}".format(source_type, asset_list[i]["title"],i))
                if not asset_title:
                    vod_asset_index = i
                elif "title" in asset_list[i] and asset_title in asset_list[i]["title"]:
                    vod_asset_index = i

            if "title" in asset_list[i] and selected_item in asset_list[i]["title"]:
                logging.error("selected_item title {} at index {}".format(asset_list[i]["title"],i))
                selected_index = i

            if selected_index != -1 and vod_asset_index != -1:
                break
        else:
            logging.error("No VOD asset found.")
            return False

        move_index = vod_asset_index - selected_index

        # we are assuming the selected index is the first one
        if move_index != 0:
            for i in range(move_index):

                check_status,selected_item = self.navigate_to_next_item("KEYCODE_DPAD_RIGHT", selected_item)

                if not check_status:
                    check_status,selected_item = \
                        self.navigate_to_next_item("KEYCODE_DPAD_DOWN",
                                                   selected_item)
                    if not check_status:
                        logging.error("No VOD asset selected.")
                        return False

        return True

    def go_to_vod_asset(self, asset_type, force_old_path=False):
        # Let's suppose the UI is in Hub menu
        logging.info("--> go_to_vod_asset")

        if not self.ve_test.screens.main_hub.navigate_to_store():
            return False
        
        he = self.ve_test.configuration['he']
        lab = str(he['lab'])
        logging.info('lab = %s' % lab)

        # TESTS folder (and SVOD) is available on all tenants but TVOD is only available on han for now
        if force_old_path == False and (lab in 'openstack-lwr-han' or "SVOD" in asset_type):
            filter_path = HAN_VOD_TEST_FILTER_PATH
            if not self.get_vod_asset( filter_path, asset_type, asset_title=SVOD_ASSET_NAME):
                return False
            else:
                self.ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 2)
        else :
            filter_path = DEFAULT_VOD_TEST_FILTER_PATH
            if not self.get_vod_asset(filter_path, asset_type):
                return False

        self.ve_test.wait(2)
        logging.info("<-- go_to_vod_asset")
   
        return True

    def go_to_asset_action_menu(self):
        # Let's suppose the UI is in Hub menu

        self.go_to_vod_asset("TVOD")
        # select tvod item
        self.ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 2)
        
    def start_free_playback(self, time_to_wait=0):
        # Let's suppose the UI is in Hub menu
        logging.info("--> start_free_playback")

        if not self.go_to_vod_asset("SVOD"):
            logging.error("Can't select the asset SVOD")
            return False

        # select svod item
        self.ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 5)
        
        # navigate_to_action_in_actionmenu is bugged as of now, just do UP
        # if self.ve_test.screens.action_menu.check_if_action_in_action_menu('PLAY'):
        #   self.ve_test.screens.action_menu.navigate_to_action_in_actionmenu('PLAY')
        # elif self.ve_test.screens.action_menu.check_if_action_in_action_menu('RENT'):
        #   self.ve_test.screens.action_menu.navigate_to_action_in_actionmenu('RENT')
        # else:
        #   test.log_assert(False, "Asset nor playable nor rentable.")
        self.ve_test.repeat_key_press("KEYCODE_DPAD_UP", 1, 2)
        self.ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 2)

        if self.ve_test.milestones.get_current_screen() == self.ve_test.screens.pincode.screen_name:
            # pincode_message is not recoverable for now, wait until milestones are corrected
            # if "pincode_message:" in self.ve_test.milestones.getElements()[0]:
            self.ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 4, 2)
        # else:
            #   test.log_assert(False, "Supposed to have a pin code action")

        # the asset VOD is playing
        self.ve_test.wait(time_to_wait)
        logging.info("<-- start_free_playback")
        return True

    def process_jump_forward(self, time_to_wait=0, show_debugs=False):
        self.ve_test.appium.key_event("KEYCODE_MEDIA_FAST_FORWARD")
        if show_debugs: print( "jump forward")
        self.ve_test.wait(time_to_wait)


    def process_jump_backward(self, time_to_wait=0, show_debugs=False):
        self.ve_test.appium.key_event("KEYCODE_MEDIA_REWIND")
        if show_debugs: print( "jump backward")
        self.ve_test.wait(time_to_wait)

    def process_play_or_pause(self, time_to_wait=0):
        logging.info("--> Play/Pause")
        self.ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
        self.ve_test.wait(time_to_wait)
        logging.info("<-- Play/Pause")

    def process_stop(self, time_to_wait=0):
        logging.info("--> Stop")
        #go in action menu
        self.ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.ve_test.wait(time_to_wait)
        #go on stop option
        self.ve_test.appium.key_event("KEYCODE_DPAD_UP")
        self.ve_test.wait(1)
        #select stop option
        self.ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.ve_test.wait(time_to_wait)
        logging.info("<-- Stop")


    def get_total_duration(self):
        duration_string = self.ve_test.milestones.sendCommand("getDuration")
        try:
            duration = int(duration_string["outParam"])
            return duration
        except ValueError: return -1

    def get_current_position(self, time_to_wait=0, cmd_latency=False):
        logging.info("get_current_position enterred at : " + str(datetime.now()))
        time_millis_before_send_cmd = int(round(time.time() * 1000))

        position_string = self.ve_test.milestones.sendCommand("getCurrentPosition")

        logging.info("get_current_position command is sent at : "  + str(datetime.now()))
        time_millis_after_send_cmd = int(round(time.time() * 1000))

        cmd_latency_millis = 0
        if cmd_latency:
            cmd_latency_millis = time_millis_after_send_cmd - time_millis_before_send_cmd

            if cmd_latency_millis > 1000:
                logging.info("WARNING TAKE CARE ------ VERY HIGH CONNECTION LATENCY "+ str(cmd_latency_millis) +  " (milli)")

        try:
            position = int(position_string["outParam"])
            logging.info("get_current_position will sleep at : "  + str(datetime.now()))
            if time_to_wait > 0 :
                self.ve_test.wait(time_to_wait)
            logging.info("get_current_position return position at : "  + str(datetime.now()))

            logging.info("[position = "+str(position)+"] [latency = "+str(cmd_latency_millis)+" ] [total = "+str((position+cmd_latency_millis)) + "]")
            return (position + cmd_latency_millis)
        except ValueError: return -1

    def jump_forward_to_end_of_stream(self, number_of_seconds_before_eos, time_to_wait=0):
        total_duration = -1
        cpt = 5
        while (total_duration == -1 and cpt > 0):
            cpt-=1
            total_duration = self.get_total_duration()
            self.ve_test.wait(1)
        logging.info("--> total_duration = "+ str(total_duration))
        if (total_duration == -1):
            return
        logging.info("--> Jump Forward EOS : offset = " + str(number_of_seconds_before_eos * 1000) + " - total_duration = "+ str(total_duration))
        current_pos = self.get_current_position()
        old_pos = -1

        while ((current_pos < (total_duration - ((number_of_seconds_before_eos +1) * 1000))) and current_pos > old_pos):
            sys.stdout.write(' >> ')
            self.process_jump_forward(1)
            old_pos = current_pos
            current_pos = self.get_current_position()
            sys.stdout.write(str(current_pos))
            sys.stdout.flush()
        logging.info(" >> EOS. Waiting "+ str(time_to_wait) + " s")
        self.ve_test.wait(time_to_wait)
        logging.info("<-- Jump Forward EOS")


    def jump_backward_to_begin_of_stream(self, time_to_wait=0):
        print "--> Jump Backward BOS"
        current_pos = self.get_current_position()
        # As long as we are not in the first 1000ms jump back
        while current_pos >= 1000:
            sys.stdout.write(' << ')
            self.process_jump_backward(1)
            current_pos = self.get_current_position()
            sys.stdout.write(str(current_pos))
            sys.stdout.flush()
        print "<< BOS. Waiting "+ str(time_to_wait) +" s"
        self.ve_test.wait(time_to_wait)
        print "<-- Jump Backward BOS"

    def check_state(self, assert_mgr, test_name, id, expected_playback_state, expected_screen, reason):
        assert_mgr.addCheckPoint(test_name, id ,
                                (self.ve_test.milestones.getPlaybackStatus()['playbackState'] == expected_playback_state)
                                 and (self.ve_test.milestones.get_current_screen() == expected_screen),
                                 "Invalid check_state(expected_playstate="+expected_playback_state +
                                 ",playback_state="+ self.ve_test.milestones.getPlaybackStatus()['playbackState'] +
                                 ", expected_screen="+ expected_screen + ", current_screen="+ self.ve_test.milestones.get_current_screen()
                                 + ") from : "+ reason
                                )

    def play_multi_language_asset_from_hub(self):
        # Use search to find multi audio asset (AWAKENING)
        # Enter store search screen
        self.ve_test.log_assert(self.ve_test.screens.search.navigate(), "Moving to search screen from hub has failed")

        # Type multi language asset keyword (part of the asset title)
        self.ve_test.screens.filter.search_keyword_typing('AWAKENING',8)      # if the list is smaller than 8 we search directly in the list
        list_sugest = self.ve_test.milestones.get_value_by_key(self.ve_test.milestones.getElements(), "suggestions_list") 
        for elem in list_sugest:
            logging.info("on " + elem)
            self.ve_test.appium.key_event("KEYCODE_DPAD_DOWN")    # move in the list to the good asset name
            if "AWAKENING" in elem.upper():
                break
        self.ve_test.appium.key_event("KEYCODE_DPAD_CENTER")      # on the good item in the list, go to the asset
        self.ve_test.wait(2)

        # Select asset
        self.ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.ve_test.wait(2)

        # Play asset
        self.ve_test.appium.key_event("KEYCODE_DPAD_UP")
        self.ve_test.wait(2)
        self.ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.ve_test.wait(10)

    def get_all_playback_audio_language(self):
        # check that audio is set to expected_language
        request = self.ve_test.milestones.getPlaybackStatus()
        #logging.info("playback Status is (%s)"% (json.dumps(request)) )
        io = StringIO()
        json.dump(request, io)
        parsed_json = json.loads(io.getvalue())
        
        all_audio = []
        for flux_type in parsed_json["allPlaybackStreams"]:
            logging.info("check type: %s"%(flux_type["type"]))
            if flux_type["type"] == "AUDIO":
                logging.info("add audio: %s"%(flux_type["language"]))
                all_audio.append(flux_type["language"])
        
        return all_audio    # a list of strings

        
    def get_current_playback_audio_language(self):
        # check that audio is set to expected_language
        request = self.ve_test.milestones.getPlaybackStatus()
        #logging.info("playback Status is (%s)"% (json.dumps(request)) )
        io = StringIO()
        json.dump(request, io)
        parsed_json = json.loads(io.getvalue())
        return parsed_json["playbackStreams"][1]["language"]    # [0] video  [1] audio
    
        
    def check_playback_audio_language(self, assertmgr,test_name, id ,expected_language):
        # check that audio is set to expected_language
        request = self.ve_test.milestones.getPlaybackStatus()
        logging.info("playback Status is (%s)"% (json.dumps(request)) )
        io = StringIO()
        json.dump(request, io)
        parsed_json = json.loads(io.getvalue())

        logging.info("Audio language is (%s)"% (parsed_json["playbackStreams"][1]["language"]) )

        if parsed_json["playbackStreams"][1]["language"] != expected_language:
            assertmgr.addCheckPoint(test_name, id , False, "Current language is not the expected one")

    def select_playback_audio_language(self,value):
        #go into Vod asset action menu
        self.ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
        logging.info("In action menu ")
        self.ve_test.wait(3)
        self.ve_test.wait_for_screen(5, "action_menu")

        #go to language options.
        self.ve_test.appium.key_event("KEYCODE_DPAD_UP")
        self.ve_test.wait(3)
        elements = self.ve_test.milestones.getElements()
        logging.info("getElements ActionMenu "+str(elements))
        action = self.ve_test.milestones.get_value_by_key(elements, "focused_item")
        logging.info("focused_item "+str(action))
        self.ve_test.log_assert(action == 'LANGUAGES', "expected action LANGUAGES, actual action "+str(action))
        self.ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.ve_test.wait(5)

         # select playback audio language from the list of available language.

        values_list = self.ve_test.milestones.get_value_by_key(self.ve_test.milestones.getElements(), "audioItems")

        if value not in values_list:
            logging.error("couldn't find %s in %s" % (value, values_list))
            return False

        selected_asset = self.ve_test.milestones.get_value_by_key(self.ve_test.milestones.getElements(), "audioItemSelected")
        if selected_asset == value:
            return True

        for _ in values_list:
            focused_asset = self.ve_test.milestones.get_value_by_key(self.ve_test.milestones.getElements(), "focused_asset")
            if focused_asset == value:
                self.ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
                self.ve_test.wait(CONSTANTS.GENERIC_WAIT)
                # double check it was selected
                selected_asset = self.ve_test.milestones.get_value_by_key(self.ve_test.milestones.getElements(), "audioItemSelected")
                if selected_asset != value:
                    logging.error("%s was not selected ! (still %s)" % (value, selected_asset))
                    return False
                return True
            self.ve_test.appium.key_event("KEYCODE_DPAD_RIGHT")
            self.ve_test.wait(CONSTANTS.GENERIC_WAIT)

        logging.error("couldn't select %s in %s ..." % (value, values_list))
        return False

    def is_tvod_playable(self, test):
        device_details = self.ve_test.milestones.getDeviceDetails()
        deviceId = device_details['drm-device-id']
        cmdc_device_type = self.ve_test.he_utils.getCmdcDeviceType(deviceId)
        logging.info("cmdc_device_type "+cmdc_device_type)
        return cmdc_device_type == "STB"

class Playback(Screen):
    def __init__(self, test):
        Screen.__init__(self, test)
        self.vod_manager = VODManager(test)

    def verify_streaming_stopped(self):
        playback_status = self.test.milestones.getPlaybackStatus()
        state = playback_status["playbackState"]
        self.test.log_assert(state == "STOPPED" or state == "UNKNOWN", "Stop streaming failed")
        self.test.log('playbackState is STOPPED')
        return playback_status

    def verify_streaming_paused(self):
        playback_status = self.test.milestones.getPlaybackStatus()
        state = playback_status["playbackState"]
        self.test.log_assert(state == "PAUSED", "Pause streaming failed")
        self.test.log('playbackState is PAUSED')
        return playback_status

    def verify_streaming_playing(self, url=None):
        for i in range(START_STREAMING_TIMEOUT):
            playback_status = self.test.milestones.getPlaybackStatus()
            state = playback_status["playbackState"]
            if state == "PLAYING":
                break
            sleep(1)
        elements = self.test.milestones.getElements()
        error_msg = self.test.milestones.get_value_by_key(elements, "msg_text")
        self.test.log_assert(state == "PLAYING", "Playback streaming failed playing : error_msg = {0}\n"
                                                 "getPlayback_status: {1}"
                                                 "milestone: {2}".format(str(error_msg), playback_status, elements))

        if isinstance(playback_status, bool):
            logging.error("Failure to retrieve valid playback status: {0}".format(playback_status))
            return playback_status

        if url is not None:
            if 'sso' in playback_status and 'sessionPlaybackUrl' in playback_status['sso']:
                self.test.log_assert(playback_status['sso']['sessionPlaybackUrl'] == url,
                                     "Not playing expected url.\nexpected={0}  \nactual  ={1}"
                                     .format(url, playback_status['sso']['sessionPlaybackUrl']))
            else:
                self.test.log_assert(False, "No sso in the playback status: {0}".format(playback_status))

        return playback_status

    def verify_streaming_playing_kpi(self, test_type, url=None):
        for i in range(START_STREAMING_TIMEOUT):
            playback_status = self.test.milestones.getPlaybackStatus()
            # If needed, in order to debug
        # dump(playback_status)
            state = playback_status["playbackState"]
            if state == 'PLAYING':
                break
            sleep(1)

        if "sso" in playback_status:
            if state != 'PLAYING':
                self.kpi_to_html(test_type)

            self.test.log_assert(state == 'PLAYING', ("Start streaming failed : url is not playing",playback_status['sso']['sessionPlaybackUrl']) )

            if url is not None:
                 if playback_status['sso']['sessionPlaybackUrl'] != url:
                      self.kpi_to_html(test_type)
                      self.test.log_assert(playback_status['sso']['sessionPlaybackUrl'] == url, "Not playing expected url. expected=%s  actual=%s"%(url, playback_status['sso']['sessionPlaybackUrl']))
        else:
            self.test.log_assert("sso" in playback_status, "sso session not created")

        return playback_status



    def verify_playing_url(self, previous_url, index, playing=True, compare = "=="):
        playback_status = self.test.milestones.getPlaybackStatus()
        state = playback_status["playbackState"]
        if playing == True:
            self.test.log_assert(state == 'PLAYING', ("player state="+state+" loop index="+str(index)))
            newUrl = playback_status['sso']['sessionPlaybackUrl']
            if compare == "==":
                self.test.log_assert(previous_url == newUrl, ("new URL="+newUrl+" previous URL="+previous_url+" loop index="+str(index)))
            else :
                self.test.log_assert(previous_url != newUrl, ("new URL="+newUrl+" previous URL="+previous_url+" loop index="+str(index)))
        else:
            self.test.log_assert(state != 'PLAYING', ("player state="+state+" loop index="+str(index)) )
            newUrl = ""
        return newUrl

    def get_playback_status(self):
        return self.test.milestones.getPlaybackStatus()


    def get_streaming_session_id(self):
        playback_status = self.test.milestones.getPlaybackStatus()
        if isinstance(playback_status, bool):
            logging.error("Failure to retrieve valid playback status: {0}".format(playback_status))
            return False

        if 'sso' in playback_status and 'id' in playback_status['sso']:
            return self.test.milestones.getPlaybackStatus()['sso']['id']

        logging.error("Failure to retrieve sessionPlaybackUrl {0}".format(playback_status))
        return False

    def get_current_tuned(self):
        playback_status = self.test.milestones.getPlaybackStatus()
        if isinstance(playback_status, bool):
            logging.error("Failure to retrieve valid playback status: {0}".format(playback_status))
            return False

        if 'sso' in playback_status and 'channelId' in playback_status['sso']:
            return self.test.milestones.getPlaybackStatus()['sso']['channelId']

        logging.error("Failure to retrieve sessionPlaybackUrl {0}".format(playback_status))
        return False

    def retrieve_session_playback_url(self):
        playback_status = self.test.milestones.getPlaybackStatus()
        if isinstance(playback_status, bool):
            logging.error("Failure to retrieve valid playback status: {0}".format(playback_status))
            return False

        if 'sso' in playback_status and 'sessionPlaybackUrl' in playback_status['sso']:
            return self.test.milestones.getPlaybackStatus()['sso']['sessionPlaybackUrl']

        logging.error("Failure to retrieve sessionPlaybackUrl {0}".format(playback_status))
        return False

    def dca(self, channel_number, tempo=0.3, time_out=2, with_ok=False):
        """
        Perform a zapping by dca
        :param channel_number: number of the channel to zap to
        :param tempo: in seconds. Time to wait before inputing a key
        :param time_out: in seconds. Time to wait before returning from the method
        :param with_ok: boolean. Pressing ok after inputing the channel number
        :return: None
        """
        for char in str(channel_number) :
            self.test.wait(tempo)
            self.test.appium.key_event_adb("KEYCODE_" + char, waitForReady=False)
        self.test.wait(time_out)

    def zap_to_next_channel(self, wait_few_seconds):
            self.test.appium.key_event("KEYCODE_DPAD_DOWN")
            self.test.wait(wait_few_seconds)

    def zap_to_previous_channel(self, wait_few_seconds):
            self.test.appium.key_event("KEYCODE_DPAD_UP")
            self.test.wait(wait_few_seconds)

    def verify_duration(self,expected_duration, compare = "equal"):
        duration_string = self.test.milestones.sendCommand("getDuration")
        try: duration = int(duration_string["outParam"])
        except ValueError: self.test.log_assert(False, "Not a number")

        if compare == "equal":
          self.test.log_assert(duration == expected_duration, ("duration = ", duration, "expected = ", expected_duration))
        if compare == "more":
          self.test.log_assert(duration >= expected_duration, ("duration = ", duration, "expected : equal or more than ", expected_duration))
        if compare == "less":
          self.test.log_assert(duration <= expected_duration, ("duration = ", duration, "expected : equal or less than ", expected_duration))
        return duration

    def verify_position(self, expected_position, compare = "equal", delta = 1000):
        position_string = self.test.milestones.sendCommand("getCurrentPosition")
        try: position = int(position_string["outParam"])
        except ValueError: self.test.log_assert(False, "Not a number")
        timestamp_position = datetime.fromtimestamp(int(position) / 1000)
        logging.info("position is %d     %s" % (position, timestamp_position))

        timestamp_expected_position = datetime.fromtimestamp(int(expected_position) / 1000)
        logging.info("expected_position is %d     %s" % (expected_position, timestamp_expected_position))

        if compare == "equal":
          self.test.log_assert(position == expected_position, ("position = ", position, "expected = ", expected_position))
        if compare == "more":
          self.test.log_assert(position >= expected_position, ("position = ", position, "expected : equal or more than ", expected_position))
        if compare == "less":
          self.test.log_assert(position <= expected_position, ("position = ", position, "expected : equal or less than ", expected_position))
        if compare == "about":
          self.test.log_assert(position <= expected_position + delta, "position = {} expected : equal or less than {} ".format(position,expected_position + delta))
          self.test.log_assert(position >= expected_position - delta, "position = {} expected : equal or more than {} ".format(position,expected_position - delta))
        return position

    def verify_output_type(self, expected_output_type):
        output_type = self.test.milestones.sendCommand("getPlaybackOutputType")
        self.test.log_assert (output_type["outParam"] == expected_output_type, ("output type = ",output_type["outParam"], " expected = ", expected_output_type))
        return output_type

    def verify_streaming_muted(self,expectedMuted):
        playback_status = self.test.milestones.getPlaybackStatus()
        self.test.log_assert(playback_status["muted"] == expectedMuted,"incorrect mute state")
        return playback_status

    def verify_streaming_blanked(self, expectedMuted):
        playback_status = self.test.milestones.getPlaybackStatus()
        self.test.log_assert(playback_status["hiddenVideo"] == expectedMuted,"incorrect 'hidden video' state")
        return playback_status

    def verify_percent_dimmer(self, expectedPercent):
        client_playback_status = self.test.milestones.getClientPlaybackStatus()
        self.test.log_assert(client_playback_status["dimmer"]["percent"] == expectedPercent,"incorrect 'dimmer percent' state")
        return client_playback_status

    def kpi_to_html(self, test_type):
        if (test_type == LIVE_PLAYBACK_TYPE or test_type == LIVE_INACTIVITY_TYPE):
            request = self.test.milestones.getLiveKpiMeasurement()
        else:
            request = self.test.milestones.getVodKpiMeasurement()
        parserApi = KpiRequestParserAPI(request)
        if (test_type == LIVE_PLAYBACK_TYPE or test_type == VOD_PLAYBACK_TYPE ):
            print "<ul>"
            print "<li> Zapping Number = " + str(parserApi.getSuccessPlaybackNb()) + "</li>"
            print "<li> Maximum zapping duration = " + str(parserApi.getMaxPlaybackStartSequenceDuration())+ "</li>"
            print "<li> Minimum zapping duration = " + str(parserApi.getMinPlaybackStartSequenceDuration())+ "</li>"
            print "<li> Average zapping duration = " + str(parserApi.getAveragePlaybackStartSequenceDuration())+ "</li>"
            print "<li> Zapping Failed Number = " + str(parserApi.getFailedPlaybackNb())+ "</li>"
            print "</ul>"
        else :
            print "<ul>"
            print "<li> inactivity = " + str(parserApi.getInactivityDuration()) + "</li>"
            print "</ul>"

