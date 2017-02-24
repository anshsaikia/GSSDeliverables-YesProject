import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
import logging
from datetime import datetime
from datetime import timedelta
import calendar
from pytz import timezone

UI_TIMEZONE = 'Europe/Berlin'

CHANNEL_WITH_VIDEO_C = 3

# ====================
# UTILITIES FUNCTIONS
# ====================
class kstb_event(object):
    def __init__(self):
        self.title = ""
        self.start_time = ""
        self.duration = ""

    def compare_with_event(self, event):

        if isinstance(event, kstb_event):
            if self.title == event.title and self.start_time == event.start_time and self.duration == event.duration:
                return True
            else:
                logging.error("%s || %s" % (self.title, event.title))
                logging.error("%s || %s" % (self.start_time, event.start_time))
                logging.error("%s || %s" % (self.duration, event.duration))
        return False

    def init_event_from_list_from_sched(self, sched_list, index):
        if 'seriesId' in sched_list[index]:
            if sched_list[index]['seriesId'] != None:
                season_number = ' S' + str(sched_list[index]['seasonNumber'])
                episode_number = ' EP' + str(sched_list[index]['episodeNumber'])
                self.title = sched_list[index]["title"] + season_number + episode_number
            else:
                self.title = sched_list[index]["title"]
        # logging.info("title: %s" % self.title)
        self.start_time = sched_list[index]["startTime"]
        self.duration = sched_list[index]["duration"]


def get_now_epoch_in_milliseconds(current_time=None):
    if current_time == None:
        current_time = datetime.utcnow()
    epoch = calendar.timegm(current_time.timetuple())
    # logging.info("epoch: %s   timetuple: %s " % (epoch, current_time.timetuple()))
    return int(epoch * 1000)


def compare_day_name_in_grid(test, selected_date):
    overview_title = test.screens.guide.get_overview_title_in_guide()

    title_words = str(overview_title).splitlines()
    if len(title_words) > 1:
        overview_day = title_words[1]
        logging.info("Day displayed in the Grid: {0}".format(overview_day))
    else:
        overview_day = ""
        test.log_assert(False, "Failure to retrieve day name in GRID: {0}".format(overview_title))

    # BE CAREFUL, the comparaison is done only in English month fullname
    calendar_day = selected_date.strftime("%A").upper()
    logging.info("Calendar day: {0}".format(calendar_day))

    return calendar_day == overview_day


def compare_filter_day_with_calendar(test, calendar_date):
    '''
    Compare the Day of the month displayed in Filter day with the expected calendar one.
    Compare the Month fullname with the expected calendar one.
    :param test:
    :param calendar_date:
    :return:
    '''
    day_filter = test.screens.main_hub.get_day_in_main_hub()
    calendar_day = calendar_date.day
    month = test.screens.main_hub.get_month_in_main_hub()
    test.log_assert(month is not False, "Failure to retrieve month in day filter")
    month_filter = month.upper()
    calendar_month = calendar_date.strftime("%b").upper()
    # BE CAREFUL, the comparaison is done only in English month fullname
    test.log_assert(int(day_filter) == int(calendar_day) and month_filter == calendar_month,
                    "Day name displayed in Grid {0}/{1} is not the filter one {2}/{3}"
                    .format(calendar_day, calendar_month, day_filter, month_filter))


def compare_event_date_with_grid_date(test, selected_date):
    calendar_day = selected_date.strftime("%d").upper()
    logging.info("calendar day/grid: {0}".format(calendar_day))
    elements = test.milestones.getElements()
    event_start_time = test.milestones.get_value_by_key(elements, "start_time")
    test.log_assert(event_start_time is not False,
                    "Failure to retrieve current event start time.\n{0}".format(elements))
    start_time = datetime.fromtimestamp(event_start_time/1000, timezone(UI_TIMEZONE))
    test.log_assert(int(calendar_day) == int(start_time.day),
                    "The event day ({0}) is not the expected one (grid day: {1})"
                    .format(start_time.day, calendar_day))


# ====================
# TESTS
# ====================

