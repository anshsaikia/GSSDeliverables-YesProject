from tests_framework.ve_tests.assert_mgr import AssertMgr
from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
import pytest
import logging
import json


# ====================
# UTILITIES FUNCTIONS
# ====================

def check_action_menu_launch_fullscreen(ve_test):
    logging.info("Verify that ActionMenu can be launch by OK key press on 'fullscreen'")
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to launch the ActionMenu. Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(CONSTANTS.GENERIC_WAIT)


def check_go_to_fullscreen(ve_test):
    status = ve_test.screens.fullscreen.navigate()
    ve_test.log_assert(status, "Fail to go to 'fullscreen'")
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)
    # check that InfoLayer is dismissed else wait for dismiss
    status = ve_test.screens.fullscreen.wait_for_infolayer_dismiss(20)
    ve_test.log_assert(status, "Fail to dismiss the InfoLayer. Current screen: %s")

def check_go_to_guide(ve_test):
    status = ve_test.screens.guide.navigate()
    ve_test.log_assert(status, "Fail to go to Guide. Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(CONSTANTS.GENERIC_WAIT)


def check_go_to_timeline(ve_test):
    logging.info("Launch the timeline")
    status = ve_test.screens.timeline.navigate()
    ve_test.log_assert(status, "Fail to launch the Timeline. Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(CONSTANTS.GENERIC_WAIT)


def end_test(ve_test, test_name):
    ve_test.end()
    logging.info("##### End %s #####" % test_name)


def retrieve_ctap_info_fullscreen(ve_test):
    """
    Allow to retrieve the logo URL and the current event title for the currently played channel
    :return: The current channel logo and the current event title
    """
    logging.info("Retrieve CTAP info for the full screen")
    ctap_fullscreen_url = ve_test.he_utils.get_fullscreen_url()
    fullscreen_r = ve_test.he_utils.get_fullscreen_content_by_href(ctap_fullscreen_url)
    ctap_fullscreen_item = ve_test.he_utils.get_fullscreen_item_by_fullscreen(fullscreen_r["metadata"])

    ctap_channel_logo = ""
    ctap_event_title = ""
    for i in ctap_fullscreen_item[0]:
        if i == 'regularChannelLogo':
            ctap_channel_logo = ctap_fullscreen_item[0][i]
        if i == 'title':
            ctap_event_title = ctap_fullscreen_item[0][i]

    return ctap_channel_logo, ctap_event_title


def retrieve_fullscreen_info(ve_test):
    milestone = ve_test.milestones.getElements()
    live_channel_logo = ve_test.milestones.get_value_by_key(milestone, "cur_channel_logo")
    live_event_title = ve_test.milestones.get_value_by_key(milestone, "cur_event_title")
    return live_channel_logo, live_event_title


def check_infos_with_ctap(test_name,channel_logo,event_title,ctap_channel_logo,ctap_event_title,assertmgr, nb = 1):
    if channel_logo != ctap_channel_logo:
        status = False
        logging.info("Channel is not the ctap one => KO")
    else:
        status = True
        logging.info("Channel is the ctap one => OK")
    assertmgr.addCheckPoint(test_name, nb, status, "Failure on channelLogo. current: %s   ctap: %s " %(channel_logo, ctap_channel_logo))
    if event_title != ctap_event_title:
        status = False
        logging.info("Event title is the ctap one => KO")
    else:
        status = True
        logging.info("Event title is the ctap one => OK")
    assertmgr.addCheckPoint(test_name, nb+1, status, "Failure on event title. current: %s   ctap: %s " %(event_title, ctap_event_title))


def check_action_menu_logo_title(ve_test, expected_channel_logo, expected_event_title) :
    return ve_test.screens.action_menu.check_action_menu_logo_title(expected_channel_logo, expected_event_title)


def check_screen_on_back(ve_test, screen):
    logging.info("Check that '%s' is displayed on Back" % screen)
    ve_test.go_to_previous_screen()
    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, screen)
    ve_test.log_assert(status, "Fail to go back to %s. Current screen: %s" % (screen, ve_test.milestones.get_current_screen()))
    return status


def check_access_to_summary(ve_test, test_name, assertmgr, nb):
    logging.info("Action menu has Summary item")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status = ve_test.screens.action_menu.get_summary()
    assertmgr.addCheckPoint(test_name, nb, status, "Summary is not displayed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    return status


def check_store(ve_test):
    status = ve_test.screens.main_hub.navigate_to_store()
    ve_test.log_assert(status, "Fail to go to the store screen. Current screen: %s" % ve_test.milestones.get_current_screen())
    return status


def check_guide_info(ve_test, test_name, guide_channel_logo, guide_event_title, assertmgr, nb):
        milestone = ve_test.milestones.getElements()
        logging.info(json.dumps(milestone, indent=2))
        guide_back_channel_logo = get_focused_channel_logo(ve_test, milestone)
        guide_back_event_title = ve_test.milestones.get_value_by_key(milestone, "focused_event_title")
        if guide_channel_logo != guide_back_channel_logo:
            assertmgr.addCheckPoint(test_name, nb, False, "Fail to go back on Guide previously selected channel. Expected %s - Found %s" % (guide_channel_logo,guide_back_channel_logo))
        if guide_event_title != guide_back_event_title:
            assertmgr.addCheckPoint(test_name, nb+1, False, "Fail to go back on Guide previously selected event. Expected %s - Found %s" % (guide_event_title,guide_back_event_title))


def check_timeline_focused_channel(ve_test,test_name,timeline_channel_logo, timeline_event_title, assertmgr,nb):
        milestone = ve_test.milestones.getElements()
        if timeline_channel_logo != get_focused_channel_logo(ve_test, milestone):
            assertmgr.addCheckPoint(test_name, nb, False, "Fail to go back on Timeline previously selected channel")
        if timeline_event_title != ve_test.milestones.get_value_by_key(milestone, "focused_event_title"):
            assertmgr.addCheckPoint(test_name, nb+1, False, "Fail to go back on Timeline previously selected event")


def check_timeline_info(ve_test,timeline_channelLogo,timeline_eventTitle,test_name,assertmgr,nb = 3):
        milestone = ve_test.milestones.getElements()
        if timeline_channelLogo != get_focused_channel_logo(ve_test, milestone):
            assertmgr.addCheckPoint(test_name, 3, False, "Fail to go back on Timeline previously selected channel")
        if timeline_eventTitle != ve_test.milestones.get_value_by_key(milestone, "focused_event_title"):
            assertmgr.addCheckPoint(test_name, 4, False, "Fail to go back on Timeline previously selected event")


def check_day_focus(ve_test):
    elt = ve_test.milestones.getElements()
    dayOffset = ve_test.milestones.get_value_by_key(elt, "day_offset")
    ve_test.log_assert(dayOffset == 0, "dayOffset_now is not 0")
    current_state = ve_test.milestones.get_value_by_key(elt, "focus_state")
    logging.info("current_state %s" % current_state)
    ve_test.log_assert(int(current_state) == 1, "current state should be NOW")


def retrieve_guide_action_list(ve_test):
    audio_languages = ve_test.screens.action_menu.retrieve_audio_languages()
    audio_languages_list = ve_test.screens.action_menu.get_languages(audio_languages)
    if len(audio_languages_list) > 1:
        return CONSTANTS.actionlist_video_guide_current_event_audios
    else:
        return CONSTANTS.actionlist_video_guide_current_event


def go_back_fullscreen(ve_test):
    for _n in range(0, 10):
        ve_test.go_to_previous_screen()
        if ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen"):
            break
    else:
        ve_test.log_assert(False, "Fail to go back to fullscreen. Current screen: %s" % ve_test.milestones.get_current_screen())


def retrieve_live_action_list(ve_test):
    fullscreen_url = ve_test.he_utils.get_fullscreen_url()
    fullscreen_content = ve_test.he_utils.get_fullscreen_content_by_href(fullscreen_url)
    actionmenu_url = ve_test.screens.action_menu.get_action_menu_url(fullscreen_content["metadata"])
    return ve_test.screens.action_menu.retrieve_action_list(actionmenu_url)


def retrieve_fullscreen_action_list(ve_test, channel_number):
    service_id = ve_test.he_utils.get_serviceid_by_logical_channel_number(serviceDeliveryType="ABR",
                                                                               logical_channel_number=channel_number)
    ve_test.log_assert(service_id, "Failed to retrieve service_id for logical_channel_number: %s" % channel_number)
    # logging.info("\n\n ----> service_id: %s \n\n" % service_id)
    fullscreen_content = ve_test.he_utils.get_fullscreen_content_by_service_id(service_id=service_id)
    actionmenu_url = ve_test.screens.action_menu.get_action_menu_url(fullscreen_content["metadata"])
    # logging.info("----> actionmenu_url :%s" % actionmenu_url)
    return ve_test.screens.action_menu.retrieve_action_list(actionmenu_url)


def check_action_list(ve_test, actionitem_list):
    return ve_test.screens.action_menu.check_action_list(actionitem_list)


# ===================================================
#  TESTS
# ===================================================

@pytest.mark.non_regression
@pytest.mark.F_Live
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L2
@pytest.mark.ethernet
@pytest.mark.wifi
def test_actionmenu_launch_exit():
    """
    Verify that the Action can be launched from fullscreen by OK and exit by Back
    """
    test_name = "test_actionmenu_launch_exit"
    ve_test = VeTestApi(test_name)
    ve_test.begin(screen=ve_test.screens.main_hub)

    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)

    # Go to action menu
    check_action_menu_launch_fullscreen(ve_test)

    logging.info("Verify that ActionMenu can be exit by Back key press")
    status = ve_test.screens.fullscreen.navigate()
    ve_test.log_assert(status, "Fail to exit from ActionMenu on go back to fullscreen by Back. Current screen: %s" % ve_test.milestones.get_current_screen())

    end_test(ve_test, test_name)

@pytest.mark.non_regression
@pytest.mark.FS_ActionMenu
@pytest.mark.LV_L2
def test_actionmenu_launch_check_event():
    '''
    Verify that the ActionMenu is launched on current channel/current event
    '''
    test_name = "test_actionmenu_launch_check_event"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.main_hub)

    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)

    # Retrieve information from CTAP
    '''
    ctap_fullscreen_url = ve_test.he_utils.get_fullscreen_url()
    fullscreen_r = ve_test.he_utils.get_fullscreen_content_by_href(ctap_fullscreen_url)
    ctap_fullscreen_item = ve_test.he_utils.get_fullscreen_item_by_fullscreen(fullscreen_r)
    ctap_channel_logo = ""
    ctap_event_title = ""
    for i in ctap_fullscreen_item[0]:
        if i == 'regularChannelLogo':
            ctap_channel_logo = ctap_fullscreen_item[0][i]
        if i == 'title':
            ctap_event_title = ctap_fullscreen_item[0][i]
    '''
    ve_test.screens.fullscreen.wait_for_event_with_minimum_time_until_end()
    # Memorize live channel/event
    live_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "current_event_title")
    '''
    if live_channel_logo != ctap_channel_logo:
        status = False
    else:
        status = True
        logging.info("Live channel is the ctap one => OK")
    assertmgr.addCheckPoint("test_actiomenu_launch_check_event", 1, status, "Failure on channelLogo. live: %s   ctap: %s " %(live_channel_logo, ctap_channel_logo))
    if live_event_title != ctap_event_title:
        status = False
    else:
        status = True
        logging.info("Live event is the ctap one => OK")
    assertmgr.addCheckPoint("test_actiomenu_launch_check_event", 2, status, "Failure on event title. live: %s   ctap: %s " %(live_event_title, ctap_event_title))
    '''
    # Launch the Action Menu
    logging.info("Launch the Action Menu")
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to launch the ActionMenu. Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # check channel/event display
    am_event_title = ve_test.screens.action_menu.get_event_title()
    if am_event_title != live_event_title:
        status = False
    else:
        status = True
        logging.info("Action Menu event is the live one => OK")
    assertmgr.addCheckPoint("test_actiomenu_launch_check_event", 4, status, "Failure on event. live: %s  actionmenu: %s" % (live_event_title, am_event_title))

    logging.info("Check that fullscreen is displayed on Back")
    ve_test.go_to_previous_screen()
    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
    ve_test.log_assert(status, "Fail to go to fullscreen. Current screen: %s" % ve_test.milestones.get_current_screen())

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.F_Live
@pytest.mark.FS_ActionMenu
@pytest.mark.LV_L2
@pytest.mark.ethernet
@pytest.mark.wifi
def test_actionmenu_summary_access():
    '''
    Verify that the Summary can be displayed
    '''
    test_name = "test_actionmenu_summary_access"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.main_hub)

    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)

    # Go to action menu
    check_action_menu_launch_fullscreen(ve_test)

    # Retrieve information from CTAP
    '''
    ctap_fullscreen_url = ve_test.he_utils.get_fullscreen_url()
    fullscreen_r = ve_test.he_utils.get_fullscreen_content_by_href(ctap_fullscreen_url)
    logging.info("---> fullscreen_r: %s" %fullscreen_r)
    # Retrieve the Summary url
    ctap_fullscreen_item = ve_test.he_utils.get_fullscreen_item_by_fullscreen(fullscreen_r)
    logging.info("---> ctap_fullscreen_item: %s" % ctap_fullscreen_item)
    ctap_channel_logo = ""
    ctap_event_title = ""
    logging.info("---> ctap_fullscreen_item[0]: %s" % ctap_fullscreen_item[0])
    for i in ctap_fullscreen_item[0]:
        if i == 'regularChannelLogo':
            ctap_channel_logo = ctap_fullscreen_item[0][i]
        if i == 'title':
            ctap_event_title = ctap_fullscreen_item[0][i]
    '''
    logging.info("Access to Summary")
    check_access_to_summary(ve_test, test_name, assertmgr, 1)

    # Retrieve and check the summary text
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to go back to fullscreen. Current screen: %s" % ve_test.milestones.get_current_screen())

    ve_test.wait(2*CONSTANTS.GENERIC_WAIT)
    ve_test.screens.playback.dca(3)
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)
    # check that InfoLayer is dismissed else wait for dismiss
    status = ve_test.screens.fullscreen.wait_for_infolayer_dismiss(20)
    ve_test.log_assert(status, "Fail to dismiss the InfoLayer. Current screen: %s")

    logging.info("Verify that ActionMenu can be launch by OK key press on full screen")
    # Go to action menu
    check_action_menu_launch_fullscreen(ve_test)

    # Go to summary page
    logging.info("Access to Summary")
    check_access_to_summary(ve_test, test_name, assertmgr, 2)

    status = ve_test.screens.action_menu.navigate()
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    ve_test.log_assert(status, "Fail to go back to fullscreen. Current screen: %s" % ve_test.milestones.get_current_screen())

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.FS_Timeline
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_actionmenu_from_timeline_current_channel_future_event():
    """
    Check that the Action Menu can be launch over the timeline.
    Check the Back key management in this case (come-back to previous screen)
    """
    test_name = "test_actionmenu_from_timeline_current_channel_future_event"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.main_hub)

    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)

    # Go to the time line
    check_go_to_timeline(ve_test)

    # Check on current channel, future event
    # --------------------------------------
    logging.info("Select a future event then launch the Action Menu")
    for _n in range(0, 3):
        ve_test.move_towards('right', 0.2)

    # Memorize selected channel/event
    milestone = ve_test.milestones.getElements()
    timeline_channelLogo = get_focused_channel_logo(ve_test, milestone)
    timeline_eventTitle = ve_test.milestones.get_value_by_key(milestone, "focused_event_title")
    # launch the Action Menu
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to open the Action Menu. Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    # Do not perform the comparison in Dummy
    if not ve_test.is_dummy:
        status = check_action_menu_logo_title(ve_test, timeline_channelLogo,timeline_eventTitle)
        assertmgr.addCheckPoint(test_name, 1, status, "Action menu logo url or event title not valid. See log error messages")
        # Return to the time line screen
        logging.info("Check that Timeline is displayed on Back")
        check_screen_on_back(ve_test,"timeline")
        # check the same channel/event is selected back on the time line screen
        check_timeline_focused_channel(ve_test,test_name,timeline_channelLogo,timeline_eventTitle,assertmgr,2)
        # Come-back to fullscreen with the back key
        ve_test.wait(CONSTANTS.GENERIC_WAIT)
        status = ve_test.screens.fullscreen.navigate('back')
        ve_test.log_assert(status, "Fail to go back on fullscreen after Timeline->ActionMenu->Back->Back. Current screen: %s" % ve_test.milestones.get_current_screen())
    else:
        logging.info("Dummy mode. Check only that Fullscreen is displayed on Back")
        check_screen_on_back(ve_test,"fullscreen")

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.F_Timeline
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_actionmenu_from_timeline_other_channel_future_event():

    """
    Check that the Action Menu can be launch over the timeline.
    Check the Back key management in this case (come-back to previous screen)
    """
    test_name = "test_actionmenu_from_timeline_other_channel_future_event"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.main_hub)

    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)

    # Go to the time line
    check_go_to_timeline(ve_test)

    # Check on not current channel, future event
    # ------------------------------------------
    logging.info("Select another channel and a future event then launch the Action Menu")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    for _n in range(1, 4):
        ve_test.move_towards('down', CONSTANTS.SMALL_WAIT)
    for _n in range(0, 2):
        ve_test.move_towards('right', CONSTANTS.SMALL_WAIT)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # Memorize selected channel/event
    milestone = ve_test.milestones.getElements()
    timeline_channelLogo = get_focused_channel_logo(ve_test, milestone)
    timeline_eventTitle = ve_test.milestones.get_value_by_key(milestone, "focused_event_title")
    # Launch the Action Menu
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to open the Action Menu. Current screen: %s" % ve_test.milestones.get_current_screen())
    # check channel/event display
    # Do not check in Dummy
    if not ve_test.is_dummy:
        status = check_action_menu_logo_title(ve_test, timeline_channelLogo,timeline_eventTitle)
        assertmgr.addCheckPoint(test_name, 1, status, "Action menu logo url or event title not valid. See log error messages")
        logging.info("Check that Timeline is displayed on Back")
        check_screen_on_back(ve_test,"timeline")
        # check channel/event selected
        check_timeline_info(ve_test,timeline_channelLogo,timeline_eventTitle,test_name,assertmgr,2)
        # Come-back to fullscreen
        ve_test.wait(CONSTANTS.GENERIC_WAIT)
        status = ve_test.screens.fullscreen.navigate('back')
        ve_test.log_assert(status, "Fail to go back on fullscreen after Timeline->ActionMenu->Back->Back. Current screen: %s" % ve_test.milestones.get_current_screen())

    else:
        check_screen_on_back(ve_test,"fullscreen")

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


