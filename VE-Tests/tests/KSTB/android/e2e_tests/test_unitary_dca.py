__author__ = 'obesrest'



import pytest

from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS

'''Globals'''
SCREEN_GUIDE = 'guide'
SCREEN_ZAPLIST = 'zap_list_tv'
SCREEN_HUB = 'hub'
SCREEN_FULLSCREEN = 'fullscreen'
SCREEN_TIMELINE = 'timeline'
SCREEN_INFOLAYER = 'infolayer'

#test DCA behavior on zaplist: if channel number exists, scroll to this channel, if not, scroll to closest channel

@pytest.mark.non_regression
@pytest.mark.FS_Dca
@pytest.mark.dummy
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_dca
def test_dca_fullscreen():
    ve_test = VeTestApi("Test_DCA_fullscreen")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    channelList = sorted(list(set(ve_test.he_utils.get_channel_number_list_from_cmdc())))
    ve_test.log_assert(ve_test.screens.fullscreen.navigate(), "Fullscreen could not be accessed")
    currentChannel = ve_test.screens.fullscreen.get_current_channel()

    # zapping on existing channel
    check_valid_channel(ve_test,channelList, currentChannel, SCREEN_INFOLAYER)

    ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, SCREEN_FULLSCREEN)
    currentChannel = ve_test.screens.fullscreen.get_current_channel()

    # zapping on existing channel with several digits
    check_valid_channel(ve_test,channelList, currentChannel, SCREEN_INFOLAYER,10)
    ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, SCREEN_FULLSCREEN)
    currentChannel = ve_test.screens.fullscreen.get_current_channel()
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # cancel dca
    for num_digits in range(1,3):
        cancel_dca_with_back(ve_test, currentChannel, num_digits)
        ve_test.wait(CONSTANTS.GENERIC_WAIT)
        ve_test.log_assert(currentChannel == ve_test.screens.fullscreen.get_current_channel(), "dca cancelling with back has failled num_digits="+str(num_digits))

        cancel_dca_with_left(ve_test, currentChannel, num_digits)
        ve_test.wait(CONSTANTS.GENERIC_WAIT)
        ve_test.log_assert(currentChannel == ve_test.screens.fullscreen.get_current_channel(), "dca cancelling with left has failled num_digits="+str(num_digits))

    # check dca with correction in keypress
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    perform_dca_with_correction(ve_test,channelList, currentChannel, SCREEN_INFOLAYER)

    # zapping on non-existing channel -> hole in the channel list
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    check_hole_in_channelList(ve_test, channelList, SCREEN_FULLSCREEN)

    # zapping on non-existing channel -> out of bound
    wait_for_error_message_end(ve_test)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    perform_dca(ve_test,channelList, channelList[len(channelList)-1] + 1, SCREEN_FULLSCREEN)

    ve_test.end()

@pytest.mark.non_regression
@pytest.mark.FS_Dca
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_dca_zaplist():
    ve_test = VeTestApi("Test_DCA_zaplist")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    ve_test.log_assert(ve_test.screens.fullscreen.navigate(), "Fullscreen could not be accessed")
    channelList = sorted(list(set(ve_test.he_utils.get_channel_number_list_from_cmdc())))

    ve_test.log_assert(ve_test.screens.zaplist.navigate(), "Zaplist could not be accessed")
    currentChannel = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_channel_number")

    # zapping on existing channel
    check_valid_channel(ve_test,channelList,currentChannel,SCREEN_ZAPLIST)

    # zapping on existing channel with several digits
    ve_test.log_assert(ve_test.screens.zaplist.navigate(), "Zaplist could not be accessed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    currentChannel = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focused_channel_number")
    check_valid_channel(ve_test,channelList, currentChannel, SCREEN_ZAPLIST,10)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # zapping on non-existing channel -> hole in the channel list
    ve_test.log_assert(ve_test.screens.zaplist.navigate(), "Zaplist could not be accessed")
    check_hole_in_channelList(ve_test, channelList, SCREEN_ZAPLIST)
    wait_for_error_message_end(ve_test)

    # zapping on non-existing channel -> out of bound
    perform_dca(ve_test,channelList,channelList[len(channelList)-1] + 1,SCREEN_ZAPLIST)

    ve_test.end()

