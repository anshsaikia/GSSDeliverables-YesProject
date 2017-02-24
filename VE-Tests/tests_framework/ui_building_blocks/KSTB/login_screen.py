__author__ = 'bwarshaw'

import logging
from time import sleep
from tests_framework.ui_building_blocks.screen import Screen

''' Global constants '''
TAB_KEYEVENT = 61
ENTER_KEYEVENT = 66

'''TIME OUT'S'''
SIGN_IN_TIMEOUT = 20
TIMEOUT = 2
LOGIN_WEBAPP_TIMEOUT = 10

class LoginScreen(Screen):

    def __init__(self, test):
        Screen.__init__(self, test, "login")

    def auto_sign_in(self):
        if self.test.platform == "Android" and (self.test.is_dummy or self.test.is_local_ctap):
            return
        if (self.test.login is self.test.login_types.login):
            self.test.screens.boot.wait_untill_not_active()
            if self.is_active(TIMEOUT*2, ignoreNotification=True):
                self.sign_in()
            elif self.test.is_fixed_household == True:
                self.test.login = self.test.login_types.none
            else:
                self.test.log_assert(False, "Login page is not displayed, current-screen: " + self.test.milestones.last_current_screen)

        if (self.test.login is self.test.login_types.custom) or (self.test.is_fixed_household == True):
            self.test.he_utils.houseHolds.append(self.test.configuration["he"]["household"])
            logging.info('Household (in appium in) : %s' +self.test.configuration["he"]["household"])

    def sign_in(self, hh_id=None, user_name=None, password='123'):
        if hh_id is None or user_name is None:
            if self.test.is_fixed_household:
                hh_id = user_name = self.test.configuration["he"]["username"]
#                password = "Olympia"
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

        self.test.appium.take_screenshot("login_screen_sign_in_before")
        self.test.wait_for_screen_assert(SIGN_IN_TIMEOUT, "main_hub", msg = "Failed to verify MainHub screen when completing signIn")

        self.test.milestones.device_details = None

    def enter_credentials(self, user_name, password):
        self.test.appium.take_screenshot("login_screen_enter_credentials")
        "Verifiy state"
        self.verify_active()
        self.test.wait(LOGIN_WEBAPP_TIMEOUT)

        logging.info("user_name= %s, password= %s" % (user_name, password))

        if self.test.platform == "Android":
            self.test.appium.type_keyboard(user_name)
            self.test.wait(TIMEOUT)
            "Enter username text"
            self.test.appium.key_event(TAB_KEYEVENT)
            self.test.appium.take_screenshot("login_screen_enter_credential_before")
            self.test.wait(0.5)
            "Enter password text"
            self.test.appium.type_keyboard(password)
            self.test.appium.take_screenshot("login_screen_enter_credential_after")
            self.test.wait(TIMEOUT)
            "Performing sign in action"
            self.test.appium.key_event(ENTER_KEYEVENT)
        elif self.test.use_appium:
            app_element = self.test.appium.get_element_by_class_name('UIATextField', 0)
            self.test.appium.type_keyboard(user_name, app_element)

            if self.test.use_web_login:
                app_element = self.test.appium.get_element_by_class_name('UIASecureTextField', 0)
                self.test.appium.type_keyboard(password, app_element) #change to password

            self.test.appium.hide_keyboard('Go')

        else:
            if self.test.use_web_login:
                self.test.appium.show_keyboard()
                self.test.appium.type_keyboard(user_name, 'username')
                self.test.appium.type_keyboard(password, 'password')
                self.test.wait(TIMEOUT)
                self.test.appium.hide_keyboard('Go')
            else:
                self.test.appium.show_keyboard()
                self.test.appium.type_keyboard(user_name, None)
                self.test.wait(TIMEOUT)
                self.test.appium.hide_keyboard('Go')

