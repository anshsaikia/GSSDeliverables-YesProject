import sys
import json
import requests
import subprocess
from commands import getstatusoutput

__author__ = 'gekatz'

def usage(reason):
    if(reason): print reason
    print "Usage: upload_hockeyapp.py <platform><release_type><Hockeyapp Token><App path><dSym path><Notes>"
    assert 0


def checkArguments():

    if len(sys.argv) < 7:
        usage("Wrong arguments")


def create_app(title, bundle_id, platform, release_type, haToken):
    if title and bundle_id and platform:
        payload = {"title": title, "bundle_identifier": bundle_id, "platform": platform}

        if release_type:
            payload.__setitem__("release_type", release_type)

        headers = {"X-HockeyAppToken": haToken}
        resp = requests.post("https://rink.hockeyapp.net/api/2/apps/new",
                             data=payload, headers=headers)
        return resp.json()["public_identifier"]


def find_app(title, bundle_id, platform, release_type, haToken):
        appId = None
        headers = {"X-HockeyAppToken": haToken}
        resp = requests.get("https://rink.hockeyapp.net/api/2/apps", headers=headers)

        apps = resp.json()["apps"]

        for app in apps:
            if app["title"] == title and \
               app["bundle_identifier"] == bundle_id and \
               str(app["release_type"]) == release_type and \
               app["platform"] == platform:
                appId = app["public_identifier"]
                break
        return appId


def update_version(version, haToken, appPath, appId):
    payload = {"status": "2", "notify": "1"}
    headers = {"X-HockeyAppToken": haToken}
    files = {"ipa": "@" + appPath}

    #print payload["ipa"]
    if version and appPath:
        print "Upload build: " + str(version) + ", appPath: " + appPath + ", url: https://rink.hockeyapp.net/api/2/apps/" + appId + "/app_versions/" + str(version)
   #     res = requests.put("https://rink.hockeyapp.net/api/2/apps/" + appId + "/app_versions/" + str(version),
   #                  data=payload, headers=headers, files=files)
   #     print res.json()

        res = getstatusoutput("curl "\
                        "-F 'status=2' "
                        "-F 'notify=1' "
                        "-F 'notes=Some new features and fixed bugs.' "
                        "-F 'notes_type=0' "
                        "-F 'ipa=@" + appPath + "' "
                        "-H 'X-HockeyAppToken: " + haToken + "' "
                        "https://rink.hockeyapp.net/api/2/apps/" + appId + "/app_versions/upload")

def upload_app(haToken, appPath, dsymPath, notes):

        res = getstatusoutput("curl "\
                        "-F 'status=2' "
                        "-F 'notify=1' "
                        "-F 'notes=" + notes + "' "
                        "-F 'notes_type=0' "
                        "-F 'ipa=@" + appPath + "' "
                        "-F 'dsym=@" + dsymPath + "' "
                        "-H 'X-HockeyAppToken: " + haToken + "' "
                        "https://rink.hockeyapp.net/api/2/apps/upload")

checkArguments()
upload_app(sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