def show_guide(ve_test):
    ve_test.begin(screen=ve_test.screens.main_hub)
    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)
    # Access to the grid
    check_go_to_guide(ve_test)
    # check the current day offset is 0, and check different focus state
    check_day_focus(ve_test)


def check_guide_action_menu_and_back(ve_test, guide_channel_logo, guide_event_title, assertmgr, test_name):
    if not ve_test.is_dummy:
        status = check_action_menu_logo_title(ve_test, guide_channel_logo, guide_event_title)
        assertmgr.addCheckPoint(test_name, 1, status, "Action menu logo url or event title not valid. See log error messages")
        logging.info("Check that Grid is displayed on Back")
        check_screen_on_back(ve_test, "guide")
        # check channel/event selected
        check_guide_info(ve_test, test_name, guide_channel_logo, guide_event_title, assertmgr, 2)

    logging.info('Come-back to full screen')

    go_back_fullscreen(ve_test)

def get_focused_channel_logo(ve_test, milestone):
    guide_channel_info = ve_test.milestones.get_value_by_key(milestone, "focused_channel_info")
    return guide_channel_info["logo"]


@pytest.mark.non_regression
@pytest.mark.F_Guide
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_grid
def test_actionmenu_in_guide_current_event_current_channel():
    """
    Check that the Action Menu can be launch over the grid.
    Check the Back key management in this case (come-back to previous screen)
    """
    test_name = "test_actionmenu_in_guide_current_event_current_channel"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)

    show_guide(ve_test)

    # Check on current channel, current event
    # ---------------------------------------
    # Memorize selected channel/event
    milestone = ve_test.milestones.getElements()
    guide_channel_logo = get_focused_channel_logo(ve_test, milestone)
    guide_event_title = ve_test.milestones.get_value_by_key(milestone, "focused_event_title")
    # launch the Action Menu
    status = ve_test.screens.action_menu.navigate()
    assertmgr.addCheckPoint(test_name, 2, status, "Fail to open the Action Menu")
    # check channel/event display
    check_guide_action_menu_and_back(ve_test, guide_channel_logo, guide_event_title, assertmgr, test_name)

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.F_Guide
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_grid
def test_actionmenu_in_guide_future_event_current_channel():
    """
    Check that the Action Menu can be launch over the grid.
    Check the Back key management in this case (come-back to previous screen)
    """
    test_name = "test_actionmenu_in_guide_future_event_current_channel"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)

    ve_test.begin(screen=ve_test.screens.main_hub)
    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)
    # Waiting that current event duration is enough to perform test
    ve_test.screens.fullscreen.wait_for_event_with_minimum_time_until_end()
    # Access to the grid
    check_go_to_guide(ve_test)
    # check the current day offset is 0, and check different focus state
    check_day_focus(ve_test)

    # Check on current channel, future event
    # --------------------------------------
    logging.info("Select current channel and the future event then launch the Action Menu")
    ve_test.move_towards('right', CONSTANTS.SMALL_WAIT)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    milestone = ve_test.milestones.getElements()
    ve_test.log_assert(ve_test.milestones.get_value_by_key(milestone, "focus_state") == 2, "current state should be NEXT")

    # Memorize selected channel/event
    guide_channel_logo = get_focused_channel_logo(ve_test, milestone)
    guide_event_title = ve_test.milestones.get_value_by_key(milestone, "focused_event_title")
    logging.info("BEFORE Action Menu launch: guide_event_title: %s  guide_channel_logo: %s " % (guide_event_title, guide_channel_logo))
    # Launch the Action Menu
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to open the Action Menu from Guide")
    # check channel/event display
    check_guide_action_menu_and_back(ve_test, guide_channel_logo, guide_event_title, assertmgr, test_name)

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.F_Guide
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_actionmenu_in_guide_current_event_other_channel():
    """
    Check that the Action Menu can be launch over the grid.
    Check the Back key management in this case (come-back to previous screen)
    """
    test_name = "test_actionmenu_in_guide_current_event_other_channel"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)

    show_guide(ve_test)

    # Check on not current channel, current event
    # -------------------------------------------
    logging.info("Select another channel and the current event then launch the Action Menu")
    for _n in range(1, 5):
        ve_test.move_towards('down', CONSTANTS.SMALL_WAIT)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # Memorize selected channel/event
    milestone = ve_test.milestones.getElements()
    guide_channel_logo = get_focused_channel_logo(ve_test, milestone)
    guide_event_title = ve_test.milestones.get_value_by_key(milestone, "focused_event_title")
    # Launch the Action Menu
    status = ve_test.screens.action_menu.navigate()
    assertmgr.addCheckPoint("test_actionmenu_in_guide_current_event_other_channel", 2, status, "Fail to open the Action Menu")
    # check channel/event display
    check_guide_action_menu_and_back(ve_test, guide_channel_logo, guide_event_title, assertmgr, test_name)

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.F_Guide
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_actionmenu_in_guide_future_event_other_channel():
    """
    Check that the Action Menu can be launch over the grid.
    Check the Back key management in this case (come-back to previous screen)
    """
    test_name = "test_actionmenu_in_guide_future_event_other_channel"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)

    show_guide(ve_test)

    # Check on not current channel, future event
    # ------------------------------------------
    logging.info("Select another channel and a future event then launch the Action Menu")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    for _n in range(1, 2):
        ve_test.screens.guide.to_nextchannel_in_guide('down')
    ve_test.move_towards('right', CONSTANTS.SMALL_WAIT)

    # Memorize selected channel/event
    milestone = ve_test.milestones.getElements()
    guide_channel_logo = get_focused_channel_logo(ve_test, milestone)
    guide_event_title = ve_test.milestones.get_value_by_key(milestone,"focused_event_title")
    # Launch the Action Menu
    status = ve_test.screens.action_menu.navigate()
    assertmgr.addCheckPoint(test_name, 2, status, "Fail to open the Action Menu")

    # check channel/event display
    check_guide_action_menu_and_back(ve_test, guide_channel_logo, guide_event_title, assertmgr, test_name)

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.F_Live
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L2
@pytest.mark.ethernet
@pytest.mark.wifi
def test_actionmenu_actionlist_cyclic():
    """
    Verify that the actions list is circular
    """
    test_name = "test_actionmenu_actionlist_cyclic"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.main_hub)

    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)

    # Launch the Action Menu
    check_action_menu_launch_fullscreen(ve_test)

    # Navigate in loop in up direction
    first_selected_item = ve_test.screens.action_menu.get_focused_item()
    # Check all action list item
    ve_test.move_towards('up')
    selected_item = ve_test.screens.action_menu.get_focused_item()
    if selected_item != first_selected_item:
        for _nb in range(1, 10):
                ve_test.move_towards('up')
                selected_item = ve_test.screens.action_menu.get_focused_item()
                if selected_item == first_selected_item:
                    # loop is done
                    break
        else:
            assertmgr.addCheckPoint(test_name, 1, False, "no loop on first item")
    else:
        assertmgr.addCheckPoint(test_name, 2, False, "missing items")

    # Navigate in loop in down direction
    first_selected_item = ve_test.screens.action_menu.get_focused_item()
    # Check all action list item
    ve_test.move_towards('down')
    selected_item = ve_test.screens.action_menu.get_focused_item()
    if selected_item != first_selected_item:
        for _nb in range(1, 10):
            ve_test.move_towards('down')
            selected_item = ve_test.screens.action_menu.get_focused_item()
            if selected_item == first_selected_item:
                # loop is done
                break
        else:
            assertmgr.addCheckPoint(test_name, 3, False, "no loop on first item")
    else:
        assertmgr.addCheckPoint(test_name, 4, False, "missing items")

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.F_Live
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L2
@pytest.mark.ethernet
@pytest.mark.wifi
def test_actionmenu_in_live_actionlist_audio_actions():
    """
    Verify the audio focus and selection in Language action menu
    """
    test_name = "test_actionmenu_in_live_actionlist_audio_actions"
    ve_test = VeTestApi(title=test_name)
    ve_test.begin(screen=ve_test.screens.main_hub)

    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)
    ve_test.screens.playback.dca(CONSTANTS.channel_number_with_several_audio)
    ve_test.wait(CONSTANTS.SCREEN_TIMEOUT)
    check_action_menu_launch_fullscreen(ve_test)

    # Check all action list items
    if ve_test.is_dummy:
        action_item_list = CONSTANTS.dummy_actionlist_video_live_current_event
    else:
        action_item_list = retrieve_fullscreen_action_list(ve_test, CONSTANTS.channel_number_with_several_audio)
        logging.info("--> action_item_list: %s" % action_item_list)

    status = check_action_list(ve_test, action_item_list)
    ve_test.log_assert(status, "Status of first action menu check")

    go_back_fullscreen(ve_test)
    check_go_to_fullscreen(ve_test)
    check_action_menu_launch_fullscreen(ve_test)

    logging.info("--> Search for Languages action")
    nb_audio_items = ve_test.screens.action_menu.get_menu_nb_audio()
    ve_test.log_assert(nb_audio_items > 1, "No audio items in sub-menu")
    logging.info("======> nb_audio_items: %s" % nb_audio_items)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    for n in range(1, nb_audio_items + 1):
        logging.info("======> n: %s" % n)
        # Navigate to language menu
        status = ve_test.screens.action_menu.navigate_to_action(CONSTANTS.A_LANGUAGE)
        ve_test.wait(CONSTANTS.GENERIC_WAIT)
        first_focused_item = ve_test.screens.action_menu.get_focused_item()
        current_focused_language = ve_test.screens.action_menu.get_focused_asset()
        logging.info("======> first_focused_item: %s   current_focused_language: %s" % (first_focused_item, current_focused_language))

        if n != 1:
            ve_test.wait(CONSTANTS.SMALL_WAIT)
            ve_test.move_towards('right')
            ve_test.wait(CONSTANTS.SMALL_WAIT)

        current_focused_language = ve_test.screens.action_menu.get_focused_asset()
        logging.info("======>  new selected language: %s" % current_focused_language)
        # Select next audio language in sub-menu
        ve_test.validate_focused_item(CONSTANTS.SMALL_WAIT)
        ve_test.wait(5)

        logging.info("--> go back to fullscreen")
        go_back_fullscreen(ve_test)
        check_go_to_fullscreen(ve_test)
        ve_test.wait(CONSTANTS.GENERIC_WAIT)

        check_action_menu_launch_fullscreen(ve_test)

        # Check all action list items
        if ve_test.is_dummy:
            action_item_list = CONSTANTS.dummy_actionlist_video_live_current_event
        else:
            action_item_list = retrieve_fullscreen_action_list(ve_test, CONSTANTS.channel_number_with_several_audio)

        logging.info("action_item_list : %s" % action_item_list)
        status = check_action_list(ve_test, action_item_list)
        ve_test.log_assert(status, "Status of action menu loop %s check" % n)

        go_back_fullscreen(ve_test)
        check_go_to_fullscreen(ve_test)
        ve_test.wait(CONSTANTS.SCREEN_TIMEOUT)
        check_action_menu_launch_fullscreen(ve_test)

    ve_test.end()


