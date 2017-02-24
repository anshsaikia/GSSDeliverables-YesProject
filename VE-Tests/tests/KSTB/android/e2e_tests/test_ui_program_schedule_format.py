# -*- coding: utf-8 -*-
import pytest
import logging
import re
from tests_framework.ve_tests.ve_test import VeTestApi

from tests_framework.ve_tests.assert_mgr import AssertMgr
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS

'''
====================
LOCAL CONSTANT
====================
'''
NOW_FOCUS_STATE = 1
OVERVIEW_FOCUS_STATE = 4

'''
====================
UTILITIES FUNCTIONS
====================
'''

def get_schedule(ve_test):
    timedate =  ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "prog_schedule_info")
    if timedate == False:
        return "false"                      # if not, boolean can be treated as string -> crash
    return timedate

def is_today_format(timeString):
    # Check that timeString is of type hh.mm - hh.mm AM/PM
    p = re.compile(u'^\d{1,2}\.\d{2} [-—] \d{1,2}\.\d{2} [AP]M$')
    return check_pattern_match(p, timeString)

def is_tomorrow_format(timeString):
    # Check that timeString is of type tomorrow - hh.mm AM/PM
    p = re.compile(u'^TOMORROW [-—] \d{1,2}\.\d{2} [AP]M$', re.IGNORECASE)
    return check_pattern_match(p, timeString)

def is_weekday_format(timeString):
    # Check that timeString is of type ddd - hh.mm AM/PM
    p = re.compile(u'^(mon)|(tue)|(wed)|(thu)|(fri)|(sat)|(sun) [-—] \d{1,2}\.\d{2} [AP]M$', re.IGNORECASE)
    return check_pattern_match(p, timeString)

def is_date_format(timeString):
    # Check that timeString is of type dd.mm.yy - hh.mm AM/PM
    p = re.compile(u'^\d{2}\.\d{2}.\d{2} [-—] \d{1,2}\.\d{2} [AP]M$')
    return check_pattern_match(p, timeString)

def check_pattern_match(pattern, timeString):
    if timeString == False:                         # this can happen -> must prevent crash
        return False
    matchObj = pattern.match(timeString)
    if matchObj is None:
        return False

    return True


def check_format(test, check_function):
    schedule_string = get_schedule(test)
    status = check_function(schedule_string)
    schedule_string = schedule_string.encode('ascii', 'ignore')
    logging.info("schedule_string = %s",schedule_string)

    return status,schedule_string


def check_event(test, expected_focus_state, expected_offset=0):
    # check the event belongs to the right day.
    elements = test.milestones.getElements()
    day_offset = test.milestones.get_value_by_key(elements, "day_offset")
    focus_state = test.milestones.get_value_by_key(elements, "focus_state")
    logging.info("day_offset= {} focus_state = {} ".format(day_offset,focus_state))
    logging.info("expected_offset= {} expected_focus_state = {} ".format(expected_offset,expected_focus_state))

    if ( day_offset == expected_offset ) and ( focus_state == expected_focus_state ):
        event_status = True
    else :
        event_status = False

    return event_status, focus_state, day_offset


def to_guide_next_day(test, nb_days, nb_back):
    test.repeat_key_press("KEYCODE_BACK", nb_back, 3)
    for i in range(nb_days):
        test.move_towards(direction='right', wait_few_seconds=CONSTANTS.SMALL_WAIT)
    test.validate_focused_item()
    status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "guide")

    return status


def to_guide_next_day_from_actionmenu(test, nb_days, action_menu_launched):
    if action_menu_launched:
        status = to_guide_next_day(test, nb_days, 2)
    else:
        status = to_guide_next_day(test, nb_days, 1)

    return status

'''
===================================================
 TESTS
===================================================
'''

