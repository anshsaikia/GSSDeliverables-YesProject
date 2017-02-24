import pytest
import logging
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from tests_framework.ve_tests.ve_test import VeTestApi

def test_log_size():
        test = VeTestApi(title="logging_size")
        test.begin(login=test.login_types.none)
      
        test.milestones.purgeAllLogs()
        
        # little configuration of the logger, then start it
        test.milestones.setFileSizeMax(128)
        test.milestones.setUploadPeriod(100000) # Arbitraty value of 100 seconds
        test.milestones.activateUpload(True)
        
        test.wait(2)
        test.milestones.sendLog("This is, indeed, a pretty long log, if we compare it to the maximum size")
        numberOfLogs = test.milestones.getNumberOfSentLogs()
        test.log_assert(numberOfLogs == 1, "numberOfLogs = %i" % numberOfLogs) # 2 because when activated, the logger perform an upload

        test.wait(2)
        test.milestones.sendLog("This is, indeed, a pretty long log, if we compare it to the maximum size")
        numberOfLogs = test.milestones.getNumberOfSentLogs()
        test.log_assert(numberOfLogs == 2, "numberOfLogs = %i" % numberOfLogs)
        
        test.wait(2)
        test.milestones.sendLog("This is, indeed, a pretty long log, if we compare it to the maximum size")
        numberOfLogs = test.milestones.getNumberOfSentLogs()
        test.log_assert(numberOfLogs == 3, "numberOfLogs = %i" % numberOfLogs)
        
        test.milestones.purgeAllLogs()
        
        test.end()

def test_log_upload_period():
        test = VeTestApi(title="logging_upload_period")
        test.begin(login=test.login_types.none)
      
        test.milestones.purgeAllLogs()
        
        # little configuration of the logger, then start it
        test.milestones.setFileSizeMax(1024)
        test.milestones.setUploadPeriod(10000)
        test.milestones.activateUpload(True)
        
        test.wait(11)
        numberOfLogs = test.milestones.getNumberOfSentLogs()
        test.log_assert(numberOfLogs == 1, "numberOfLogs = %i" % numberOfLogs) # 2 because when activated, the logger perform an upload
        
        test.wait(11)
        numberOfLogs = test.milestones.getNumberOfSentLogs()
        test.log_assert(numberOfLogs == 2, "numberOfLogs = %i" % numberOfLogs)
        
        test.wait(11)
        numberOfLogs = test.milestones.getNumberOfSentLogs()
        test.log_assert(numberOfLogs == 3, "numberOfLogs = %i" % numberOfLogs)
        
        test.milestones.purgeAllLogs()
        
        test.end()