@pytest.mark.non_regression
@pytest.mark.F_Live
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L2
@pytest.mark.ethernet
@pytest.mark.wifi
def test_actionmenu_in_fullscreen_actionlist_live_video():
    """
    Verify that the actions available on current event when ActionMenu is launch from the fullscreen
    """
    test_name = "test_actionmenu_in_fullscreen_actionlist_live_video"
    ve_test = VeTestApi(title=test_name)
    ve_test.begin(screen=ve_test.screens.main_hub)

    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)
    channel = 1
    ve_test.screens.playback.dca(channel)
    ve_test.wait(CONSTANTS.SCREEN_TIMEOUT)
    ve_test.screens.fullscreen.wait_for_event_with_minimum_time_until_end()

    if ve_test.is_dummy:
        action_item_list = CONSTANTS.dummy_actionlist_video_live_current_event
    else:
        action_item_list = retrieve_fullscreen_action_list(ve_test, channel)

    check_action_menu_launch_fullscreen(ve_test)

    # Check all action list items
    status = check_action_list(ve_test, action_item_list)
    logging.info("Status : %s" % str(status))
    ve_test.log_assert(status, "Action item list not valid. See log error messages")

    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.F_Guide
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_actionmenu_in_guide_actionlist_live_video_current_channel():
    """
    Verify that the actions available on current event when ActionMenu is launch from the Guide
    """
    test_name = "test_actionmenu_in_guide_actionlist_live_video_current_channel"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.main_hub)

    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)
    channel = 1
    ve_test.screens.playback.dca(channel)
    ve_test.wait(CONSTANTS.SCREEN_TIMEOUT)

    # Access to the grid
    check_go_to_guide(ve_test)

    # Launch the Action Menu on current channel/event
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to open the Action Menu. Current screen: %s" % ve_test.milestones.get_current_screen())

    # Check all action list items
    if ve_test.is_dummy:
        action_item_list = CONSTANTS.dummy_actionlist_video_live_current_event
    else:
        action_item_list = retrieve_guide_action_list(ve_test)

    status = check_action_list(ve_test, action_item_list)
    assertmgr.addCheckPoint(test_name, 1, status, "Action item list not valid. See log error messages")

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.F_Guide
@pytest.mark.FS_ActionMenu
@pytest.mark.LV_L2
def test_actionmenu_in_guide_actionlist_live_video_other_channel():
    """
    Verify that the actions available on current event when ActionMenu is launch from the Guide
    """
    test_name = "test_actionmenu_in_guide_actionlist_live_video_other_channel"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.main_hub)

    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)

    # Access to the grid
    check_go_to_guide(ve_test)

    selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_event_title')
    logging.info('Selected event: %s' % selected_event_title)

    # Navigate to another channel
    logging.info("Select another channel then launch the Action Menu")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    for _n in range(1, 3):
        ve_test.screens.guide.to_nextchannel_in_guide('down')
        new_ev = str(ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_event_title'))
        if selected_event_title != new_ev:
            break
    logging.info('New selected event: %s' %(new_ev))

    guide_channel_number = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_channel_number')
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to open the Action Menu. Current screen: %s" % ve_test.milestones.get_current_screen())

    action_item_list = CONSTANTS.actionlist_video_live_current_event_other_channel


    # Check all action list item
    status = check_action_list(ve_test,action_item_list)
    assertmgr.addCheckPoint(test_name, 1, status, "Action item list not valid. See log error messages")

    # Check that Play do the expected zapping
    ve_test.move_towards('up')
    selected_item = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_item")
    if selected_item != CONSTANTS.actionlist_video_live_current_event_other_channel[1]:
        assertmgr.addCheckPoint(test_name, 4, False, "No Play item")
        logging.info("No Play item: focused_item = (%s)"%(selected_item))
    ve_test.validate_focused_item(CONSTANTS.GENERIC_WAIT)

    status = ve_test.screens.fullscreen.wait_for_infolayer_dismiss(CONSTANTS.WAIT_TIMEOUT)
    ve_test.log_assert(status, "Fail to dismiss the InfoLayer. Current screen: %s")

    milestone = ve_test.milestones.getElements()
    live_channel = ve_test.milestones.get_value_by_key(milestone,'current_channel')
    if live_channel != guide_channel_number:
        assertmgr.addCheckPoint(test_name, 5, False, "Not correct channel playing on Play. no %s instead of no %s" % (live_channel, guide_channel_number ))

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.FS_ActionMenu
@pytest.mark.LV_L2
def test_actionmenu_in_guide_actionlist_future_event_current_channel():
    """
    Verify that the actions available on future event, current channel when ActionMenu is launch from the guide
    """
    test_name="test_actionmenu_in_guide_actionlist_future_event_current_channel"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.main_hub)

    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)

    # Access to the grid
    check_go_to_guide(ve_test)

    selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_event_title')
    logging.info('Selected event: %s' % selected_event_title)

    # Future event on current channel
    logging.info("Select a future event")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    ve_test.move_towards('right')
    selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_event_title')
    if selected_event_title == False:
        logging.info('No future event on this channel')

    # Future event on current channel
    logging.info("Select a future event")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    ve_test.move_towards('right')
    selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_event_title')
    if selected_event_title == False:
        logging.info('No future event on this channel')
        ve_test.log_assert(False, "Fail to find future event on current channel")

    # Open the Action Menu
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to open the Action Menu. Current screen: %s" % ve_test.milestones.get_current_screen())
    selected_item = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focused_action")
    logging.info('focused item is %s' % selected_item)

    actionitem_list = CONSTANTS.actionlist_video_live_future_event

    # Check all action list item
    status = check_action_list(ve_test,actionitem_list)
    assertmgr.addCheckPoint(test_name, 1, status, "Action item list not valid. See log error messages")

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.FS_ActionMenu
@pytest.mark.LV_L3
def test_actionmenu_in_guide_actionlist_future_event_other_channel():
    """
    Verify that the actions when same event is currently broadcast on two different channels
    """
    test_name = "test_actionmenu_in_guide_actionlist_future_event_other_channel"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.main_hub)

    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)

    # Access to the grid
    check_go_to_guide(ve_test)

    selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_event_title')
    logging.info('Selected event: %s' % selected_event_title)

    # Select another channel
    ve_test.screens.guide.to_nextchannel_in_guide('down')

    logging.info("Select a future event")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    ve_test.move_towards('right')
    selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_event_title')

    if selected_event_title == False:
        logging.info('No future event on this channel')
        # Navigate to another channel in order to find a future event
        ve_test.wait(CONSTANTS.GENERIC_WAIT)
        for _n in range(1, 20):
            if ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_event_title') != False:
                break
        else:
            ve_test.log_assert(False, "Fail to go to find a future event")

    # Open the Action Menu
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to open the Action Menu. Current screen: %s" % ve_test.milestones.get_current_screen())

    selected_item = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focused_action")
    logging.info('focused item is %s' % selected_item)

    actionitem_list = CONSTANTS.actionlist_video_live_future_event

    # Check all action list item
    status = check_action_list(ve_test,actionitem_list)
    assertmgr.addCheckPoint(test_name, 1, status, "Action item list not valid. See log error messages")

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)

