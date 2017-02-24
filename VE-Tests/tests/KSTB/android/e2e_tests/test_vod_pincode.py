__author__ = 'pculembo'

import pytest
import logging

from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS


def get_device_id(elements, key):
    if elements == None:
        return False
    for element in elements:
        logging.info("element %s"%element)
        if key == element:
            return elements[element]
    return False


def check_pincode_screen(test, rental=False, already_blocked=False):
    '''going into asset action menu'''
    test.validate_focused_item(CONSTANTS.GENERIC_WAIT)
    status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "action_menu")
    test.log_assert(status, "expected action menu screen")
    '''go to RENT option and rent the asset'''
    test.move_towards("up", CONSTANTS.SMALL_WAIT)
    elements = test.milestones.getElements()
    logging.info("getElements ActionMenu "+str(elements))
    if rental:
        #deactivate this test until milestones are corrected
        #entitlement = test.ve_test.milestones.get_value_by_key(elements, "prog_time")
        #logging.info("entitlement "+str(entitlement))
        #check = ("$" in entitlement)
        #logging.info("check "+str(check))
        #test.log_assert("$" in entitlement, "expected $ price, instead "+str(entitlement))
        action = test.milestones.get_value_by_key(elements, "focused_item")
        test.log_assert(action == 'RENT', "expected action RENT , actual action "+str(action))
    else:
        action = test.milestones.get_value_by_key(elements, "focused_item")
        test.log_assert(action in ['PLAY', 'RESUME'], "expected PLAY/RESUME action, actual action "+str(action))
    '''OK on RENT/PLAY/RESUMES'''
    test.validate_focused_item(CONSTANTS.SMALL_WAIT)
    '''Pincode entry should be displayed'''
    screen = test.milestones.get_current_screen()
    logging.info("screen1 "+str(screen))
    test.log_assert(screen == 'action_menu', "expected screen action_menu 1, actual screen "+str(screen))
    elements = test.milestones.getElements()
    logging.info("getElements Error "+str(elements))
    pincode_msg = test.milestones.get_value_by_key(elements, "pincode_message")
    logging.info("getElements pincode_msg "+str(pincode_msg))
    if (already_blocked==False):
        test.log_assert(pincode_msg == 'LOCKED PROGRAM\nPlease enter your PINCODE', "expected pincode message LOCKED PROGRAM\nPlease enter your PINCODE, actual message "+str(pincode_msg))
    #re-enable code below when CTAP is deployed with version implementing "refactoring of PINCODE screen messages"
    #commit : bc481ead08f041d986a64f7470e49327095f73d4 (july 28th)
    #else:
    #    test.log_assert(pincode_msg[:12] == 'PIN BLOCKED,', "expected pincode message PIN blocked, actual message "+str(pincode_msg))


def go_to_first_vod_asset(test):
    test.screens.playback.vod_manager.go_to_vod_asset("TVOD", True)


def verify_correct_pincode_entry(test):
    '''enter correct pincode'''
    test.screens.pincode.enter_correct_pincode()
    '''check that the movie is displayed'''
    test.wait(3)
    if test.screens.playback.vod_manager.is_tvod_playable(test) :
        screen = test.milestones.get_current_screen()
        logging.info("screen "+str(screen))
        test.log_assert(screen == 'trickmode', "expected screen trickmode 2, actual screen "+str(screen))
        '''check that the movie is displayed'''
        status = test.wait_for_screen(CONSTANTS.SCREEN_TIMEOUT, 'fullscreen')
        test.log_assert(status, "expected fullscreen , actual screen "+str(test.milestones.get_current_screen()))
    else:
        status = test.wait_for_screen(CONSTANTS.SCREEN_TIMEOUT, 'notification')
        test.log_assert(status, "expected notification error screen , actual screen "+str(test.milestones.get_current_screen()))


def verify_one_failed_correct_pincode_entry(test, message):
    test.screens.pincode.enter_incorrect_pincode()
    test.wait(2)
    '''check that the number of tries is decremented'''
    screen = test.milestones.get_current_screen()
    logging.info("screen 2nd try "+str(screen))
    test.log_assert(screen == 'action_menu', "expected screen action_menu , actual screen "+str(screen))
    test.wait(3)
    elements = test.milestones.getElements()
    logging.info("getElements Error2 "+str(elements))
    pincode_msg = test.milestones.get_value_by_key(elements, "pincode_message")
    logging.info("getElements pincode_msg2 "+pincode_msg)
    test.log_assert(pincode_msg == message, "expected pincode message " + message + ", actual message " + str(pincode_msg))
    '''enter correct pincode'''
    test.screens.pincode.enter_correct_pincode()
    test.wait(2)
    '''check that the movie is displayed'''
    if test.screens.playback.vod_manager.is_tvod_playable(test) :
        status = test.wait_for_screen(CONSTANTS.SCREEN_TIMEOUT, 'fullscreen')
        test.log_assert(status, "expected fullscreen , actual screen "+str(test.milestones.get_current_screen()))
    else:
        status = test.wait_for_screen(CONSTANTS.SCREEN_TIMEOUT, 'notification')
        test.log_assert(status, "expected notification error screen , actual screen "+str(test.milestones.get_current_screen()))



