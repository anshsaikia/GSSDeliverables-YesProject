

__author__ = 'bwarshaw'

import logging


from time import sleep
from tests_framework.ui_building_blocks.screen import Screen



TIMEOUT = 2



class InfoLayer(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "infolayer")
        self.infoLayerData = []

    def navigate(self, direction="up"):
        elements = self.test.milestones.getElements()
        screen = self.test.milestones.get_current_screen(elements)
        if screen == self.screen_name:
            return True
        assert False, "Not implemented"

    def dismiss(self):
        screen = self.test.milestones.get_current_screen()
        if screen != "infolayer":
            logging.info("Not in info layer screen. screen=%s"%screen)
            return

        video_started = False
        for counter in range(20):
            playback_buffer_curr = self.test.milestones.getPlaybackStatus()["playbackBufferCurrent"]
            if playback_buffer_curr > 0:
                video_started = True
                break
            sleep(0.5)

        if not video_started:
            logging.info("Video not started after more than 10 seconds")
            return

        #info layer should be dismissed after 2 seconds after video has been started
        for counter in range(7):
            if self.test.milestones.get_current_screen() != "infolayer":
                break
            sleep(0.5)

        screen = self.test.milestones.get_current_screen()
        self.test.log_assert(screen != "infolayer", "info layer was not dismiss")
        self.test.log_assert(screen == "fullscreen", "not returning to fullscreen after infolayer dismiss")

    def is_showing(self):
        did_show = False
        for i in range(10):
            current_screen = self.test.milestones.get_current_screen()
            if current_screen == "infolayer":
                did_show = True
                break
            sleep(0.5)
        return did_show

    def verify_active_within(self, timeout):
        self.verify_active(timeout)

    def getSnapshot(self):
        self.infoLayerData = self.test.milestones.getElements()

    def verify_dismiss_within(self, timeout):
        # todo
        print "milestones?"

    def verify_data(self, lcn):
        serverData = self.test.ctap_data_provider.server_data_for_lcn(lcn)
        clientData = self.clientData()

        print "LCN = " + lcn
        print "serverData" , serverData
        print str(serverData["title"]) + "  <- S ?=? C ->  " + str(clientData["title"])
        print str(serverData["airingTime"]) + "  <- S ?=? C ->  " + str(clientData["airingTime"])

        assert serverData["title"] != clientData["title"]
        assert serverData["airingTime"] != clientData["airingTime"]

    def verifynotactive(self):
         assert not self.test.ui.verify_screen("KDInfoLayerView")

    def verify_tune(self, lcn1, lcn2):
        assert lcn1 != lcn2



    # get logical chanel number from info layer using milestones
    def getLCN(self):
        # infoLayerData = self.test.milestones.getElements()
        #print "infoLayerData", self.infoLayerData
        element = self.test.milestones.get_value_by_key(self.infoLayerData,"LCN")
        print "lcn1", element
        return element["title_text"]

    def clientData(self):
        print "retrieving client data "
        timeElement = self.test.milestones.get_value_by_key(self.infoLayerData,"InfoLayerView_AiringTime")
        titleElement = self.test.milestones.get_value_by_key(self.infoLayerData, "InfoLayerView_InfoTitle")
        time = timeElement['title_text']
        title = titleElement['title_text']
        print time
        print title

        return { "airingTime" : time, "title" : title}