@pytest.mark.non_regression
@pytest.mark.FS_Guide
@pytest.mark.LV_L2
def test_grid():
    # now = datetime.now(timezone(UI_TIMEZONE))
    now = datetime.utcnow()
    ve_test = VeTestApi("Tests_ui_grid")

    ve_test.begin(screen=ve_test.screens.fullscreen)

    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status, "Failed to be in Hub")

    status = ve_test.screens.main_hub.focus_item_in_hub(item_title='GRID')
    ve_test.log_assert(status, "Failed to focus Guide in Hub")

    # move the focus to "GRID"
    if ve_test.is_dummy:
        status = ve_test.screens.filter.focus_menu_item_by_id_in_filter("TELEVISION", "GRID")

    # check the day is today (does not work in dummy mode)
    if not ve_test.is_dummy:
        logging.info("Checking calendar day is today")
        ve_test.log_assert(int(ve_test.screens.main_hub.get_day_in_main_hub()) == int(now.day),
                        ("Calendar day is not today : %s is not %s", str(ve_test.screens.main_hub.get_day_in_main_hub()), str(now.day)))
        ve_test.log_assert((ve_test.screens.main_hub.get_month_in_main_hub()).upper() == (now.strftime("%b")).upper(),
                        ("Calendar month is not today : %s is not %s", str(ve_test.screens.main_hub.get_month_in_main_hub()), str(now.day)))
        logging.info("Calendar day is today")

    # Going into guide
    logging.info("Going into guide")

    status = ve_test.screens.guide.navigate()
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    ve_test.log_assert(status, "to_guide_from_hub failed")

    # check the current day offset is 0
    ve_test.log_assert(ve_test.screens.guide.get_dayOffset_in_guide() == 0, "dayOffset_now is not 0")

    # check different focus state
    focus_state = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focus_state")
    ve_test.log_assert(focus_state == 1, "Current state is %s and NOW is expected." % CONSTANTS.GRID_STATE[focus_state])
    logging.info("Current state is: %s" % CONSTANTS.GRID_STATE[focus_state])
    # Check to have the current duration enough to complete the test
    logging.info("now date is: %s" % now)
    for i in range(1, 10):
        ve_test.move_towards(direction='down')
        milestone = ve_test.milestones.getElements()
        event_start_time = ve_test.milestones.get_value_by_key(milestone, "start_time")
        start_time = datetime.utcfromtimestamp(event_start_time / 1000)
        # start_time = datetime.fromtimestamp(event_start_time/1000, timezone(UI_TIMEZONE))
        logging.info("start_time: %s" % start_time)
        end_time = start_time + timedelta(seconds=ve_test.milestones.get_value_by_key(milestone, "duration")/1000)
        logging.info(" end_time : %s" % end_time)
        # check that event will end in at least 60s
        if end_time > now + timedelta(seconds=120):
            logging.info("Current channel number is: %s" % ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_channel_number'))
            break

    else:
        ve_test.log_assert(True, "Failure to find current event with a end time is more than 1min")

    ve_test.move_towards(direction='right', wait_few_seconds=2)
    focus_state = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focus_state")
    ve_test.log_assert(focus_state == 2, "Current state is %s and NEXT is expected." % CONSTANTS.GRID_STATE[focus_state])
    logging.info("Current state is: %s" % CONSTANTS.GRID_STATE[focus_state])

    ve_test.move_towards(direction='right', wait_few_seconds=2)
    focus_state = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focus_state")
    ve_test.log_assert(focus_state == 3, "Current state is %s and TONIGHT is expected." % CONSTANTS.GRID_STATE[focus_state])
    logging.info("Current state is: %s" % CONSTANTS.GRID_STATE[focus_state])

    ve_test.move_towards(direction='right', wait_few_seconds=2)
    focus_state = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focus_state")
    ve_test.log_assert(focus_state == 4, "Current state is %s and GRID is expected." % CONSTANTS.GRID_STATE[focus_state])
    logging.info("Current state is: %s" % CONSTANTS.GRID_STATE[focus_state])

    ve_test.move_towards(direction='left', wait_few_seconds=2)
    focus_state = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focus_state")
    ve_test.log_assert(focus_state == 3, "Current state is %s and TONIGHT is expected." % CONSTANTS.GRID_STATE[focus_state])
    logging.info("Current state is: %s" % CONSTANTS.GRID_STATE[focus_state])

    ve_test.move_towards(direction='left', wait_few_seconds=2)
    focus_state = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focus_state")
    ve_test.log_assert(focus_state == 2, "Current state is %s and NEXT is expected." % CONSTANTS.GRID_STATE[focus_state])
    logging.info("Current state is: %s" % CONSTANTS.GRID_STATE[focus_state])

    ve_test.move_towards(direction='left', wait_few_seconds=2)
    focus_state = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focus_state")
    ve_test.log_assert(focus_state == 1, "Current state is %s and NOW is expected." % CONSTANTS.GRID_STATE[focus_state])
    logging.info("Current state is: %s" % CONSTANTS.GRID_STATE[focus_state])

    if not ve_test.is_dummy:
        # check first event
        now_time = get_now_epoch_in_milliseconds(now)
        logging.info("utc now time: %s         %s" % (now_time, datetime.utcfromtimestamp(now_time/1000)))
        milestones_event = kstb_event()
        sched_event = kstb_event()

        focused_channel_number = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focused_channel_number")
        sched_list = ve_test.he_utils.get_events_list_from_sched(startTime=now_time,
                                                                      logicalChannelNumber=focused_channel_number,
                                                                      eventCount=1)
        # logging.info("sched_list %s" % sched_list[0])
        sched_event.init_event_from_list_from_sched(sched_list, 0)
        sched_start_time = datetime.utcfromtimestamp(int(sched_event.start_time) / 1000)
        logging.info("sched_event title: %s   start time: %s  human start time: %s  duration: %s" % (
            sched_event.title, sched_event.start_time, sched_start_time, sched_event.duration))

        milestones_event.title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focused_event_title")
        milestones_event.start_time = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"start_time")
        milestones_start_time = datetime.fromtimestamp(int(milestones_event.start_time) / 1000, timezone(UI_TIMEZONE))
        milestones_event.duration = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"duration")
        logging.info("grid event title:  %s   start time: %s  human start time: %s  duration: %s" % (
            milestones_event.title, milestones_event.start_time, milestones_start_time, milestones_event.duration))

        ve_test.log_assert(sched_event.compare_with_event(milestones_event), "event focused doesnt match")
        logging.info("Events match")

        # check NEXT event
        # ve_test.move_towards(direction='left', longpress=True)
        ve_test.move_towards(direction='right', wait_few_seconds=2)
        milesones = ve_test.milestones.getElements()
        focus_state = ve_test.milestones.get_value_by_key(milesones,"focus_state")
        ve_test.log_assert(focus_state == 2,
                        "Current state is %s and NEXT is expected." % CONSTANTS.GRID_STATE[focus_state])

        next_start_time = ve_test.milestones.get_value_by_key(milesones,"start_time")
        next_event_start_time = datetime.fromtimestamp(int(next_start_time) / 1000, timezone(UI_TIMEZONE))
        logging.info("next_start_time is %d     %s" % (next_start_time, next_event_start_time))
        ve_test.log_assert(now_time < next_start_time, "NEXT event should be in the future")
        logging.info("NEXT event is confirmed to be in the future")

        # check zap to different channel and playback channel status = test.to_guide_from_tvfilter()
        ve_test.move_towards(direction='left', wait_few_seconds=2)
        focus_state = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focus_state")
        ve_test.log_assert(focus_state == 1,
                        "Current state is %s and NOW is expected." % CONSTANTS.GRID_STATE[focus_state])

        ve_test.move_towards(direction='down', wait_few_seconds=2)
        new_focused_channel_number = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focused_channel_number")
        ve_test.log_assert(focused_channel_number != new_focused_channel_number, "focused channel number has not changed")

        logging.info("Launch Action Menu and validate PLAY action")
        ve_test.screens.action_menu.navigate()
        ve_test.wait(CONSTANTS.GENERIC_WAIT)
        ve_test.screens.action_menu.navigate_to_action('PLAY')
        ve_test.validate_focused_item()

        logging.info("Check the streaming and the channel")
        playing_status = ve_test.screens.playback.verify_streaming_playing()
        ve_test.log_assert(playing_status, "zapping from grid failed")
        ve_test.wait(CONSTANTS.WAIT_TIMEOUT)
        current_channel = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"current_channel")
        ve_test.log_assert(current_channel == new_focused_channel_number,
                        "Channel number should be different. Live channel: %s   Guide channel:  %s" % (current_channel, new_focused_channel_number))
        ve_test.wait(CONSTANTS.GENERIC_WAIT)

    ve_test.end()


