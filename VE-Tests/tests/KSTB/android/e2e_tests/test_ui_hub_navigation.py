__author__ = 'bngo'

from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
import logging
import pytest


# ====================
# UTILITIES FUNCTIONS
# ====================
def check_channel_name_display(ve_test):
    logging.info("Check that the channel name is displayed for the current event")
    channel_info = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'focused_asset_channel_info')
    logging.info("channel_info: %s" % channel_info)
    if not channel_info:
        logging.info("no channel_info milestone")
        return False
    else:
        if 'logo' in channel_info:
            if channel_info['logo'] != "" and channel_info['logo'] != None and not channel_info['logo']:
                logging.info("logo present")
                return False
        if 'name' in channel_info:
            logging.info("channel name present")
            return True
    return False


def check_channel_logo_display(ve_test):
    logging.info("Check that the channel logo is displayed for the current event")
    elt = ve_test.milestones.getElements()
    channel_info = ve_test.milestones.get_value_by_key(elt, 'focused_asset_channel_info')
    logging.info("channel_info: %s" % channel_info)
    if not channel_info:
        logging.info("no channel_info milestone")
        return False
    else:
        logging.info("channel_info['logo']: %s" % channel_info['logo'])
        if 'logo' in channel_info:
            logging.info("logo found item")
            if channel_info['logo'] != "" and channel_info['logo'] != None and channel_info['logo'] != False:
                logging.info("logo present")
                return True
        else:
            logging.info("else  channel_info['logo']: %s" % channel_info['logo'])
    return False


# ====================
# TESTS
# ====================


@pytest.mark.non_regression
@pytest.mark.FS_HUB
@pytest.mark.LV_L2
def test_hub_navigation():
    ve_test = VeTestApi("test_hub_navigation")

    ve_test.begin(screen=ve_test.screens.fullscreen)
    logging.info("Check Hub timeout")
    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
    ve_test.log_assert(status, "Hub timeout to fullscreen failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Access to ActionMenu from Fullscreen")
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Navigation from fullscreen to actionmanue has failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status = ve_test.screens.fullscreen.navigate()
    ve_test.log_assert(status, "Navigation from actionmenu to fullscreen has failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Access to Timeline from fullscreen")
    status = ve_test.screens.timeline.navigate()
    ve_test.log_assert(status, "Navigation from fullscreen to timeline has failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status = ve_test.screens.fullscreen.navigate()
    ve_test.log_assert(status, "Navigation from timeline to fullscreen has failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Access to Hub from fullscreen")
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status, "Navigation from fullscreen to main hub has failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Access to Settings from Hub")
    status = ve_test.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES", expected_pos=10, check_pos=False)
    ve_test.log_assert(status, "Access to Settings from Hub has failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status, "Navigation from PREFERENCES submenu to main hub has failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Access to TV Filter from Hub")
    status = ve_test.screens.main_hub.to_tvfilter_from_hub(expected_pos=0, check_pos=True)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    ve_test.log_assert(status, "Access to TV Filter from Hub has failed")
    status = ve_test.screens.main_hub.navigate()
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    ve_test.log_assert(status, "Navigation from TV Filter to main hub has failed")

    logging.info("Access to Guide from Hub")
    status = ve_test.screens.guide.navigate()
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    ve_test.log_assert(status, "Navigation from main hub to guide has failed")
    status = ve_test.screens.main_hub.navigate()
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    ve_test.log_assert(status, "Navigation from guide to main hub has failed")

    logging.info("Access to Search from Hub")
    status = ve_test.screens.search.navigate()
    ve_test.log_assert(status, "Navigation from main hub to search has failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status, "Navigation from search to main hub has failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # Can't access Library at this time as there is no record in it (OK on Library option has no effect)
    logging.info("Access to Library from Hub")
    status = ve_test.screens.library.navigate()
    if not status:  # If we did not enter Library but library is empty, then no error
        focused_asset = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_asset")
        ve_test.log_assert(focused_asset == "YOUR LIBRARY IS EMPTY", "Navigation from main hub to library has failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status, "Navigation from library to main hub has failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Access to Store from Hub")
    status = ve_test.screens.main_hub.navigate_to_store()
    ve_test.log_assert(status, "Navigation to store from mainhub has failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status, "Navigation to main hub from store has failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Access to fullscreen from Hub")
    status = ve_test.screens.fullscreen.navigate()
    ve_test.log_assert(status, "Navigation from hub to fullscreen has failed")

    ve_test.end()

@pytest.mark.non_regression
@pytest.mark.FS_HUB
@pytest.mark.LV_L3
def test_hub_missing_channel_logo():
    ve_test = VeTestApi("test_hub_missing_channel_logo")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
    ve_test.log_assert(status, "Hub timeout to fullscreen failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # Zap to a channel without logo
    channel_number = CONSTANTS.channel_number_without_logo
    logging.info("Zap to channel n %s" % channel_number)
    ve_test.screens.playback.dca(channel_number)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # Check that Channel name is displayed in the Hub as no logo is available
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status, "Failure to access to the Hub")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status = check_channel_logo_display(ve_test)
    logging.info("status: %s " % status)
    ve_test.log_assert(not status, "Channel logo is displayed and is not expected on this channel (%s)" % ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'current_channel_info'))
    status = check_channel_name_display(ve_test)
    logging.info("status: %s " % status)
    ve_test.log_assert(status, "Channel name is not displayed and is expected on this channel (%s)." % ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'current_channel_info'))

    status = ve_test.screens.fullscreen.navigate()
    ve_test.log_assert(status, "Failure to come-back from Hub to fullscreen")
    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # Zap to a channel with logo
    channel_number = CONSTANTS.channel_number_classic_1
    logging.info("Zap to channel n %s" % channel_number)
    ve_test.screens.playback.dca(channel_number)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    # Check that Channel name is displayed in the Hub as no logo is available
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status, "Failure to access to the Hub")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status = check_channel_logo_display(ve_test)
    ve_test.log_assert(status, "Channel logo is NOT displayed and is expected on this channel (%s)" % ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), 'current_channel_info'))

    ve_test.end()