@pytest.mark.non_regression
@pytest.mark.FS_Dca
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_dca_timeline():
    ve_test = VeTestApi("Test_DCA_timeline")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    ve_test.log_assert(ve_test.screens.fullscreen.navigate(), "Fullscreen could not be accessed")

    channelList = sorted(list(set(ve_test.he_utils.get_channel_number_list_from_cmdc())))

    ve_test.log_assert(ve_test.screens.timeline.navigate(), "timeline could not be accessed")
    currentChannel = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focused_channel_number")

    # zapping on existing channel
    check_valid_channel(ve_test,channelList,currentChannel,SCREEN_TIMELINE)

    # zapping on existing channel with several digits
    ve_test.log_assert(ve_test.screens.timeline.navigate(), "timeline could not be accessed")
    currentChannel = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_channel_number")
    check_valid_channel(ve_test,channelList,currentChannel,SCREEN_TIMELINE,10)

    # zapping on non-existing channel -> hole in the channel list
    ve_test.log_assert(ve_test.screens.timeline.navigate(), "timeline could not be accessed")
    check_hole_in_channelList(ve_test,channelList,SCREEN_TIMELINE)
    wait_for_error_message_end(ve_test)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # zapping on non-existing channel -> out of bound
    perform_dca(ve_test,channelList,channelList[len(channelList)-1] + 1,SCREEN_TIMELINE)

    ve_test.end()

@pytest.mark.non_regression
@pytest.mark.FS_Dca
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_dca_hub():
    ve_test = VeTestApi("Test_DCA_hub")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    channelList = sorted(list(set(ve_test.he_utils.get_channel_number_list_from_cmdc())))
    ve_test.log_assert(ve_test.screens.fullscreen.navigate(), "Fullscreen could not be accessed")
    currentChannel = ve_test.screens.fullscreen.get_current_channel()
    ve_test.log_assert(ve_test.screens.main_hub.navigate(), "Hub could not be accessed")

    # zapping on existing channel
    check_valid_channel(ve_test,channelList,currentChannel, SCREEN_INFOLAYER)

    # zapping on existing channel with several digits
    ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, SCREEN_FULLSCREEN)
    currentChannel = ve_test.screens.fullscreen.get_current_channel()
    ve_test.log_assert(ve_test.screens.main_hub.navigate(), "Hub could not be accessed")
    check_valid_channel(ve_test,channelList,currentChannel, SCREEN_INFOLAYER,10)

    # zapping on non-existing channel -> hole in the channel list
    ve_test.log_assert(ve_test.screens.main_hub.navigate(), "main hub is not displayed")
    check_hole_in_channelList(ve_test,channelList, SCREEN_HUB)
    wait_for_error_message_end(ve_test)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # zapping on non-existing channel -> out of bound
    perform_dca(ve_test,channelList,channelList[len(channelList)-1] + 1, SCREEN_HUB)

    ve_test.end()


@pytest.mark.non_regression
@pytest.mark.FS_Dca
@pytest.mark.dummy
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_dca
def test_dca_grid():
    ve_test = VeTestApi("Test_DCA_grid")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    channelList = sorted(list(set(ve_test.he_utils.get_channel_number_list_from_cmdc())))
    ve_test.log_assert(ve_test.screens.guide.navigate(), "STB is not on guide")
    currentChannel = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_channel_number")

    # zapping on existing channel
    check_valid_channel(ve_test, channelList, currentChannel, SCREEN_GUIDE)

    # zapping on existing channel with several digits
    check_valid_channel(ve_test, channelList, currentChannel, SCREEN_GUIDE,10)

    # zapping on non-existing channel -> hole in the channel list
    check_hole_in_channelList(ve_test,channelList, SCREEN_GUIDE)
    wait_for_error_message_end(ve_test)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # zapping on non-existing channel -> out of bound
    perform_dca(ve_test,channelList,channelList[len(channelList)-1] + 1, SCREEN_GUIDE)

    ve_test.end()

################ Methods specific to dca tests #################