@pytest.mark.non_regression
@pytest.mark.FS_Guide
@pytest.mark.F_Guide_Navigation
@pytest.mark.LV_L2
def test_guide_navigation_future_events():
    """
    Check the navigation through the events into the GRID part (right/left).
    Check events ordering according to event end/start time
    :return:
    """
    test = VeTestApi("test_guide_navigation_future_events")

    test.begin(screen=test.screens.fullscreen)

    logging.info("Access to the Guide")
    status = test.screens.guide.navigate()
    test.log_assert(status, "Failed to go to Guide. Current screen: {0}".format(test.milestones.get_current_screen()))

    test.wait(2*CONSTANTS.GENERIC_WAIT)
    status = test.screens.guide.guide_find_channel_with_events()
    test.log_assert(status, "Failure to find channel with events")

    logging.info("Scroll to the GRID part")
    test.wait(2*CONSTANTS.GENERIC_WAIT)
    guide_state = test.screens.guide.get_guide_focus_state()

    test.log_assert(guide_state == CONSTANTS.GRID_STATE_NOW, "Focus shall be on NOW but is on {0}"
                    .format(CONSTANTS.GRID_STATE[guide_state]))

    now_channel_lcn = test.screens.guide.get_focused_channel_number()
    now_event_title = test.screens.guide.get_focused_event_title()
    test.log_assert(now_channel_lcn is not False and now_event_title is not False,
                    "Failure to retrieve channel lcn and event at Guide access.\nMilestone: {0}"
                    .format(test.milestones.getElements()))

    for nb_move in range(4):
        status = test.screens.guide.guide_goto_next_event(direction='right')
        test.log_assert(status, "Failure to retrieve valid event.\nMilestone: {0}"
                        .format(test.milestones.getElements()))
        guide_state = test.screens.guide.get_guide_focus_state()
        if guide_state == CONSTANTS.GRID_STATE_GRID:
            logging.info("In the GRID part")
            break
    else:
        test.log_assert(guide_state == CONSTANTS.GRID_STATE_GRID, "Failure to access to the GRID part of the Guide. {0}"
                        .format(CONSTANTS.GRID_STATE[guide_state]))

    first_channel_lcn = test.screens.guide.get_focused_channel_number()
    first_event_title = test.screens.guide.get_focused_event_title()
    test.log_assert(first_channel_lcn is not False and first_event_title is not False,
                    "Failure to retrieve channel lcn and event at Guide access.\nMilestone: {0}"
                    .format(test.milestones.getElements()))
    logging.info("Retrieve current Channel lcn: {0} Event: {1} ".format(first_channel_lcn, first_event_title))

    # Check that first event of the GRID is the Now one
    test.log_assert(first_event_title == now_event_title,
                    "First event of the GRID part ({0}) is not the same than the NOW one ({1})"
                    .format(first_event_title, now_event_title))

    list_grid_event = [first_event_title]

    nb_navigation = 30
    logging.info("Navigate through the {0} next events".format(nb_navigation))
    for i in range(nb_navigation):
        status = test.screens.guide.guide_goto_next_event(direction='right', validation_check=True)
        test.log_assert(status is not False, "Failure to navigate in the future events."
                                             " status: {0}  nb events browsed: {1}".format(status, i))
        guide_state = test.screens.guide.get_guide_focus_state()
        test.log_assert(guide_state == CONSTANTS.GRID_STATE_GRID, "Guide state is no more GRID but {0}.\n"
                        "Nb event browsed is {1}".format(guide_state, i))
        list_grid_event.append(test.screens.guide.get_focused_event_title())

    logging.info("Event list browsed: {0}".format(list_grid_event))

    for n in range(nb_navigation):
        guide_state = test.screens.guide.get_guide_focus_state()
        test.log_assert(guide_state == CONSTANTS.GRID_STATE_GRID, "Guide state is no more GRID but {0}.\n"
                        "Nb event browsed is {1}".format(guide_state, n))

        expected_event = list_grid_event.pop()
        current_grid_event = test.screens.guide.get_focused_event_title()
        test.log_assert(expected_event == current_grid_event,
                        "Current event ({0}) is not the expected one ({1})."
                        .format(current_grid_event, expected_event))

        status = test.screens.guide.guide_goto_next_event(direction='left', validation_check=False)
        test.log_assert(status is not False, "Failure to navigate in the future events. "
                                             " status: {0}  nb events browsed: {1}".format(status, n))

    test.end()


