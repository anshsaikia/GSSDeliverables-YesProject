

__author__ = 'bwarshaw'

import logging

from time import sleep
from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ui_building_blocks.screen import ScreenDismiss
from tests_framework.ve_tests.tests_conf import DeviceType

INFO_LAYER_TIMEOUT = 2

class InfoLayer(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "infolayer")
    def show(self):
        if not self.test.screens.infolayer.is_active():
            self.test.screens.fullscreen.navigate()
            self.test.ui.top_tap()
            self.test.screens.infolayer.verify_active()

    def dismiss(self, action = ScreenDismiss.TIMEOUT):
        self.test.log_assert(action in [ScreenDismiss.TAP, ScreenDismiss.TIMEOUT], "Unknown action  %s in dismiss main hub" % action)
        logging.info("Dismiss infolayer by %s" % action.value)

        screen = self.test.milestones.get_current_screen()
        if screen != "infolayer":
            logging.info("Not in info layer screen. screen=%s" % screen)
            return

        if self.test.autoPin and self.test.project.upper() != "KD" and self.is_program_locked():
            self.tap_unlock_program()
            self.test.screens.pincode.enter_pin()
            self.test.screens.pincode.wait_untill_not_active()
            screen = self.test.milestones.get_current_screen()
            if screen != "infolayer":
                logging.info("Not in info layer screen. screen=%s" % screen)
                return

        if action == ScreenDismiss.TIMEOUT:
            video_started = False
            for counter in range(20):
                playback_buffer_curr = self.test.milestones.getPlaybackStatus("playbackBufferCurrent")
                if playback_buffer_curr > 0:
                    video_started = True
                    break
                if playback_buffer_curr == -1:  #in iOS, if it means video is stopped. probably for play error
                    break
                sleep(0.5)

            if not video_started:
                #infoLayer is not dismiss by timeout if there is no playback in background
                logging.warn("Video not started after more than 10 seconds. tap to dismiss infoLayer")
                if self.test.project != "KD":
                    self.test.ui.center_tap()
                else :
                    self.test.ui.top_tap()

            #info layer should be dismissed after 2 seconds after video has been started
            for counter in range(INFO_LAYER_TIMEOUT + 2):
                if self.test.milestones.get_current_screen() != "infolayer":
                    break
                sleep(1)

        elif action == ScreenDismiss.TAP:
            screen = self.test.milestones.get_current_screen()
            if screen != "infolayer":
                logging.info("Not in info layer screen. screen=%s" % screen)
                return
            # self.verify_active()
            if self.test.project != "KD":
                self.test.ui.center_tap()
            else:
                self.test.ui.top_tap()
            self.test.wait(2)

        self.test.screens.infolayer.verify_not_active(timeout=0)

    def getSnapshot(self):
        self.infoLayerData = self.test.milestones.getElements()

    def verify_dismiss_within(self, timeout):
        # todo
        logging.info("***Not implemented***")

    def verify_metadata_KV2(self,lcn):
        elements = self.test.milestones.getElements()
        clientData = self.clientLiveKV2Data()
        serverData = self.test.ctap_data_provider.server_data_for_lcn(lcn)

        serverTitle = serverData['content']["title"].upper()
        clientTitle = clientData["title"].upper()

        serverTime = serverData["airingTime"]
        client_subtitle = clientData["airingTime"]
        server_subtitle = serverTime
        clientStatus = clientData["status"]
        self.test.ctap_data_provider.compare_event_progress_bar(serverData, clientData['progress'])
        on_air_dic = self.test.milestones.get_dic_value_by_key("DIC_FILTER_TV_ON_AIR").upper()
        if(serverData['content']["type"] == 'standalone'):
            serverStatus = on_air_dic
            self.test.log_assert(serverStatus == clientStatus ,"event statuses are different. server : %s, client: %s" % (serverStatus, clientStatus))
        elif(serverData['content']["type"] == 'episode'):
            serverStatus = on_air_dic
            episode_number = serverData['content']['episodeNumber']
            season_number =  serverData['content']['seasonNumber']
            if(season_number):
               season_number_dic = self.test.milestones.get_dic_value_by_key("DIC_SEASON_PREFIX").upper()
               season_str = season_number_dic + season_number
            if(episode_number):
               episode_number_dic = self.test.milestones.get_dic_value_by_key("DIC_EPISODE_PREFIX").upper()
               ep_str = episode_number_dic + episode_number
            server_subtitle = serverTime + " - " + season_str + " " + ep_str
            logging.info("the subtitle is : %s",server_subtitle )
        if(self.test.milestones.getPlaybackStatus('hiddenVideo')):
            unlock_dic = self.test.milestones.get_dic_value_by_key("DIC_ACTION_MENU_ACTION_UNLOCK")
            self.test.log_assert(self.test.milestones.getElementContains(elements, unlock_dic, key='title_text'))
        self.test.log_assert(serverStatus == clientStatus ,"event statuses are different. server : %s, client: %s" % (serverStatus, clientStatus))
        self.test.log_assert(serverTitle == clientTitle,"event titles are different. server : %s, client: %s" % (serverTitle, clientTitle))
        self.test.log_assert(server_subtitle == client_subtitle ,"event times are different. server : %s, client: %s" % (server_subtitle, client_subtitle))

    def verify_data(self, lcn, elements):
        if self.test.project != "KD" and self.test.app_mode == "V2"and (self.test.platform == "iOS"):
           self.verify_metadata_KV2(lcn)
           return
        clientData = self.clientData(elements)
        serverData = self.test.ctap_data_provider.server_data_for_lcn(lcn)

        serverTitle = serverData['content']["title"].upper()
        clientTitle = clientData["title"].upper()
        self.test.log_assert(serverTitle == clientTitle,"event titles are different. server : %s, client: %s" % (serverTitle, clientTitle))
        # serverTime= serverData["airingTime"]
        # clientTime = clientData["airingTime"]
        # self.test.log_assert(serverTime == clientTime ,"event times are different. server : %s, client: %s" % (serverTime, clientTime))
        # self.test.ctap_data_provider.compare_event_progress_bar(serverData, clientData['progress'])

    def verify_tune(self, lcn1, lcn2):
        self.test.log_assert(lcn1 != lcn2, "lcn1 %s != lcn2 %s " %(lcn1,lcn2))

    def tune(self, direction=ScreenActions.UP):
        self.test.screens.fullscreen.navigate()
        if self.test.project != "KD":
            self.test.ui.two_finger_swipe(direction)
        else:
            self.test.ui.one_finger_swipe(direction)
        self.verify_active(ignoreNotification=True)

    def channelChange(self, direction=ScreenActions.DOWN):
        self.test.ui.one_finger_swipe(direction)

    # get logical chanel number from info layer using milestones
    def getLCN(self, elements=None):
        element = self.test.milestones.getElement([("id", "LCN", "==")],elements)
        if(element):
            return self.test.milestones.get_value(element, "title_text")
        else:
            element = self.test.milestones.getElement([("name", "event_view", "==")], elements)
            if(element):
                return self.test.milestones.get_value(element, "channel_number")
        self.test.log_assert(False, "Cannot find LCN element in: " + str(elements))

    def verifyKV2TrickModeBarElements(self,elements):
        startTrickTimeElt = self.test.ui.element_verify('startTime',elements)
        endTrickTimeElt = self.test.ui.element_verify('endTime',elements)
        zaplistElement = self.test.ui.element_verify('zaplist',elements)
        subtitles_el = self.test.ui.element_verify('audioSubtitlesButton',elements)
        back_to_live_el = self.test.ui.element_verify('backToLiveButton',elements)
        if self.test.device_type == DeviceType.TABLET:
            action_menu_el = self.test.ui.element_verify('actionmenu', elements)
        pause_el = self.test.ui.element_verify('playPauseButton',elements)
        rewind_el =self.test.ui.element_verify('timeLine',elements)
        timeLine_el = self.test.ui.element_verify('rewind15SecButton',elements)
        action_button_el = self.test.ui.element_verify('actionButton',elements)
        if(action_button_el):
                action_text = action_button_el['title_text']
        startTime = startTrickTimeElt['title_text']
        endTime = endTrickTimeElt['title_text']
        return startTime, endTime

    def clientLiveKV2Data(self):
        elements = self.test.milestones.getElements()
        titleElement = self.test.ui.element_verify("info_title",elements)
        title = titleElement['title_text']

        progressElement = self.test.ui.element_verify('playBackScrubberBar',elements)
        progress = progressElement['value']

        statusElement = self.test.ui.element_verify( "event_status",elements)
        status = statusElement['title_text']
        time = self.test.milestones.getUniqueElementValue("airing_time",elements)
        channel_logo = self.test.milestones.getUniqueElementValue("channel_logo",elements)
        self.test.log_assert(channel_logo, "Cannot find channel_logo  element") #it is for linear
        self.test.log_assert(time, "Cannot find time")

        startTime, endTime = self.verifyKV2TrickModeBarElements(elements)
        return {"airingTime": time, "title": title,'progress': progress,'status': status, 'startTime': startTime, 'endTime': endTime}

    def clientData(self, elements):
        #self.verify_active()
        if self.test.project != "KD":
            return self.clientLiveKV2Data()
        else:
            #elements = self.test.milestones.getElements()
            titleElement = self.test.milestones.getElement([("id", "info_title", "==")],elements)
            timeElement = self.test.milestones.getElement([("id", "airing_time", "==")],elements)
            progressElement = self.test.milestones.getElement([("name", "progress_view", "==")],elements)
            time = timeElement['title_text']
            self.test.log_assert(timeElement, "Cannot find time element")
            self.test.log_assert(titleElement, "Cannot find title element")
            title = titleElement['title_text']
            self.test.log_assert(progressElement, "Cannot find progress element")
            progress = progressElement['value']
            return { "airingTime" : time, "title" : title, 'progress': progress}

    @property
    def event_data_available(self):
        elements = self.test.milestones.getElements()
        titleElement = self.test.milestones.getElement([("id", "info_title", "==")], elements)
        self.test.log_assert(titleElement, "Cannot find title element")
        title = titleElement['title_text']
        if title == self.test.milestones.get_dic_value_by_key("DIC_NO_TITLE_AVAILABLE","general").upper():
            return False
        else:
            return True