def perform_dca(ve_test, channelList, dca_number, screen):
    ve_test.screens.playback.dca(dca_number)
    check_dca(ve_test, channelList, dca_number, screen)

def check_dca(ve_test, channelList, dca_number, screen):
    if dca_number in channelList:
        expectedChannel = dca_number
        if screen in [SCREEN_INFOLAYER, SCREEN_ZAPLIST, SCREEN_TIMELINE, SCREEN_GUIDE]:
            ve_test.log_assert(ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, screen), "STB is not on " + screen)
            focusedChannel = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_channel_number")
            retries = 0
            while focusedChannel != expectedChannel and retries < 10:
                ve_test.wait(1)
                focusedChannel = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_channel_number")
                retries += 1

            ve_test.log_assert(focusedChannel == expectedChannel, "focus is on channel " + str(focusedChannel) + " instead of " + str(expectedChannel))

        if screen in [SCREEN_INFOLAYER, SCREEN_ZAPLIST, SCREEN_TIMELINE]:
            ve_test.appium.key_event("KEYCODE_DPAD_CENTER")

        if screen != SCREEN_GUIDE:
            ve_test.log_assert(ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, SCREEN_FULLSCREEN), "STB is not on fullscreen")
            ve_test.log_assert(ve_test.screens.fullscreen.get_current_channel() == focusedChannel, "Current channel is not " + str(expectedChannel))
    else:
        if not(screen in [SCREEN_INFOLAYER, SCREEN_ZAPLIST, SCREEN_TIMELINE, SCREEN_GUIDE]):
            message = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "dca_message")
            retries = 0
            while (not message) and retries < 10:
                ve_test.wait(1)
                message = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "dca_message")
                retries += 1
            ve_test.log_assert(message != False, "No DCA Error message")
            ve_test.log_assert(ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "dca_input") == str(dca_number), "DCA input is not "+str(dca_number))

def wait_for_error_message_end(ve_test):
    message = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "dca_message")
    retries = 0
    while (message != False) and retries < 10:
        ve_test.wait(1)
        message = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "dca_message")
        retries += 1


def perform_dca_with_correction(ve_test, channelList, currentChannel,screen):
    for channel in channelList :
        if channel != currentChannel and channel > 9:
            for i in range(0,len(str(channel))) :
                ve_test.appium.key_event("KEYCODE_" + str(channel)[i])
                ve_test.wait(0.3)
                if i == 1:
                    ve_test.appium.key_event("KEYCODE_DPAD_LEFT")
                    ve_test.wait(0.3)
                    ve_test.appium.key_event("KEYCODE_" + str(channel)[1])

            ve_test.wait(1.6)
            check_dca(ve_test, channelList, channel, screen)
            return


def check_valid_channel(ve_test, channelList, currentChannel, screen, min_channel_number =1):
    for i in channelList :
        if i != currentChannel and i >= min_channel_number:
            perform_dca(ve_test,channelList,i,screen)
            return

def check_hole_in_channelList(test, channelList, screen):
    for j in range(50, 999) :
        if not(j in channelList) :
            perform_dca(test, channelList, j, screen)
            return

def cancel_dca_with_left(ve_test, currentChannel, number_of_digits = 1):
    digit = other_digit(int(str(currentChannel)[0]))
    for i in range(0, number_of_digits):
        ve_test.appium.key_event("KEYCODE_" + str(digit))
        digit = other_digit(digit)
        ve_test.wait(0.1)

    for i in range(0, number_of_digits):
        ve_test.appium.key_event("KEYCODE_DPAD_LEFT")
        ve_test.wait(0.3)

def cancel_dca_with_back(ve_test, currentChannel, number_of_digits = 1):
    digit = other_digit(int(str(currentChannel)[0]))
    for i in range(0, number_of_digits):
        ve_test.appium.key_event("KEYCODE_" + str(digit))
        digit = other_digit(digit)
        ve_test.wait(0.1)
    ve_test.appium.key_event("KEYCODE_BACK")
    ve_test.wait(0.3)

def other_digit(digit):
    if digit == 9:
        return 1
    else:
        return int(digit)+1