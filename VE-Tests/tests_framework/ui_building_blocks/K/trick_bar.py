from tests_framework.ui_building_blocks.screen import Screen, ScreenDismiss
import logging

import math

class TrickBar(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "trick_bar")

    def navigate(self):
        logging.info("Navigate to trick bar")
        elements = self.test.milestones.getElements()
        screen = self.test.milestones.get_current_screen(elements)
        if screen == "trick_bar":
            return

        self.test.log_assert(screen == "fullscreen", "you can only navigate to trick bar during VOD playback, current screen is {0} while it should be fullscreen".format(screen))


        "Open trick bar from fullscreen"
        self.test.ui.center_tap()
        self.test.wait(2)

        self.verify_active()

    def verify_active(self):
        logging.info("Verify Active Trick Bar")
        elements = self.test.milestones.getElements()
        screen = self.test.milestones.get_current_screen(elements)
        self.test.log_assert(screen == "trick_bar", "trick bar should be active, current screen is {0}".format(screen))

    def seek(self, is_tap, percent=0):
        self.navigate()
        self.test.wait(1)
        x_pos, y_pos = self.get_seek_bar_pos()
        if is_tap:
            self.seek_on_tap( x_pos, y_pos, percent)
        else:
            current_position = self.get_current_seek_bar_position()
            self.seek_on_swipe(x_pos, y_pos, current_position, percent)

    def get_seek_bar_pos(self):
        milestones = self.test.milestones
        seek_bar_element = milestones.getElement([("id", "playBackScrubberBar", "==")])
        self.test.log_assert(seek_bar_element, "Seek Bar not present")
        x_pos = int(seek_bar_element['x_pos'])
        y_pos = int(seek_bar_element['y_pos'])
        return x_pos, y_pos

    def seek_on_swipe(self, x_pos, y_pos, current_position, percent = 0):
        self.navigate()
        percent = int(percent)
        milestones = self.test.milestones
        seek_bar_element = milestones.getElement([("id", "playBackScrubberBar", "==")])
        self.test.log_assert(seek_bar_element, "Seek Bar element not present")
        start_x = self.test.mirror.offset(int(x_pos), current_position)
        start_y = y_pos
        stop_x = self.test.mirror.offset(int(x_pos), int(seek_bar_element['width'] * (float(percent)/float(100))))
        stop_y = y_pos
        self.test.appium.swipe_area(start_x, start_y, stop_x, start_y)
        self.test.wait(8)
        """self.verifyTimingLabels()"""
        self.test.appium.swipe_area(start_x, start_y, stop_x, start_y)
        self.test.wait(5)

    def seek_on_tap(self, x_pos, y_pos, percent = 0):
        self.navigate()
        percent = int(percent)
        milestones = self.test.milestones
        seek_bar_element = milestones.getElement([("id", "playBackScrubberBar", "==")])
        self.test.log_assert(seek_bar_element, "Seek Bar element not present")
        tap_x = self.test.mirror.offset(int(x_pos), int(seek_bar_element['width'] * (float(percent)/float(100))))
        self.test.appium.tap(tap_x, y_pos)

    def verifyTimingLabels(self):
        buffer_time = 5
        seek_bar_elements = self.get_seek_bar_elements()
        position = float(seek_bar_elements['playBackScrubberBar']['position'])
        width = float(seek_bar_elements['playBackScrubberBar']['width'])
        current_position = round(float(position/width), 2)

        elapsed_time_label = seek_bar_elements['playBackScrubberBar']['playback_time']
        total_time_label = seek_bar_elements['playBackScrubberBar']['duration']

        self.test.log_assert(total_time_label and elapsed_time_label, \
                             "Timing labels are missing, seek bar elements : %s" %str(seek_bar_elements))

        elapsed_time = self.timing_text_to_int(elapsed_time_label)
        total_time = self.timing_text_to_int(total_time_label)
        if total_time > 30:
            buffer_time += int(math.ceil(total_time / 30)) * 3

        time_range = xrange(elapsed_time - buffer_time, elapsed_time + buffer_time)
        self.test.log_assert(int(total_time * current_position) in time_range, \
            "timing labels incorrect. Total time is %d, and on the elapsed is %d while current_position is %f"\
            %(total_time, elapsed_time, current_position))

    def timing_text_to_int(self, timing_text):
        return int(int(timing_text) / 1000)

    def get_current_seek_bar_position(self):
        self.navigate()
        milestones = self.test.milestones
        seek_bar_element = milestones.getElement([("id", "playBackScrubberBar", "==")])
        self.test.log_assert(seek_bar_element, "Seek Bar not present")
        position = float(seek_bar_element['position'])
        return position

    def get_seek_bar_elements(self):
        self.navigate()
        milestones = self.test.milestones
        elements = milestones.getElements()
        seek_bar_elements = dict()
        seek_bar_elements['playBackScrubberBar'] = milestones.getElementContains(elements, "playBackScrubberBar", "id")
        seek_bar_elements['playPauseButton'] = milestones.getElementContains(elements, "playPauseButton", "id")
        seek_bar_elements['rewind15SecButton'] = milestones.getElementContains(elements, "rewind15SecButton", "id")

    def dismiss(self, action = ScreenDismiss.TAP):
        self.test.log_assert(action in [ScreenDismiss.TAP, ScreenDismiss.CLOSE_BUTTON, ScreenDismiss.BACK_BUTTON], "Unknown action  %s in dismiss trick_bar" % action)
        logging.info("Dismiss trickbar by %s" % action.value)

        self.verify_active()
        if action == ScreenDismiss.TAP:
            self.test.ui.center_tap()

        if action == ScreenDismiss.CLOSE_BUTTON:
            self.test.ui.tap_element("exit")

        if action == ScreenDismiss.BACK_BUTTON:
            self.test.ui.tap_element("back")