@pytest.mark.non_regression
@pytest.mark.FS_Guide
@pytest.mark.F_Guide_Navigation
@pytest.mark.LV_L2
def test_guide_navigation_channels_lineup():
    """
    Check the navigation through channels (up/down) on the entire channels line up.
    Check that the navigation is cyclic.
    :return:
    """
    test = VeTestApi("test_guide_navigation_channels_lineup")

    test.begin(screen=test.screens.fullscreen)

    logging.info("Access to the Guide")
    status = test.screens.guide.navigate()
    test.log_assert(status, "Failed to go to Guide. Current screen: {0}".format(test.milestones.get_current_screen()))

    elements = test.milestones.getElements()
    first_channel_lcn = test.screens.guide.get_focused_channel_number(elements)
    test.log_assert(first_channel_lcn is not False, "Failure to retrieve correct channel number in Guide.\n{0}"
                    .format(elements))

    guide_lcn_list = []
    for n in range(1000):
        current_lcn = test.screens.guide.guide_scroll_channellineup('down')
        test.log_assert(current_lcn is not False, "Failure to retrieve the channel number. Milestone: {0}"
                        .format(test.milestones.getElements()))
        if current_lcn == first_channel_lcn and n != 1:
            break
        guide_lcn_list.append(current_lcn)
    else:
        test.log_assert(False, "Not able to find to come-back on the first channel")

    nb_channels = len(guide_lcn_list)
    logging.info("Nb channels: {0}  Channel List: {1}".format(nb_channels, guide_lcn_list))

    for i in range(nb_channels):
        current_lcn = test.screens.guide.guide_scroll_channellineup('up')
        test.log_assert(current_lcn is not False, "Failure to retrieve the channel number. Milestone: {0}"
                        .format(test.milestones.getElements()))
        expected_lcn = guide_lcn_list.pop()
        test.log_assert(expected_lcn == current_lcn, "Failure to have the same channel list. "
                        "Current lcn: {0}  Expected: {1}"
                        .format(current_lcn, expected_lcn))
    test.end()


