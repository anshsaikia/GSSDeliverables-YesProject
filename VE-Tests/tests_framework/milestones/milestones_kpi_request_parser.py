class KpiRequestParserAPI(object):

    def __init__(self, request):
        self.request = request

    def getSuccessPlaybackNb(self):
        try:
            return self.request["playbackSummary"]["playbackStatus"]["playbackSuccessNb"]
        except:
            return 0

    def getFailedPlaybackNb(self):
        try:
            return self.request["playbackSummary"]["playbackStatus"]["playbackFailedNb"]
        except:
            return 0

    def getPlaybackNb(self):
        try:
            return self.request["playbackSummary"]["playbackStatus"]["playbackNb"]
        except:
            return 0

    def getMinPlaybackStartSequenceDuration(self):
        try:
            return self.request["playbackSummary"]["playbackStartSeqDuration"]["minPlaybackStartSeqDuration"]
        except:
            return 0

    def getMaxPlaybackStartSequenceDuration(self):
        try:
            return self.request["playbackSummary"]["playbackStartSeqDuration"]["maxPlaybackStartSeqDuration"]
        except:
            return 0

    def getAveragePlaybackStartSequenceDuration(self):
        try:
            return self.request["playbackSummary"]["playbackStartSeqDuration"]["averagePlaybackStartSeqDuration"]
        except:
            return 0

    def getInactivityDuration(self):
        try:
            return self.request["playbackSummary"]["inactivityDuration"]
        except:
            return 0

    def getCurrentPlaybackDuration(self):
        try:
            return self.request["playbackSummary"]["currentPlayback"]["currentStartSeqDuration"]
        except:
            return 0

    def getNetworkLinkLoss(self):
        try:
            return self.request["playbackSummary"]["networkEvents"]["lossLinkErrors"]
        except:
            return 0

    def getNetworkLinkUp(self):
        try:
            return self.request["playbackSummary"]["networkEvents"]["upLink"]
        except:
            return 0

    def getPlaybackErrors(self):
        try:
            return self.request["playbackSummary"]["playbackEvents"]["playbackErrors"]
        except:
            return 0

    def getPlaybackRecovery(self):
        try:
            return self.request["playbackSummary"]["playbackEvents"]["playbackRecovery"]
        except:
            return 0

    def getCurrentPlaybackAudioStatus(self):
        try:
            return self.request["zappingSummary"]["currentPlayback"]["currentAudioStatus"]
        except:
            return 0

    def getProfilesIds(self):
        try:
            return self.request["profilesSummary"]["profilesIds"]
        except:
            return []

    def getProfileCount(self,profileId):
        try:
            return self.request["profilesSummary"]["profiles"][profileId]["profileCount"]
        except:
            return 0

    def getProfileBitrate(self,profileId):
        try:
            return self.request["profilesSummary"]["profiles"][profileId]["profileBitrate"]
        except:
            return 0

    def getProfileResolution(self,profileId):
        try:
            return self.request["profilesSummary"]["profiles"][profileId]["profileResolution"]
        except:
            return ""

    def printAll(self):
        print("SuccessZappingNb          = " + str(self.getSuccessPlaybackNb()))
        print("FailedZappingNb           = " + str(self.getFailedPlaybackNb()))
        print("ZappingNb                 = " + str(self.getPlaybackNb()))

        print("MinZappingDuration        = " + str(self.getMinPlaybackStartSequenceDuration()))
        print("MaxZappingDuration        = " + str(self.getMaxPlaybackStartSequenceDuration()))
        print("AverageZappingDuration    = " + str(self.getAveragePlaybackStartSequenceDuration()))
        print("InactivityDuratio         = " + str(self.getInactivityDuration()))

        print("CurrentZappingDuration    = " + str(self.getCurrentPlaybackDuration()))
        print("CurrentZappingAudioStatus = " + str(self.getCurrentPlaybackAudioStatus()))

        print("NetworkLinkLoss = " + str(self.getNetworkLinkLoss()))
        print("NetworkLinkUp = " + str(self.getNetworkLinkUp()))
        print("PlaybackErrors = " + str(self.getPlaybackErrors()))
        print("PlaybackRecovery = " + str(self.getPlaybackRecovery()))
        
        ids = self.getProfilesIds()
        for myId in ids:
            print("")
            print("profile id            = " + str(myId))
            print("ProfileResolution     = " + str(self.getProfileResolution(myId)))
            print("ProfileBitrate        = " + str(self.getProfileBitrate(myId)))
            print("ProfileCount          = " + str(self.getProfileCount(myId)))



if __name__ == "__main__":

    print "----getLiveKpiMeasurement : Simulated request"
    request = {
                  "playbackSummary":
                  {
                      "playbackStatus":{"playbackSuccessNb":3,"playbackFailedNb":1,"playbackNb":4},
                      "playbackStartSeqDuration":{"minPlaybackStartSeqDuration":1000,"maxPlaybackStartSeqDuration":4000,"averagePlaybackStartSeqDuration":3000},
                      "currentPlayback":{"currentStartSeqDuration":2800,"currentAudioStatus":"PLAYED"},
                      "inactivityDuration":"1 day",
                      "NetworkEvents":{"lossLinkErrors":1,"upLink":1},
                      "PlaybackEvents":{"playbackErrors":2,"playbackRecovery":2}
                  },
                                
                   "profilesSummary":
                  {
                       "profilesIds":['0', '3'],
                       "profiles": 
                       {
                           "3":{"profileResolution":"300X300","profileBitrate":980000,"profileCount":3},
                           "0":{"profileResolution":"300X360","profileBitrate":6980000,"profileCount":1},
                       }
                  },
              }

    milestones = KpiRequestParserAPI(request)
    milestones.printAll()