def show_timeline(ve_test):
    ve_test.begin(screen=ve_test.screens.main_hub)

    # Go to Initial Conditions: fullscreen
    check_go_to_fullscreen(ve_test)

    # Access to the timeline
    status = ve_test.screens.timeline.navigate('right')
    ve_test.log_assert(status, "Fail to go to Timeline. Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_event_title')
    logging.info('Selected event: %s' % selected_event_title)
    return selected_event_title


@pytest.mark.non_regression
@pytest.mark.FS_ActionMenu
@pytest.mark.LV_L2
def test_actionmenu_in_timeline_actionlist_future_event_current_channel():
    """
    Verify that the actions on future event in the Timeline (current channel)
    """
    test_name = "test_actionmenu_in_timeline_actionlist_future_event_current_channel"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)

    _selected_event_title = show_timeline(ve_test)

    logging.info("Select a future event")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    ve_test.move_towards('right')
    selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_event_title')
    if selected_event_title == False:
        logging.info('No future event on this channel')
        ve_test.log_assert(False, "Fail to go to find a future event on current channel")

    # Open the Action Menu
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to open the Action Menu. Current screen: %s" % ve_test.milestones.get_current_screen())

    # Check all action list item
    status = check_action_list(ve_test,CONSTANTS.actionlist_video_live_future_event)
    assertmgr.addCheckPoint(test_name, 1, status, "Action item list not valid. See log error messages")

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.FS_ActionMenu
@pytest.mark.LV_L2
def test_actionmenu_in_timeline_actionlist_future_event_other_channel():
    """
    Verify that the actions on future event in the Timeline (not current channel)
    """
    test_name = "test_actionmenu_in_timeline_actionlist_future_event_other_channel"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)

    _selected_event_title = show_timeline(ve_test)

    logging.info("Select another channel")
    ve_test.move_towards('down')
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    # check if future event is available
    ve_test.move_towards('right')
    selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_event_title')
    if selected_event_title == False:
        logging.info('No future event on this channel')
        for _nb_channel in range(1, 10):
            ve_test.move_towards('down')
            ve_test.wait(CONSTANTS.GENERIC_WAIT)
            # check if future event is available
            ve_test.move_towards('right')
            selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_event_title')
            if selected_event_title == False:
                    logging.info('No future event on this channel')
        else:
            logging.info('No future event on this channel')
            ve_test.log_assert(False, "Fail to go to find a future event on another channel")

    # Open the Action Menu
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to open the Action Menu. Current screen: %s" % ve_test.milestones.get_current_screen())

    # Check all action list item
    status = check_action_list(ve_test,CONSTANTS.actionlist_video_live_future_event)
    assertmgr.addCheckPoint(test_name, 1, status, "Action item list not valid. See log error messages")

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_action
def test_actionmenu_in_hub_showcase_vod_asset():
    """
    Verify that the actions menu when launch from hub showcase
    """
    test_name = "test_actionmenu_in_hub_showcase_vod_asset"
    ve_test = VeTestApi(title="")
    assertmgr = AssertMgr(ve_test)

    ve_test.begin(screen=ve_test.screens.fullscreen)
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    # Access to the showcase
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status, "Fail to launch the Hub. Current screen: %s" % ve_test.milestones.get_current_screen())

    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    # Select a non linear event
    # Access to Store then down to have the first VOD item
    # No Library today
    status = ve_test.screens.main_hub.focus_store_item_in_hub()
    ve_test.log_assert(status, "Failed to focus store showcase")

    # Retrieve selected asset then launch the Action Menu
    selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_asset')
    logging.info("selected_event_title to launch action menu: '%s'"%(selected_event_title))
    if selected_event_title == False:
        ve_test.log_assert('No event selected')
    status = ve_test.screens.action_menu.navigate()      # key_pad_center -> go into the default store asset
    ve_test.log_assert(status, "Fail to open the Action Menu. Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # check event title display'
    logging.info("Check the Event displayed")
    am_event_title = ve_test.screens.action_menu.get_event_title()
    # Do not perform the comparaison in Dummy
    if not ve_test.is_dummy:
        logging.info("event_title: '%s'  (%s) "%(am_event_title,selected_event_title))
        if am_event_title != selected_event_title:
            assertmgr.addCheckPoint("test_actionmenu_in_hub_showcase_vod_asset", 1, False, "Action Menu %s is not launch on selected event %s" %(am_event_title, selected_event_title))


    # Check Actions List
    logging.info("Check the Actions List")
    #if ve_test.is_dummy:
    #    action_item_list = CONSTANTS.actionlist_vod_event
    #else:
    #    action_item_list = CONSTANTS.actionlist_vod_event
    action_item_list = ve_test.screens.action_menu.get_actions_from_current_actionmenu()

    # Check all action list item
    status = check_action_list(ve_test,action_item_list)
    assertmgr.addCheckPoint(test_name, 2, status, "Action item list not valid. See log error messages")

    if not ve_test.is_dummy:
        # Check access to Summary
        logging.info("Access to the Summary")
        check_access_to_summary(ve_test, test_name, assertmgr, 3)

        logging.info("Check that main hub is displayed on Back")
        ve_test.go_to_previous_screen()
        back_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_asset')
        status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "main_hub")
        if not status:
            assertmgr.addCheckPoint("test_actionmenu_in_hub_showcase_vod_asset", 5, status, "Failed to come-back on main hub")
        logging.info("In main_hub")

        
        if back_event_title == False:
            assertmgr.addCheckPoint("test_actionmenu_in_hub_showcase_vod_asset", 6, False, "Failed to come-back on main hub 's selected asset")
        if back_event_title != selected_event_title:
            assertmgr.addCheckPoint("test_actionmenu_in_hub_showcase_vod_asset", 7, False, "Failed to have the same asset selected in main hub on come-back")

    assertmgr.verifyAllCheckPoints()
    ve_test.end()