@pytest.mark.non_regression
@pytest.mark.FS_Guide
@pytest.mark.F_Guide_Navigation
@pytest.mark.LV_L2
def test_guide_default_event_shown():
    """
    Check that the current on air event is the one focused at Guide launch
    :return:
    """
    test = VeTestApi("test_guide_default_event_shown")

    test.begin(screen=test.screens.fullscreen)

    test.screens.playback.dca(CHANNEL_WITH_VIDEO_C)
    test.wait(CONSTANTS.GENERIC_WAIT)
    logging.info("wait for fullscreen")
    status = test.wait_for_screen(2*CONSTANTS.SCREEN_TIMEOUT, 'fullscreen')
    test.log_assert(status, "Failed to go to fullscreen. Current screen: {0}".format(test.milestones.get_current_screen()))

    status = test.screens.fullscreen.wait_for_event_with_minimum_time_until_end(60)
    test.log_assert(status, "Failure to find event with minimum time until end")

    # Memorize current channel/event
    live_lcn = test.screens.fullscreen.get_current_channel()
    live_event_title = test.screens.fullscreen.get_current_event_title()
    test.log_assert(live_lcn is not False and live_event_title is not False,
                    "Failure to retrieve channel lcn and event on fullscreen.\nMilestone: {0}"
                    .format(test.milestones.getElements()))

    # Access to the Guide and retrieve the focussed channel/event
    status = test.screens.guide.navigate()
    test.log_assert(status, "Failed to go to Guide. Current screen: {0}".format(test.milestones.get_current_screen()))
    test.wait(2*CONSTANTS.GENERIC_WAIT)
    guide_lcn = test.screens.guide.get_focused_channel_number()
    guide_event_title = test.screens.guide.get_focused_event_title()
    test.log_assert(guide_lcn is not False and guide_event_title is not False,
                    "Failure to retrieve channel lcn and event on Guide.\nMilestone: {0}"
                    .format(test.milestones.getElements()))

    # Compare the Live and Channel info
    test.log_assert(live_lcn == guide_lcn, "Focused channel is not the live one. Guide: {0}  Live: {1}"
                    .format(guide_lcn, live_lcn))
    test.log_assert(live_event_title == guide_event_title, "Focused event is not the live one. Guide: {0}  Live: {1}"
                    .format(guide_event_title, live_event_title))

    # Check that the focus is on the NOW column
    guide_state = test.screens.guide.get_guide_focus_state()
    test.log_assert(guide_state == CONSTANTS.GRID_STATE_NOW, "Failure to be on NOW column at Guide launch. State: {0}"
                    .format(CONSTANTS.GRID_STATE[guide_state]))

    test.end()


