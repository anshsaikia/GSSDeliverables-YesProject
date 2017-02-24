import pytest
import logging
from time import sleep
import random
from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ve_tests.ve_test import VeTestApi


'''----------------------------------------------------------------------------------------Tests-------------------------------------------------------------'''

'''
Performance Criteria:
Trigger zap list 100 times.
Zaplist is displayed within 1 second or less at least 80% of the time Remainder 20% Zaplist is displayed within 1 to 2 seconds
'''
@pytest.mark.MF969_Linear_zaplist_stress
def test_zaplist_check_performance():
    ve_test = VeTestApi("zaplist:test_zaplist_check_performance")
    ve_test.begin()

    performance = ve_test.performance
    zaplistMetrics = list()
    ve_test.screens.fullscreen.navigate()
    window_width, window_height = ve_test.milestones.getWindowSize()
    x = window_width/2
    upper_y = window_height*0.1
    lower_y = window_height*0.75
    
    for index in range(0,100):

        'swipe on full screen, wait 1 second, verify that zaplist is displayed'
        #ve_test.appium.swipe_area(x, upper_y, x, lower_y)
        if ve_test.project != "KD":
            ve_test.ui.one_finger_swipe(ScreenActions.DOWN)
        else:
            ve_test.ui.two_finger_swipe(ScreenActions.DOWN)

        sleep(1)
        element = ve_test.milestones.getElement([("screen", "zap_list", "==")])

        if element:
            zaplistMetrics.append(1)
        else:
            'wait an additional second if zaplist was not yet displayed'
            sleep(1)
            element = ve_test.milestones.getElement([("screen", "zap_list", "==")])
            'performance fails if it takes more than 2 seconds to display zaplist after swipe on a full screen'
            ve_test.log_assert(element, "Zaplist was not display within 2 seconds of the swipe.")
            zaplistMetrics.append(2)
        ve_test.screens.fullscreen.navigate()

    performance.verifylist(zaplistMetrics, 80,1)
    twoSecondRun = [entry for entry in zaplistMetrics if entry > 1]
    if twoSecondRun:
        performance.verifylist(twoSecondRun, 100, 2)
    logging.info('Zaplist metrics: [%s]' % ', '.join(map(str, zaplistMetrics)))

    ve_test.end()

'''
zaplist Stress Benchmarks
'''
@pytest.mark.MF969_Linear_zaplist_stress
def test_zaplist_stress():
    ve_test = VeTestApi("zaplist:test_zaplist_stress")
    ve_test.begin()

    for index in range(0,100):
        ve_test.screens.zaplist.navigate()
        seconds = random.randrange(100,4000)
        directions = [ScreenActions.UP,ScreenActions.DOWN]
        direction = random.choice(directions)
        logging.info('iteration= %d, duration= %d, direction= %s' % (index+1,seconds,direction))
        ve_test.screens.zaplist.scroll_from_center(duration=seconds, direction=direction)
        sleep(1)
        elements = ve_test.milestones.getElements()
        current_events = ve_test.screens.zaplist.get_displayed_events(elements)
        ve_test.appium.tap_element(current_events[1])
        sleep(7)

    ve_test.end()