@pytest.mark.non_regression
@pytest.mark.FS_ActionMenu
@pytest.mark.F_Guide
@pytest.mark.LV_L3
def test_program_schedule_format():
    """
    The aim of this test is to check that the format of the program schedule String in actionmenu matches the expected format depending on the day :
        Today:              hh.mm - hh.mm AM/PM
        Tomorrow:           TOMORROW - hh.mm AM/PM
        Within next 6 days: ddd - hh.mm AM/PM
        In 7 days or more:  dd.mm.yy - hh.mm AM/PM
    Tests are not case sensitive. Accuracy of times and dates are not part of this test
    """

    ve_test = VeTestApi("test_program_schedule_format")
    assertmgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.fullscreen)

    # Go to guide through tvfilter
    stop_test_status  = ve_test.screens.guide.navigate()
    assertmgr.addCheckPoint("test_program_schedule_format", 2, stop_test_status, "Failed to go to guide")

    ''' Sometimes the milestone retrieved is not correct even the screen is correct.
        So let some time to the screen to be fully updated.
    '''
    ve_test.wait(2)
    '''
    '''
    action_menu_launched = False
    if stop_test_status:
        status,focus_state,day_offset = check_event(ve_test, NOW_FOCUS_STATE )
        assertmgr.addCheckPoint("test_program_schedule_format", 2, status, "Wrong Event selected focus state = {} date offset = {} ".format(focus_state,day_offset))

        # Open Action Menu and check program schedule format. Should be hh.mm - hh.mm AM/PM
        if status:
            stop_test_status = ve_test.screens.action_menu.navigate()
            assertmgr.addCheckPoint("test_program_schedule_format", 3, stop_test_status, "Failed to go to action menu")

            if stop_test_status:
                action_menu_launched = True
                status, schedule_string = check_format(ve_test, is_today_format)
                assertmgr.addCheckPoint("test_program_schedule_format", 4, status, "Wrong format : %s does not match hh.mm - hh.mm AM/PM" % (schedule_string))

    # Go to next day in guide
    if stop_test_status:
        stop_test_status = to_guide_next_day_from_actionmenu(ve_test, 1, action_menu_launched)
        action_menu_launched = False
        assertmgr.addCheckPoint("test_program_schedule_format", 5, stop_test_status, "Fail to go to next day in guide. Current screen: %s" % (ve_test.milestones.get_current_screen()))

        if stop_test_status:
            status,focus_state,day_offset = check_event(ve_test, OVERVIEW_FOCUS_STATE, 0 )
            assertmgr.addCheckPoint("test_program_schedule_format", 6, status, "Wrong Event selected focus state = {} date offset = {} ".format(focus_state,day_offset))
            # Open Action Menu and check program schedule format. Should be TOMORROW - hh.mm AM/PM
            if status:
                stop_test_status = ve_test.screens.action_menu.navigate()
                assertmgr.addCheckPoint("test_program_schedule_format", 7, stop_test_status, "Failed to go to action menu")

                if stop_test_status:
                    action_menu_launched = True
                    status, schedule_string = check_format( ve_test, is_tomorrow_format)
                    assertmgr.addCheckPoint("test_program_schedule_format", 8, status, "Wrong format : %s does not match TOMORROW - hh.mm AM/PM" % (schedule_string))

    # Go to next day in guide
    if stop_test_status:
        stop_test_status = to_guide_next_day_from_actionmenu(ve_test, 1, action_menu_launched)
        action_menu_launched = False
        assertmgr.addCheckPoint("test_program_schedule_format", 9, stop_test_status, "Fail to go to the next day in guide. Current screen: %s" % (ve_test.milestones.get_current_screen()))

        if stop_test_status:
            status,focus_state,day_offset = check_event(ve_test, OVERVIEW_FOCUS_STATE, 1 )
            assertmgr.addCheckPoint("test_program_schedule_format", 10, status, "Wrong Event selected focus state = {} date offset = {} ".format(focus_state,day_offset))

            # Open Action Menu and check program schedule format. Should be DDD - hh.mm AM/PM
            if status:
                stop_test_status = ve_test.screens.action_menu.navigate()
                assertmgr.addCheckPoint("test_program_schedule_format", 11, stop_test_status, "Failed to go to action menu")

                if stop_test_status:
                    action_menu_launched = True
                    status, schedule_string = check_format( ve_test, is_weekday_format)
                    assertmgr.addCheckPoint("test_program_schedule_format", 12, status, "Wrong format : %s does not match DAY - hh.mm AM/PM" % (schedule_string))

    # Go to last weekday in guide
    if stop_test_status:
        stop_test_status = to_guide_next_day_from_actionmenu(ve_test,4, action_menu_launched)
        action_menu_launched = False
        assertmgr.addCheckPoint("test_program_schedule_format", 13, stop_test_status, "Fail to go to guide with the last weekday. Current screen: %s" % (ve_test.milestones.get_current_screen()))

        if stop_test_status:
            status,focus_state,day_offset = check_event(ve_test, OVERVIEW_FOCUS_STATE, 5 )
            assertmgr.addCheckPoint("test_program_schedule_format", 14, status, "Wrong Event selected focus state = {} date offset = {} ".format(focus_state,day_offset))

            # Open Action Menu and check program schedule format. Should be DDD - hh.mm AM/PM
            if status:
                stop_test_status = ve_test.screens.action_menu.navigate()
                assertmgr.addCheckPoint("test_program_schedule_format", 15, stop_test_status, "Failed to go to action menu")

                if stop_test_status:
                    action_menu_launched = True
                    status, schedule_string = check_format( ve_test, is_weekday_format)
                    assertmgr.addCheckPoint("test_program_schedule_format", 16, status, "Wrong format : %s does not match DAY - hh.mm AM/PM" % (schedule_string))

    # Go to next day in guide
    if stop_test_status:
        status = to_guide_next_day_from_actionmenu(ve_test, 1, action_menu_launched)
        action_menu_launched = False
        assertmgr.addCheckPoint("test_program_schedule_format", 17, stop_test_status, "Fail to go to guide. Current screen: %s" % (ve_test.milestones.get_current_screen()))

        if stop_test_status:
            status,focus_state,day_offset = check_event(ve_test, OVERVIEW_FOCUS_STATE, 6 )
            assertmgr.addCheckPoint("test_program_schedule_format", 18, status, "Wrong Event selected focus state = {} date offset = {} ".format(focus_state,day_offset))

            # Open Action Menu and check program schedule format. Should be dd.mm.yy - hh.mm AM/PM
            if status:
                stop_test_status = ve_test.screens.action_menu.navigate()
                assertmgr.addCheckPoint("test_program_schedule_format", 19, stop_test_status, "Failed to go to action menu")

                if stop_test_status:
                    action_menu_launched = True
                    status, schedule_string = check_format( ve_test, is_date_format)
                    assertmgr.addCheckPoint("test_program_schedule_format", 20, status, "Wrong format : %s does not match dd.mm.yy - hh.mm AM/PM" % (schedule_string))

    assertmgr.verifyAllCheckPoints()
    ve_test.end()
    logging.info("##### End test_program_schedule_format #####")

