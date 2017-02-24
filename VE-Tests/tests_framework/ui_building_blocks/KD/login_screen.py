__author__ = 'bwarshaw'

import logging
from time import sleep
from tests_framework.ui_building_blocks.screen import Screen

''' Global constants '''
TAB_KEYEVENT = 61
ENTER_KEYEVENT = 66

'''TIME OUT'S'''
SHORT_TIMEOUT = 3
MEDIUM_TIMEOUT = 6
LONG_TIMEOUT = 60

loginFirstTry = True
class LoginScreen(Screen):

    def __init__(self, test):
        Screen.__init__(self, test, "login")

    def auto_sign_in(self):
        global loginFirstTry
        if self.test.platform == "Android" and self.test.is_dummy:
            return
        if (self.test.login is self.test.login_types.login):
            self.test.screens.boot.wait_untill_not_active()
            if self.is_active(LONG_TIMEOUT, bootmode=True):
                loginFirstTry = True
                self.sign_in()
            elif self.test.is_fixed_household == True:
                self.test.login = self.test.login_types.none
            else:
                if self.test.platform == "iOS" and loginFirstTry:
                    loginFirstTry = False
                    #try to deactivate then try again
                    logging.info("trying to log out and in again")
                    self.test.say("trying to log out and in again")
                    self.test.say("stopping app")
                    self.test.appium.stop_app(True)
                    self.test.say("launching app")
                    self.test.appium.launch_app()
                    self.test.say("auto sign in")
                    self.auto_sign_in()
                else:
                    self.test.screens.login_screen.verify_active()

        if (self.test.login is self.test.login_types.custom) or (self.test.is_fixed_household == True):
            logging.info('use Household (in appium in) : %s' +self.test.configuration["he"]["generated_household"])

    def sign_in(self, hh_id=None, user_name=None, password='123', verify_startup_screen = True):
        if hh_id is None or user_name is None:
            if self.test.is_fixed_household:
                hh_id = self.test.configuration["he"]["generated_household"]
                user_name = self.test.configuration["he"]["generated_username"]
                password = self.test.configuration["he"]["password"]
            elif self.test.is_dummy:
                hh_id = self.test.title
                user_name = 'dummy'
            else:
                credentials = self.test.he_utils.get_default_credentials()
                hh_id, user_name = credentials[0], credentials[1]

        logging.info("hh_id= %s" % hh_id)
        self.test.configuration["he"]["generated_household"] = hh_id
        self.test.configuration["he"]["generated_username"] = user_name
        self.test.configuration["he"]["password"] = password

        self.enter_credentials(user_name, password)

        # check failures on Login
        self.wait_untill_not_active()
        screen = self.test.milestones.get_current_screen()
        logging.info(' screen= ' + screen)
        if screen == "notification":
            login_error = False
            message = self.test.screens.notification.get_notification_message()
            if message in (self.test.milestones.get_dic_value_by_key("DIC_ERROR_SIGN_IN_FAILED_ACTIVATION", "error"),
                           self.test.milestones.get_dic_value_by_key("DIC_ERROR_SIGN_IN_FAILED_CREDENTIALS", "error"),
                           self.test.milestones.get_dic_value_by_key("DIC_ERROR_SIGN_IN_FAILED_NETWORK_REQUIRED", "error"),
                           self.test.milestones.get_dic_value_by_key("DIC_ERROR_SIGN_IN_FAILED_UNREACHABLE", "error")):
                login_error = True
            self.test.log_assert(login_error==False, "failed on login with error message: %s" % message)

        if verify_startup_screen and self.test.startup_screen:
            self.test.startup_screen.verify_active(LONG_TIMEOUT, ignoreNotification=True)

        self.test.milestones.device_details = None

    def enter_credentials(self, user_name, password):
        "Verifiy state"
        self.verify_active()
        timeout = self.test.login_wait
        if timeout:
            timeout = int(timeout)
        else:
            timeout = MEDIUM_TIMEOUT
        self.test.log("login wait: " + str(timeout))
        self.test.wait(timeout)

        logging.info("user_name= %s, password= %s" % (user_name, password))

        if self.test.platform == "Android":
            self.test.wait(SHORT_TIMEOUT)
            if self.test.liveIdp:
                self.test.appium.key_event(TAB_KEYEVENT)
            self.test.appium.type_keyboard(user_name)
            self.test.wait(SHORT_TIMEOUT)
            "Enter username text"
            self.test.appium.key_event(TAB_KEYEVENT)
            self.test.wait(MEDIUM_TIMEOUT)
            "Enter password text"
            self.test.appium.type_keyboard(password)
            self.test.wait(SHORT_TIMEOUT)
            "Performing sign in action"
            self.test.appium.key_event(ENTER_KEYEVENT)
        else:
            isWebLogin = self.test.milestones.getUniqueElementValue("is_web_login")
            if isWebLogin:
                useWebLogin = (isWebLogin == "true")
            else:
                useWebLogin = self.test.use_web_login
            self.test.log("useWebLogin: " + str(useWebLogin) + " deviceLogin:" + str(isWebLogin))
            if useWebLogin:
                self.test.appium.show_keyboard()
                self.test.appium.type_keyboard(user_name, 'username')
                self.test.appium.type_keyboard(password, 'password')
                self.test.wait(SHORT_TIMEOUT)
                self.test.appium.hide_keyboard('Go')
            else:
                self.test.appium.show_keyboard()
                self.test.wait(MEDIUM_TIMEOUT)
                self.test.appium.type_keyboard(user_name, None)
                self.test.wait(SHORT_TIMEOUT)
                self.test.appium.hide_keyboard('Go')

