'''
Created on Jun 28, 2015

@author: rweinste
'''

import json
from time import time

class performance(object):
    start_time = None
    
    def __init__(self,test):
        self.test = test

    def start(self):
        self.start_time = time()
        pass
        
    def stop(self):
        stop_time = time()
        diff = stop_time - self.start_time
        return diff
            
    def verifylist(self, entry_list, percent, max_sec):
        verify_count = 0
        for entry in entry_list:
            if entry <= max_sec:
                verify_count = verify_count + 1
        verify_percent = verify_count * 100 / len(entry_list)
        assert verify_percent >= percent