@pytest.mark.non_regression
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L2
def test_actionmenu_in_fullcontent_vod_asset():
    """
    Verify that the actions menu when launch from fullcontent
    """
    test_name = "test_actionmenu_in_fullcontent_vod_asset"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)
    ctap_assets_list = []

    ve_test.begin(screen=ve_test.screens.main_hub)

    status = ve_test.screens.main_hub.navigate_to_store()
    assertmgr.addCheckPoint(test_name, 1, status, "Fail to go to Store")
    #go in fullcontent
    if ve_test.is_dummy:
        status, classification_id = ve_test.screens.fullcontent.navigate(filter_path = ("FILMS", "GENRES", "DRAMA"))
        assertmgr.addCheckPoint(test_name, 2, status, "Fail to go to FullContent")
    else:
        category = "GENRES"
        sub_category = "DRAMA"
        status = ve_test.screens.filter.focus_item_in_filterscreen_ux(category)
        ve_test.log_assert(status, "Fail to go to %s" % category)
        ve_test.wait(CONSTANTS.GENERIC_WAIT)
        status = ve_test.screens.filter.select_sub_item_in_filterscreen_ux(sub_category)
        assertmgr.addCheckPoint(test_name, 2, status, "Fail to go to FullContent")
        classification_id = ve_test.screens.filter.get_classification_id(filter_path = ("GENRES", "DRAMA"))
        if status is not False and classification_id is not "":
            ctap_assets_list = ve_test.he_utils.get_content_list_from_classificationId(classification_id)

    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)
	
    # sort alphabetically
    ve_test.repeat_key_press("KEYCODE_DPAD_UP", 1, 2)	
    ve_test.repeat_key_press("KEYCODE_DPAD_RIGHT", 2, 2)	
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 2)	
    ve_test.repeat_key_press("KEYCODE_DPAD_DOWN", 1, 2)	

    # Retrieve selected asset then launch the Action Menu
    selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'selected_item')
    if selected_event_title == False:
        ve_test.log_assert('No event selected')
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to open the Action Menu on %s" % selected_event_title)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # check event title display'
    am_event_title = ve_test.screens.action_menu.get_event_title()
    logging.info("Check the Event displayed (%s)"%(am_event_title))

    if not ve_test.is_dummy:
        if am_event_title != selected_event_title:
            assertmgr.addCheckPoint(test_name, 3, False, "Action Menu %s is not launch on selected event %s" %(am_event_title, selected_event_title))

        # Check title is in Ctap_asset_list
        ctap_selected_asset = {}
        nb_assets = len(ctap_assets_list)
        num_asset = 0
        for asset in ctap_assets_list:      # ctap_assets_list is a list of assets which are dictionnaries
            num_asset +=1
            logging.info("%d/%d) asset['title']: %s" %(num_asset,nb_assets, asset['title']))
            logging.info('\n')
            if asset['title'] == am_event_title:
                ctap_selected_asset = asset
                logging.info("ctap_selected_asset: %s" % (ctap_selected_asset['title']))
                break
        # Check Action Menu short summary

        # Check the Action list
        # Retrieve Actions from CTAP
        if ctap_selected_asset.has_key('id'):
            logging.info("----> ctap_selected_asset['id']: %s " %(ctap_selected_asset['id']))
            ctap_action_menu_resp = ve_test.he_utils.get_actiomenu_by_content_id(ctap_selected_asset['id'])
            ctap_action_title_list = ve_test.screens.action_menu.retrieve_action_list_from_content(ctap_action_menu_resp)
        else:
            logging.info("----> ctap_selected_asset does not have id")
            ctap_action_title_list =[""]      # when error create empty list to don't crash
        # Check all action list item
        status = check_action_list(ve_test,ctap_action_title_list)
        assertmgr.addCheckPoint(test_name, 1, status, "Action item list not valid. See log error messages")

        # Check access to Summary
        logging.info("Access to the Summary")
        check_access_to_summary(ve_test, test_name, assertmgr, 7)

        logging.info("Check that full_content is displayed on Back")
        check_screen_on_back(ve_test,"full_content")
        logging.info("In full_content")

        back_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'selected_item')
        if back_event_title == False:
            assertmgr.addCheckPoint(test_name, 10, status, "Failed to come-back on full_content 's selected asset")
        if back_event_title != selected_event_title:
            assertmgr.addCheckPoint(test_name, 11, status, "Failed to have the same asset (%s) selected in full_content (%s) on come-back"%(selected_event_title,back_event_title))


    # In Dummy
    else:
        # Check Actions List
        logging.info("Check the Actions List")
        status = check_action_list(ve_test,CONSTANTS.actionlist_vod_event)
        assertmgr.addCheckPoint(test_name, 1, status, "Action item list not valid. See log error messages")

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L2
def test_actionmenu_in_filter_vod_asset():
    """
    Verify that the actions menu when launch from filter
    """
    test_name = "test_actionmenu_in_filter_vod_asset"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)
    classification_id = ""
    ctap_assets_list = []
    ve_test.begin(screen=ve_test.screens.main_hub)

    status = ve_test.screens.main_hub.focus_item_in_hub(item_title='STORE')
    assertmgr.addCheckPoint(test_name, 1, status, "Fail to go to Store")
    # go in filter leaf
    if ve_test.is_dummy:
        status, classification_id = ve_test.screens.filter.to_filter_leaf_from_filter(filter_path = ("FILMS", "RECOMMENDED"))
        assertmgr.addCheckPoint(test_name, 2, status, "Fail to go to Filter RECOMMENDED")
    else:
        classification_id = ve_test.screens.filter.get_root_classification_id("RECOMMENDED")
        assertmgr.addCheckPoint(test_name, 2, status, "Fail to go to Filter leaf")
        if status is not False and classification_id is not "":
            ctap_assets_list = ve_test.he_utils.get_content_list_from_classificationId(classification_id) # request to CMDC
            logging.info("on filter leaf, got %d assets in list"%(len(ctap_assets_list)))       # we are on filter screen
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    # Retrieve selected asset then launch the Action Menu
    selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_asset')
    if selected_event_title == False:
        ve_test.log_assert('No event selected')
    logging.info("Launch the Action Menu")
    
    #status = test.to_actionmenu_from_filter()  # may need to go on full content and after on action menu
    ve_test.validate_focused_item(2)               # may be on full content, may be on action menu ...
    if ve_test.milestones.get_current_screen() == "full_content": # must entering to first asset to have action_menu
        selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'selected_item')
        by_fullcontent = True                       # notify an additionnal move
        ve_test.validate_focused_item(2)
    else:
        by_fullcontent = False
    
    ve_test.log_assert(status, "Fail to open the Action Menu on '%s' from filter leaf" % (selected_event_title))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # check event title display
    logging.info("Check the Event displayed")
    am_event_title = ve_test.screens.action_menu.get_event_title()

    if not ve_test.is_dummy:
        if am_event_title != selected_event_title:
            assertmgr.addCheckPoint(test_name, 3, False, "Action Menu %s is not launch on selected event %s" %(am_event_title, selected_event_title))
        # Check title is in Ctap_asset_list
        ctap_selected_asset = {}
        for asset in ctap_assets_list:      # ctap_assets_list is a list of assets which are dictionnaries
            logging.info("asset['title']: %s" % asset['title'])
            logging.info('\n')
            if asset['title'] == am_event_title:
                ctap_selected_asset = asset
                logging.info("ctap_selected_asset: %s" % ctap_selected_asset)
                break
        # Check Action Menu short summary

        # Check the Action list
        # Retrieve Actions from CTAP
        if ctap_selected_asset.has_key('id'):
            logging.info("----> ctap_selected_asset['id']: %s " %(ctap_selected_asset['id']) )
            ctap_action_menu_resp = ve_test.he_utils.get_actiomenu_by_content_id(ctap_selected_asset['id'])
            ctap_action_title_list = ve_test.screens.action_menu.retrieve_action_list_from_content(ctap_action_menu_resp)
        else:
            ctap_action_title_list =[""]      # when error create empty list to don't crash

        status = check_action_list(ve_test, ctap_action_title_list)
        assertmgr.addCheckPoint(test_name, 5, status, "Action item list not valid. See log error messages")

        # Check access to Summary
        logging.info("Access to the Summary")
        check_access_to_summary(ve_test, test_name, assertmgr, 7)

        logging.info("Check that filter is displayed on Back")
        ve_test.go_to_previous_screen()        #  action menu --> full_content/filter/main_hub
        back_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_asset')
        if by_fullcontent:
            ve_test.go_to_previous_screen()    #  full_content --> main_hub (which is a filter)
        status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "main_hub")
        if not status:
            assertmgr.addCheckPoint(test_name, 9, status, "Failed to come-back on main_hub/filter")
        logging.info("In main_hub/filter")

        
        if back_event_title == False:
            assertmgr.addCheckPoint(test_name, 10, status, "Failed to come-back on main_hub/filter's selected asset")
        if back_event_title != selected_event_title:
            assertmgr.addCheckPoint(test_name, 11, status, "Failed to have the same asset selected in filter on come-back")

    # In Dummy
    else:
        logging.info("In duumy - Check the Actions List")
        status = check_action_list(ve_test,CONSTANTS.actionlist_vod_event)
        assertmgr.addCheckPoint(test_name, 5, status, "Action item list not valid. See log error messages")

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test, test_name)


