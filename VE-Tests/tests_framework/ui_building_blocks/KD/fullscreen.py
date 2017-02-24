
__author__ = 'bwarshaw'

from tests_framework.ui_building_blocks.screen import Screen, ScreenActions
import logging

'''Constants'''
TIMEOUT = 2


class Fullscreen(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "fullscreen")

    def navigate(self, verify_active = True):
        screen = self.test.milestones.get_current_screen()
        logging.info("Navigate to fullscreen from screen %s" % screen)

        if screen == "login":
            self.test.screens.login_screen.wait_untill_not_active()
            screen = self.test.milestones.get_current_screen()
        elif screen == "boot":
            self.test.screens.boot.wait_untill_not_active()
            screen = self.test.milestones.get_current_screen()

        if screen == "notification":
            self.test.screens.fullscreen.go_to_previous_screen()
            self.test.wait(1)
            screen = self.test.milestones.get_current_screen()

        if screen == "fullscreen":
            return

        elif screen == "tv_filter":
            self.test.screens.tv_filter.dismiss()

        elif screen == "zap_list":
            self.test.screens.zaplist.dismiss()

        elif screen == "infolayer":
            if self.test.project != "KD":
                self.test.screens.infolayer.dismiss(action = self.test.screens.infolayer.dismissTypes.TAP)
            else:
                self.test.screens.infolayer.dismiss()

        elif screen == "action_menu":
            self.test.screens.linear_action_menu.dismiss()
            if self.test.project != "KD" and self.test.app_mode == "V2":
                self.test.screens.tv_filter.dismiss()   # dismiss KV2 action menu navigates to tv_filter

        elif screen == "timeline":
            self.test.screens.timeline.dismiss()

        elif screen == "timeline_catchup":
            self.test.screens.timeline_catchup.dismiss()

        else:
            self.test.log("navigating to startup screen %s" % self.test.startup_screen.screen_name)
            self.test.startup_screen.navigate()
            self.test.startup_screen.dismiss()

        if verify_active:
            self.verify_active()

    def tune_to_channel_by_sek(self, channel_id, verify_streaming_started=True):
        current_channel = self.test.screens.playback.get_current_channel()
        first_current_channel = current_channel = str(current_channel)
        channel_found = False
        while True:
            if str(current_channel) == str(channel_id):
                channel_found = True
                break
            current_channel = self.channel_change(verify_playing=False, skip_not_playable_channel=True, ignore_notification=True)
            if first_current_channel >= current_channel:
                first_current_channel = current_channel
                continue
            if first_current_channel == current_channel:
                break
        self.test.log_assert(channel_found, "Cannot find channel " + str(channel_id))
        if verify_streaming_started:
            self.test.screens.playback.verify_streaming_playing(skip_not_playable_channel=False)

    def swipe_channel(self, direction=ScreenActions.UP):
        self.navigate()

        current_channel = self.test.screens.playback.get_current_channel()
        logging.info("Current playing channel: %s" % current_channel)

        if self.test.project != "KD" and self.test.app_mode != 'V2':
            self.test.ui.two_finger_swipe(direction)
        else:
            self.test.ui.one_finger_swipe(direction)

    def channel_change(self, direction=ScreenActions.UP, verify_playing=True, skip_not_playable_channel=False, ignore_notification=False):
        info_layer = self.test.screens.infolayer

        self.swipe_channel(direction)

        info_layer.verify_active(ignoreNotification=ignore_notification)
        current_channel = self.test.screens.playback.get_current_channel()
        logging.info("Channel playing after channel change: %s" % current_channel)

        if verify_playing:
            self.test.screens.playback.verify_streaming_playing(skip_not_playable_channel=skip_not_playable_channel)
        return current_channel
