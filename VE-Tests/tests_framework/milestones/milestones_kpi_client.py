from milestones_client import MilestonesClient
import logging

# Utility constants
CC_TRACKS = { 'off' : '', 'cc1': 'cc1'}

class MilestonesKpiClient(MilestonesClient):

    def __init__(self, ve_test):
        MilestonesClient.__init__(self, ve_test)

    def getClientPlaybackStatus(self):
        return self.post_milestones_request("getClientPlaybackStatus")

    def getLiveKpiMeasurement(self):
        return self.post_milestones_request("getLiveKpiMeasurement")

    def getVodKpiMeasurement(self):
        return self.post_milestones_request("getVodKpiMeasurement")

    def compare(self, val1, val2, operator):
        if operator == "!=":
            return val1 != val2
        else :
            return MilestonesClient.compare(self, val1, val2, operator)
    