@pytest.mark.non_regression
@pytest.mark.FS_ActionMenu
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_actionmenu_in_search_vod_asset():
    """
    Verify that the actions menu when launch from a VOD search result
    """
    test_name = "test_actionmenu_in_search_vod_asset"
    ve_test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.main_hub)

    status = ve_test.screens.main_hub.navigate_to_store()
    assertmgr.addCheckPoint(test_name, 1, status, "Fail to go to Store. Current screen: %s" % ve_test.milestones.get_current_screen())
    # go to Search
    status = ve_test.screens.filter.select_item_in_filterscreen_ux('SEARCH')
    assertmgr.addCheckPoint(test_name , 2, status, "Fail to go to Search. Current screen: %s" % ve_test.milestones.get_current_screen())

    # Type a keyword and validate a result one
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    if ve_test.is_dummy:
        keyword = 'J'
    else:
        keyword = 'THE'
    ve_test.screens.filter.search_keyword_typing(keyword)
    ve_test.move_towards('down')
    search_result = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'search_result')
    logging.info("---> search_result: %s" % search_result)
    if search_result == False:
        assertmgr.addCheckPoint(test_name, 3, False, "Fail to have a search result")
    else:
        ve_test.validate_focused_item()

    # Retrieve selected asset then launch the Action Menu
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    selected_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'selected_item')
    logging.info("---> selected_event_title: %s" %selected_event_title)
    if selected_event_title == False:
        ve_test.log_assert('No event selected')
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to open the Action Menu on %s" % selected_event_title)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # Check event title display
    logging.info("Check the Event displayed")
    am_event_title = ve_test.screens.action_menu.get_event_title()

    # On live lab
    if not ve_test.is_dummy:
        if am_event_title != selected_event_title:
            assertmgr.addCheckPoint(test_name, 4, False, "Action Menu is launch on %s instead of %s" %(am_event_title, selected_event_title))

        # Check title is in CMDC_asset_list
        cmdc_search_result = ve_test.he_utils.get_search_keyword_result_for_vod_from_cmdc('TO')
        cmdc_selected_asset_title = ""
        cmdc_selected_asset_id = ""
        for result in cmdc_search_result:
            if result == 'suggestions':
                search_result_list = cmdc_search_result[result]
                cmdc_asset_list = ve_test.he_utils.get_content_list_from_search(search_result_list[0])
                # Compare the title between Action Menu and CMDC ones
                for asset in cmdc_asset_list:
                    #logging.info("---> asset: %s" % asset)
                    logging.info('\n')
                    if asset['title'] == am_event_title:
                        _cmdc_selected_asset = asset
                        cmdc_selected_asset_title = asset['title']
                        cmdc_selected_asset_id = asset['id']
                        logging.info("cmdc_selected_asset_title: %s" % cmdc_selected_asset_title)
                        logging.info("cmdc_selected_asset_id: %s" %cmdc_selected_asset_id)
                        break
                else:
                    ve_test.log_assert('AM asset not found in CMDC result')
            else:
                ve_test.log_assert('No CMDC response of keyword search')

        # Check Action Menu short summary

        # Check the Action list
        # Retrieve Actions from CTAP
        if cmdc_selected_asset_id != "":
            ctap_action_menu_resp = ve_test.he_utils.get_actiomenu_by_content_id(cmdc_selected_asset_id)
            ctap_action_title_list = ve_test.screens.action_menu.retrieve_action_list_from_content(ctap_action_menu_resp)
            status = check_action_list(ve_test,ctap_action_title_list)
            assertmgr.addCheckPoint(test_name, 5, status, "Action item list not valid. See log error messages")
        else:
            ve_test.log_assert('AM asset not found in CMDC result')

        # Check access to Summary
        logging.info("Access to the Summary")
        check_access_to_summary(ve_test, test_name, assertmgr, 8)

        # Check the Back Management
        logging.info("Check that fullcontent is displayed on Back")
        check_screen_on_back(ve_test,"full_content")
        logging.info("In Fullcontent")

        back_event_title = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_item')
        if back_event_title == False:
            assertmgr.addCheckPoint(test_name, 11, status, "Failed to come-back on filter's selected asset")
        if back_event_title != selected_event_title:
            assertmgr.addCheckPoint(test_name, 12, status, "Failed to have the same asset selected in filter on come-back")

    # In Dummy
    else:
        logging.info("In dummy - Check the Actions List")
        status = check_action_list(ve_test,CONSTANTS.actionlist_vod_event)
        assertmgr.addCheckPoint(test_name, 5, status, "Action item list not valid. See log error messages")

    assertmgr.verifyAllCheckPoints()
    end_test(ve_test,test_name)


