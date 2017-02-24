import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
import logging

GENERIC_WAIT = 2
WAIT_TIMEOUT = 10


    
@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Reboot
@pytest.mark.notification    
@pytest.mark.LV_L2
def test_error_logging():
    '''
    Test the error message on a failed login attempt
    
    Check that the messages are not empty
    Check the error code
    Check that the back button dismissed the error message and goes back to the login screen
    ""Home"" button is not tested as it can only be done manually
    :return:
    '''
    ve_test = VeTestApi("test_error_logging")
    ve_test.fail_login_begin()
    
    ve_test.wait(GENERIC_WAIT * 2)
    milestone = ve_test.milestones.getElements()
    
    # Testing the screen name
    screen_name = ve_test.milestones.get_value_by_key(milestone, "screen_name")
    ve_test.log_assert(screen_name == "notification", "Error Message Screen not shown, actual screen = {}"
                       .format(screen_name))
    
    # displaying error messages
    msg_title=ve_test.milestones.get_value_by_key(milestone, "msg_title")
    logging.info("msg_title : {}".format(msg_title))
    ve_test.log_assert(len(msg_title) != 0, "Error Message has no title")
    
    msg_text=ve_test.milestones.get_value_by_key(milestone,"msg_text")
    logging.info("msg_text : {}".format(msg_text))
    ve_test.log_assert(len(msg_text) != 0, "Error Message has no message")
    
    msg_error=ve_test.milestones.get_value_by_key(milestone,"msg_error")
    logging.info("msg_error : {}".format(msg_error))
    ve_test.log_assert(len(msg_error) != 0, "Error Message has no error")
    
    ve_test.log_assert("ERR-104" in msg_error, "Error code is {} instead of should be ERR-104".format(msg_error))

    button_nb=ve_test.milestones.get_value_by_key(milestone,"button_nb")
    logging.info("button_nb : {}".format(button_nb))
    ve_test.log_assert(button_nb == 2 , "Wrong number of buttons, Found {} instead of 2 ".format(button_nb))
    
    focused_button = ve_test.milestones.get_value_by_key(milestone,"focused_action")
    logging.info("focused_button : {}".format(focused_button))
    
    prev_focused_button = focused_button    
    ve_test.move_towards('right')
    ve_test.wait(GENERIC_WAIT)
    milestone = ve_test.milestones.getElements()
    focused_button = ve_test.milestones.get_value_by_key(milestone,"focused_action")
    logging.info("focused_button : {}".format(focused_button))
    
    ve_test.log_assert(focused_button != prev_focused_button , "Buttons texts should be different. Button : {}"
                       .format(focused_button))

    # Check that by selecting and pressing the back button, the error message is dismissed
    # and we are at the login screen again.
    if focused_button != "RETRY":
        ve_test.move_towards('left')
        
    ve_test.validate_focused_item()
    ve_test.wait(GENERIC_WAIT)
    milestone = ve_test.milestones.getElements()
    
    screen_name=ve_test.milestones.get_value_by_key(milestone,"screen_name")
    ve_test.log_assert(screen_name != "notification", "Error Message Screen not dismissed: Screen display : {}"
                       .format(screen_name))
    
    status = ve_test.wait_for_screen(WAIT_TIMEOUT, "login" )
    ve_test.log_assert(status, "Not on login screen")
    
    logging.info("Back to login screen")
    
    ve_test.wait(GENERIC_WAIT)
    ve_test.end()

