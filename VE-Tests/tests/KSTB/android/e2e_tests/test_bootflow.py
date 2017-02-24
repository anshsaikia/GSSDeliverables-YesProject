from __builtin__ import str
__author__ = 'ljusseau'

import os
import ast
import json
import pytest
import logging
#import pdb

from tests_framework.ve_tests.ve_test import VeTestApi

level = os.environ.get('LOG_LEVEL', 'INFO')

logging.basicConfig(level=level,
                    format="^%(asctime)s !%(levelname)s <t:%(threadName)s T:%(name)s M:%(filename)s F:%(funcName)s L:%(lineno)d > %(message)s",
                    datefmt="%y/%m/%d %H:%M:%S")

logging.getLogger("requests").setLevel(logging.WARNING)

'''
Boot application and verify the boot component list
'''
@pytest.mark.FS_Reboot
@pytest.mark.sanity
@pytest.mark.LV_L2
def test_normal_bootflow():
    component_tag = 'component'
    ve_test = VeTestApi("test_normal_bootflow")
    ve_test.begin()
    ve_test.wait(5)

    bootComponents = ve_test.milestones.getBootComponents()
    sequenceId = bootComponents['BootSequenceId']
    expectedComponents = bootComponents['BootSequences'][sequenceId]
    executedComponents = bootComponents['ExecutedBootComponents']
    
    #pdb.set_trace()
    ve_test.log_assert(len(expectedComponents) == len(executedComponents.keys()), " Not matching number of expected bootComponents " + str(len(executedComponents.keys())) + " that should be equal to " + str(len(expectedComponents)))
    
    it = 0
    for bootComponent in expectedComponents :
        executedBootComponent = executedComponents[str(it)]
        logging.info(bootComponent)
        logging.info(executedBootComponent)
        ve_test.log_assert(bootComponent[component_tag] == executedBootComponent[component_tag], "incorrect executed boot component " + bootComponent[component_tag] + " instead of " + executedBootComponent[component_tag])
        if bootComponent['timeOut'] != 0:
            ve_test.log_assert(bootComponent['timeOut'] >= executedBootComponent['duration'], "should be in timeOut " + bootComponent[component_tag] + " boot component. [timeout(" + str(bootComponent['timeOut']) + "):spendtime(" + str(executedBootComponent['duration']) + ")]")
        it = it + 1
          
    ve_test.end()

 
'''
Boot the application with a test BootSequence that has a timeout exception in one component
and check if Error an error message is displayed.
'''
@pytest.mark.FS_Reboot
@pytest.mark.sanity
def test_bootflow_with_timeout_exception():
    pref_keyword = "pref_app_boot_sequenceId"
    testSequence = "sequence_timeoutErrorInTest"
    
    ve_test = VeTestApi("test_bootflow_with_timeout_exception")
    ve_test.begin()
    
    boot_sequences_id = ve_test.milestones.getSettings(pref_keyword)[pref_keyword]
    logging.info("Current sequence ID:" + boot_sequences_id)
    
    ve_test.milestones.changeSettings(json.dumps([pref_keyword, testSequence]))
     
    ve_test.appium.restart_app()
    ve_test.wait(5)
    
    changed_boot_sequences_id = ve_test.milestones.getSettings(pref_keyword)[pref_keyword]
    logging.info("Changed sequence ID:" + changed_boot_sequences_id)
 
    # pdb.set_trace();
    element = ve_test.milestones.getElement([("screen_name", "notification", "==")])
     
    ve_test.log_assert(element, "notification message not found on screen")
     
    notification_title = ve_test.milestones.get_dic_value_by_key('DIC_MESSAGE_ERROR_TITLE')
     
    # logging.info('dump element == Error: %s ' % json.dumps(element))
    # {u'button_name_0': u'RETRY', u'button_name_1': u'HOME', u'screen_name': u'NotificationView', u'msg_title': u'Error', u'foc_action': u'RETRY', u'msg_text': u'Failed to start.', u'button_nb': 2, u'msg_error': u'ERR-'}
    ve_test.log_assert(element['msg_title'] == notification_title, "incorrect notification title " + str(element['msg_title']) + " instead of " + notification_title)
   
    ve_test.milestones.changeSettings(json.dumps([pref_keyword, boot_sequences_id]))
   
    ve_test.end()