def get_current_event(events_cache):
    current_time = events_cache["currentTime"]
    for event in events_cache["eventsCache"]:
        start_time = event["startTime"]
        duration = event["duration"]
        if (start_time <= current_time) and ((start_time + duration) > current_time):
            return event
    return None

def search(table, searchFor):
    for values in table:
        for k in values:
            for v in values[k]:
                if searchFor in v:
                    return k
    return None

def getRatingNameByValue(schemes, value):
    for scheme in schemes:
        if 'value' in scheme and scheme['value'] == str(value):
            return scheme['name']
    return ""
        
@pytest.mark.non_regression
@pytest.mark.F_Live
@pytest.mark.FS_ActionMenu
@pytest.mark.LV_L3
def test_actionmenu_check_if_live_program_am_has_parental_rating_displayed():
    """
    Checks if live program with 'parentalRating' is properly diplayed in his action menu
    """
    test_name = "test_actionmenu_check_if_live_program_am_has_parental_rating_displayed"
    ve_test = VeTestApi(title=test_name)
    ve_test.begin(screen=ve_test.screens.main_hub)

    status = ve_test.screens.fullscreen.navigate()
    ve_test.log_assert(status, "Failed to go to the full Screen. Current screen: %s" % ve_test.milestones.get_current_screen())
    
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Failed to go to the action menu. Current screen: %s" % ve_test.milestones.get_current_screen())
    
    events = ve_test.milestones.getPcEventsCache()

    currentEvent = get_current_event(events)
    ve_test.log_assert(currentEvent != None, "Failed to get current event Data.")


    eventRating = currentEvent['parentalRating']
    schemes = ve_test.he_utils.get_ratings_scheme_from_cmdc()
    nameInAM = ""
    for scheme in schemes:
        if 'value' in scheme and scheme['value'] == str(eventRating):
            nameInAM = scheme['name']
            break

    milestone = ve_test.milestones.getElements()
    milestoneStr = str(milestone)
    
    status = milestoneStr.find(nameInAM) >= 0
    ve_test.log_assert(status, "Event information '%s' not displayed on the action menu screen." %nameInAM)
    ve_test.end()
    