@pytest.mark.non_regression
@pytest.mark.FS_Guide
@pytest.mark.F_Guide_Navigation
@pytest.mark.LV_L2
def test_guide_filter_days():
    """
    Verify the filter days functionality by checking the default event start time in the GRID and the day name
    :return:
    """
    test = VeTestApi("test_guide_filter_days")
    test.begin(screen=test.screens.fullscreen)

    # Access to the Guide and retrieve the focused channel/event
    status = test.screens.guide.to_grid_days_filter_from_fullscreen()
    test.log_assert(status, "Failed to go to Grid days filter. Current screen: {0}".format(test.milestones.get_current_screen()))
    test.wait(CONSTANTS.SMALL_WAIT)

    NB_DAYS_WITH_EVENTS = 3
    for n in range(0, NB_DAYS_WITH_EVENTS):
        # Check the current day/month
        logging.info("Checking that filter day")
        calendar_day = datetime.utcnow() + timedelta(days=n)
        compare_filter_day_with_calendar(test, calendar_day)

        # Access to the grid
        status = test.screens.guide.navigate()
        test.log_assert(status, "Failed to go to Guide. Current screen: {0}".format(test.milestones.get_current_screen()))
        test.wait(CONSTANTS.GENERIC_WAIT)

        # Compare day's name display in the GRID and the calendar one
        compare_day_name_in_grid(test, calendar_day)

        # Compare current selected event date to the expected one (Grid)
        compare_event_date_with_grid_date(test, calendar_day)

        test.go_to_previous_screen()
        status = test.wait_for_screen(CONSTANTS.SCREEN_TIMEOUT, "main_hub")
        test.log_assert(status, "Failed to return to main_hub. Current screen: {0}".format(test.milestones.get_current_screen()))
        status = test.screens.main_hub.verify_main_hub_item_focused('GRID')
        test.log_assert(status, "Failure to come-back to GRID main_hub's item")
        test.wait(CONSTANTS.GENERIC_WAIT)
        test.move_towards('right')

    test.end()


@pytest.mark.non_regression
@pytest.mark.FS_Guide
@pytest.mark.LV_L3
def test_grid_missing_channel_logo():
    """
    Check that the channel is displayed in case of no channel logo is available
    :return:
    """
    ve_test = VeTestApi("test_actionmenu_missing_channel_logo")

    ve_test.begin(screen=ve_test.screens.fullscreen)

    status = ve_test.screens.fullscreen.navigate()
    ve_test.log_assert(status, "Hub timeout to fullscreen failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # Zap to a channel without logo
    channel_number = CONSTANTS.channel_number_without_logo
    logging.info("Zap to channel n %s" % channel_number)
    ve_test.screens.playback.dca(channel_number)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # Check that Channel name is displayed as no logo is available
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status, "Failed to be in Hub")

    status = ve_test.screens.main_hub.focus_item_in_hub(item_title='GRID')
    ve_test.log_assert(status, "Failed to focus Guide in Hub")
    status = ve_test.screens.guide.navigate()
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    ve_test.log_assert(status, "to_guide_from_hub failed")

    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status, logo = ve_test.get_channel_logo_display('focused_channel_info')
    logging.info("status: %s " % status)
    ve_test.log_assert(not status, "Channel logo is displayed and is not expected on this channel (%s)" % ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_channel_info'))
    status, channel_name = ve_test.get_channel_name_display('focused_channel_info')
    logging.info("status: %s " % status)
    ve_test.log_assert(status, "Channel name is not displayed and is expected on this channel (%s)." % ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_channel_info'))

    # Zap to a channel with logo
    channel_number = CONSTANTS.channel_number_classic_1
    ve_test.screens.playback.dca(channel_number)
    logging.info("Zap to channel n %s" % channel_number)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    # Check that Channel name is displayed as no logo is available
    status, logo = ve_test.get_channel_logo_display('focused_channel_info')
    ve_test.log_assert(status, "Channel logo is NOT displayed and is expected on this channel (%s)" % ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_channel_info'))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    ve_test.end()