def verify_blocked_pincode_entry(test, message):
    '''enter incorrect pincode'''
    test.screens.pincode.enter_incorrect_pincode()
    test.wait(2)
    '''check that the number of tries is decremented'''
    screen = test.milestones.get_current_screen()
    logging.info("screen 1st try "+str(screen))
    test.log_assert(screen == 'action_menu', "expected screen action_menu 2, actual screen "+str(screen))
    elements = test.milestones.getElements()
    logging.info("getElements Error1 "+str(elements))
    pincode_msg = test.milestones.get_value_by_key(elements, "pincode_message")
    logging.info("getElements pincode_msg1 "+pincode_msg)
    test.log_assert(pincode_msg == message[0], "expected pincode message "+message[0]+", actual message " + str(pincode_msg))
    '''enter incorrect pincode'''
    test.screens.pincode.enter_incorrect_pincode()
    test.wait(2)
    '''check that the number of tries is decremented'''
    screen = test.milestones.get_current_screen()
    logging.info("screen 2nd try "+str(screen))
    test.log_assert(screen == 'action_menu', "expected screen action_menu 3, actual screen "+str(screen))
    elements = test.milestones.getElements()
    logging.info("getElements Error2 "+str(elements))
    pincode_msg = test.milestones.get_value_by_key(elements, "pincode_message")
    logging.info("getElements pincode_msg2 "+str(pincode_msg))
    test.log_assert(pincode_msg == message[1], "expected pincode message "+message[1]+", actual message " + str(pincode_msg))
    '''enter incorrect pincode'''
    test.screens.pincode.enter_incorrect_pincode()
    test.wait(2)
    '''heck that the pincode entry is blocked'''
    screen = test.milestones.get_current_screen()
    logging.info("screen Locked "+str(screen))
    test.log_assert(screen == 'action_menu', "expected screen action_menu 4, actual screen "+str(screen))

    elements = test.milestones.getElements()
    logging.info("getElements Error3 "+str(elements))
    pincode_msg = test.milestones.get_value_by_key(elements, "pincode_message")
    logging.info("getElements pincode_msg3 "+str(pincode_msg))
    test.log_assert(pincode_msg == message[2], "expected pincode message " + message[2]+" actual message " + str(pincode_msg))


'''
Check that once the user has done OK on RENT, the pincode entry is displayed and that if the user enters a correct pincode, the movie is displayed
'''
@pytest.mark.sanity
@pytest.mark.FS_VOD
@pytest.mark.LV_L2
def test_vod_pincode_correct():
    test = VeTestApi("test_vod_pincode_correct")
    test.begin(screen=test.screens.fullscreen) 

    go_to_first_vod_asset(test)

    check_pincode_screen(test, True)

    '''enter correct pincode'''
    verify_correct_pincode_entry(test)

    test.end()


'''
Check that once the user has done OK on RENT, the pincode entry is displayed and that if the user enters a incorrect pincode followed by a correct pincode, the movie is displayed
'''
@pytest.mark.sanity
@pytest.mark.FS_VOD
@pytest.mark.LV_L3
def test_vod_pincode_incorrect_correct():
    test = VeTestApi("test_vod_pincode_incorrect_correct")

    test.begin(screen=test.screens.fullscreen) 

    go_to_first_vod_asset(test)

    check_pincode_screen(test, True)

    '''enter incorrect pincode'''
    verify_one_failed_correct_pincode_entry(test, 'WRONG PIN\nENTER YOUR PINCODE. 2 ATTEMPTS LEFT')

    test.end()


'''
Check that once the user has done OK on RENT, the pincode entry is displayed and that if the user enters an incorrect pincode, the number of tries is decremented
'''
@pytest.mark.sanity
@pytest.mark.FS_VOD
@pytest.mark.LV_L2
def test_vod_pincode_incorrect():
    test = VeTestApi("test_vod_pincode_incorrect")
    
    test.begin(screen=test.screens.fullscreen) 

    go_to_first_vod_asset(test)

    check_pincode_screen(test, True)

    '''Blocked screen'''
    verify_blocked_pincode_entry(test,  ['WRONG PIN\nENTER YOUR PINCODE. 2 ATTEMPTS LEFT', 'WRONG PIN\nENTER YOUR PINCODE. 1 ATTEMPT LEFT', 'WRONG PIN\nPIN BLOCKED, 10 MINUTES left'])

    test.end()


'''
Check that the pincode entry is displaying PIN BLOCKED message if PIN is already blocked. And check that PIN is unblocked after 15 minutes
'''
@pytest.mark.FS_VOD
@pytest.mark.LV_L3
def test_vod_pincode_blocked():
    test = VeTestApi("test_vod_pincode_blocked")

    test.begin(screen=test.screens.fullscreen) 

    go_to_first_vod_asset(test)

    check_pincode_screen(test, True)

    '''Blocked screen'''
    verify_blocked_pincode_entry(test,  ['WRONG PIN\nENTER YOUR PINCODE. 2 ATTEMPTS LEFT', 'WRONG PIN\nENTER YOUR PINCODE. 1 ATTEMPT LEFT', 'WRONG PIN\nPIN BLOCKED, 10 MINUTES left'])

    '''Close and reopen PIN code screen. Check message : PIN blocked '''
    test.go_to_previous_screen(CONSTANTS.GENERIC_WAIT)
    check_pincode_screen(test, True, True)

    '''Close and reopen PIN code screen after 15 minutes. Check message : PIN unblocked '''
    test.go_to_previous_screen(CONSTANTS.GENERIC_WAIT)
    test.wait(CONSTANTS.FIFTEEN_MINUTES_WAIT)
    check_pincode_screen(test, True)

    test.end()