@pytest.mark.non_regression
@pytest.mark.F_VOD
@pytest.mark.FS_ActionMenu
@pytest.mark.LV_L3
def test_actionmenu_check_if_vod_asset_has_right_parental_rating_displayed():
    """
    Checks if VOD asset with 'parentalRating' is properly displayed in his action menu screen
    """
    test_name = "test_actionmenu_check_if_vod_asset_has_right_parental_rating_displayed"
    ve_test = VeTestApi(title=test_name)
    ve_test.begin(screen=ve_test.screens.main_hub)
    vod_manager = ve_test.screens.playback.vod_manager

    vod_manager.go_to_vod_asset("TVOD") #go_to_asset_action_menu(test)
    ve_test.repeat_key_press("KEYCODE_DPAD_RIGHT", 1, 2)
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 10)
    milestone = ve_test.milestones.getElements()
    milestoneStr = str(milestone)
    
    title = ve_test.milestones.get_value_by_key(milestone, "prog_title")
    asset = ve_test.he_utils.get_content_list_from_search(title)[0]
    assetRating = asset['parentalRating']['rating']
    
    schemes = ve_test.he_utils.get_ratings_scheme_from_cmdc()
    nameInAM = ""
    for scheme in schemes:
        if 'value' in scheme and scheme['value'] == str(assetRating):
            nameInAM = scheme['name']
            break
    
    status = milestoneStr.find(nameInAM) >= 0
    ve_test.log_assert(status, "Event information '%s' not displayed on the action menu screen." % nameInAM)
    ve_test.end()

@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_ActionMenu
@pytest.mark.F_Clock
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_check_clock_in_actionmenu():
    ve_test = VeTestApi(title="test_check_clock_in_actionmenu")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    check_action_menu_launch_fullscreen(ve_test)

    clock_time = ve_test.get_clock_time()
    if not clock_time:
        ve_test.log_assert(False, "The Clock is not displayed in live ActionMenu")
    else:
        logging.info("Clock is displayed: %s" % clock_time)

    # wait 1 min and check time is updated
    status = ve_test.check_clock_time_update(clock_time)
    ve_test.log_assert(status, "Clock is not more displayed after 1 min. Current screen: %s" % ve_test.milestones.get_current_screen())

    ve_test.end()
    logging.info("##### End test_check_clock_in_actionmenu #####")
