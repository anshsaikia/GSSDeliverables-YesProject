__author__ = 'bwarshaw'

import logging

logging.getLogger('').handlers = []
logging.basicConfig(format="^%(asctime)s !%(levelname)s M:%(filename)s F:%(funcName)s L:%(lineno)d > %(message)s", datefmt="%y/%m/%d %H:%M:%S")

class Logger(object):
    def __init__(self, test):
        self.test = test

    def log_assert(self, condition, msg='assert error'):
        if not condition:
            if self.test.milestones.last_current_screen:
                msg += ", screen: " + self.test.milestones.last_current_screen + ", trail: " + str(self.test.milestones.screen_trail)
            logging.error(msg)
            self.test.assert_error = msg
            self.test.say('Assert failed! ' + msg)
            self.test.end(endFromAssert = True)
            assert condition, msg

    def log(self, msg):
        logging.info(msg)

    def setLevel(self, level, module_name=None):
        logger = logging.getLogger(module_name)
        logger.setLevel(level)
