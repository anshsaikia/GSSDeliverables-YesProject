__author__ = 'callix'

from tests_framework.ve_tests.assert_mgr import AssertMgr
from tests_framework.ve_tests.ve_test import VeTestApi
import pytest
import logging
import random

GENERIC_WAIT = 2


@pytest.mark.FS_Zaplist
@pytest.mark.stress
@pytest.mark.LV_L4
def test_zaplist_stress():
    '''
    Stress test - Launch the Zaplist, perform random navigation and zap by the Zaplist
       Check Zaplist is displayed
       Check that video is playing after zapping
    Done 100 times
    :return:
    '''
    test = VeTestApi("test_zaplist_stress")
    assertmgr = AssertMgr(test)
    test.begin(screen=test.screens.fullscreen)

    'Go to Initial Conditions: fullscreen'
    status = test.screens.fullscreen.navigate()
    assertmgr.addCheckPoint("test_zaplist_stress", 1, status, "Failed to go to fullscreen")
    test.wait(GENERIC_WAIT)

    ' Launch the Zaplist'
    directions = ['up', 'down']
    for index in range(1, 100):
        nb_key_press = random.randrange(1, 150)
        launch_way = random.choice(directions)
        direction = random.choice(directions)
        status = test.screens.zaplist.navigate(launch_way)
        assertmgr.addCheckPoint("test_zaplist_stress", 2, status, "Failed to launch the Zaplist")
        test.wait(GENERIC_WAIT)
        logging.info("iteration= %d, nb_key_press= %d, direction= %s" % (index, nb_key_press, direction))
        for key in range(0, nb_key_press):
            test.screens.zaplist.move(direction, 0.2)
            key += 1

        if test.milestones.get_value_by_key(test.milestones.getElements(), "screen") != 'zap_list_tv':
            logging.info("screen= %s" % test.milestones.get_value_by_key(test.milestones.getElements(), "screen"))
            assertmgr.addCheckPoint("test_zaplist_stress", 3, False, "Zaplist is no more displayed after move: iteration= %d, nb_key_press= %d, direction= %s" % (index+1, nb_key_press, direction))

        test.screens.fullscreen.navigate()
        playback_status = test.screens.playback.verify_streaming_playing( test.milestones)
        logging.info("playbackState: %s" % playback_status["playbackState"])
        if playback_status["playbackState"] != 'PLAYING':
                        assertmgr.addCheckPoint("test_zaplist_stress", 4, False, "Start streaming failed : url is not playing %s" % playback_status['sso']['sessionPlaybackUrl'])
        test.wait(5)

    assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_zaplist_stress #####")