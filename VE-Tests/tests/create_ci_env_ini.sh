#!/bin/sh
#
# NOTE:
# This will create a CI_Environment.ini file for you,
# or **overwrite** your exisiting file in case you already have it.
#
# Run this script under VE-Tests/tests directory
#

# usage:
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <lab> <K/KD> <Android/iOS>" >&2
    echo "E.g.:  $0 lwr-beta K Android" >&2
    exit 1
fi

# save arguments
OUTPUT_INI_FILE=CI_Environment.ini
lab=$1
project=$2
platform=$3

# create ini file
echo '[CI_VARIABLES]
; openstack server to use when vgwUtils is True in current profile
vlan.name=openstack-'$lab'

[USER_VARIABLES]
user.subscriptions=""
[profile]
; default profile to use. Use --profile <profile name> to use a different profile without changing configuration file
name='$project'
; location to put screenshots when test fail
screenshotDir=screenshots
; support for verbose output in log
verbose=True
; Android / iOS
platformName='$platform'

[NET]
; Do not use openstack server
vgwUtils=False
; Application to use
project=NET
; using net staging
lab=net-st.hercules.ciscolabs.com
; using fixed household, False for dynamic household
fixedHousehold=True
; household name to use
generated_household=dudu
; user name to use
generated_username=dudu
; password for household
password=123

[KD]
; use openstack server defined in vlan.name
vgwUtils=True
; application to use
project=KD

[K]
; use openstack server defined in vlan.name
vgwUtils=True
; application to use
project=HAPPY
' > $OUTPUT_INI_FILE
