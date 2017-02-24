from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KSTB.error import *

import pytest
import xml.etree.ElementTree as ET
import requests
from time import sleep
import logging

GEO_RESTRICTED_IP = '192.2.22.3'
ON_NET_ASN = '31334'

ZONE_BLACKLISTED = 'Restrict:Blacklist-IP'
ZONE_GEO_ALLOWED = "Allow:Geo-Location"
ZONE_ONNET_ALLOWED = "Allow:SP-OnNet"
ZONE_NETWORK_TYPE = "Requires:WiFi"

SUBNET = 'SubNet'
COUNTRY_CODE = 'CountryCode'
ASN = 'ASN'

CHANNEL_ID = "7"
SERVICE_ID = "7_abr"
TIMEOUT = 5
REFRESH_TIME = 20


# Update LCS and change the country code
# Verify whether the Video is restricted or not
@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_geo_location_restrict():
    ve_test = VeTestApi("test_geo_localisation")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    zaplist = ve_test.screens.zaplist     
    milestones = ve_test.milestones
    config = ve_test.configuration 
    removed = False   

    try:
        #zapping on the channelid
        zaplist.to_zaplist_from_fullscreen()
        status = zaplist.tune_to_channel_by_sek(CHANNEL_ID, True, True)
        if not status:
            ve_test.log_assert(status, 'Failed to tune by the Zaplist')

        ve_test.wait(TIMEOUT)

        # Updating LCS with a country code, that doesn't exist. By doing this all country will be restricted
        setZoneGroup(ve_test, config, SERVICE_ID, 'LINEAR', ZONE_GEO_ALLOWED, COUNTRY_CODE, ['ZZ'])
        ve_test.wait(REFRESH_TIME)

        ve_test.appium.key_event("KEYCODE_DPAD_UP")
        ve_test.wait(TIMEOUT)

        #zapping on the channelid
        ve_test.appium.key_event("KEYCODE_DPAD_DOWN")
        ve_test.wait(TIMEOUT)

        # Verify the playback status of the content
        ve_test.screens.playback.verify_streaming_stopped()
        ve_test.wait(TIMEOUT)

        # Verify the Notification message displayed correctly
        ve_test.check_notification_screen('shown', msg_code=E_STREAMING_GEO_LOC_ERROR_CODE,msg_text=E_STREAMING_GEO_LOC_ERROR_MSG)

        # Remove the zone
        removeZoneGroup(ve_test, config, SERVICE_ID, 'LINEAR')
        removed = True
        ve_test.wait(REFRESH_TIME)

        ve_test.appium.key_event("KEYCODE_DPAD_UP")
        ve_test.wait(TIMEOUT)


        ve_test.appium.key_event("KEYCODE_DPAD_DOWN")
        ve_test.wait(TIMEOUT)

        # Verify the Notification message displayed correctly
        ve_test.screens.playback.verify_streaming_playing()

    finally:
        if not removed:
            # Remove the changes made
            removeZoneGroup(ve_test, config, SERVICE_ID, 'LINEAR')

    ve_test.end()

# Update LCS with the device's network subnet
# Verify whether the subnet is restricted from viewing the video or not
@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_blacklisted_ip():
    ve_test = VeTestApi("test_geo_restriction")
    ve_test.wait(TIMEOUT)
    ve_test.begin(screen=ve_test.screens.fullscreen)

    zaplist = ve_test.screens.zaplist
    milestones = ve_test.milestones
    config = ve_test.configuration
    device_ip = getDeviceIP(ve_test)
    ip_subnet = "%s/16" % device_ip
    removed = False   

    try:
        #zapping on the channelid
        zaplist.to_zaplist_from_fullscreen()
        status = zaplist.tune_to_channel_by_sek(CHANNEL_ID, True, True)
        if not status:
            ve_test.log_assert(status, 'Failed to tune by the Zaplist')
        ve_test.wait(TIMEOUT)

        # Update LCS to blacklist the sub-net
        setZoneGroup(ve_test, config, SERVICE_ID, 'LINEAR', ZONE_BLACKLISTED, SUBNET, [ip_subnet])
        ve_test.wait(REFRESH_TIME)

        ve_test.appium.key_event("KEYCODE_DPAD_UP")
        ve_test.wait(TIMEOUT)

        #zapping on the channelid
        ve_test.appium.key_event("KEYCODE_DPAD_DOWN")
        ve_test.wait(TIMEOUT)

        # Verify the playback status of the content
        ve_test.screens.playback.verify_streaming_stopped()
        ve_test.wait(TIMEOUT)

        # Verify the Notification message displayed correctly
        ve_test.check_notification_screen('shown', msg_code=E_STREAMING_BLACKLIST_ERROR_CODE,msg_text=E_STREAMING_BLACKLIST_ERROR_MSG)


        # Remove the zone
        removeZoneGroup(ve_test, config, SERVICE_ID, 'LINEAR')
        removed = True
        ve_test.wait(REFRESH_TIME)

        ve_test.appium.key_event("KEYCODE_DPAD_UP")
        ve_test.wait(TIMEOUT)


        ve_test.appium.key_event("KEYCODE_DPAD_DOWN")
        ve_test.wait(TIMEOUT)

        # Verify the Notification message displayed correctly
        ve_test.screens.playback.verify_streaming_playing()

    finally:
        if not removed:
            # Remove the changes made
            removeZoneGroup(ve_test, config, SERVICE_ID, 'LINEAR')

    ve_test.end()

# Update the LCS with an ASN that doesn't exist
# Verify whether the device's ASN is restricted from viewing the video or not
@pytest.mark.F_Playback_Error
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_on_net_restrict():
    ve_test = VeTestApi("test_off_net")
    ve_test.begin(screen=ve_test.screens.fullscreen)

    zaplist = ve_test.screens.zaplist
    milestones = ve_test.milestones
    config = ve_test.configuration
    device_ip = getDeviceIP(ve_test)
    asn = getAttribute(ve_test, config, device_ip, "asn")
    removed = False   

    try:
        # zapping on the channelid
        zaplist.to_zaplist_from_fullscreen()
        status = zaplist.tune_to_channel_by_sek(CHANNEL_ID, True, True)
        if not status:
            ve_test.log_assert(status, 'Failed to tune by the Zaplist')
        ve_test.wait(TIMEOUT)

        # Updating with an ASN that doesn't exist, by doing so all other ASN will be restricted
        setZoneGroup(ve_test, config, SERVICE_ID, 'LINEAR', ZONE_ONNET_ALLOWED, ASN, [str(int(asn) + 1)])
        ve_test.wait(REFRESH_TIME)

        ve_test.appium.key_event("KEYCODE_DPAD_UP")
        ve_test.wait(TIMEOUT)

        #zapping on the channelid
        ve_test.appium.key_event("KEYCODE_DPAD_DOWN")
        ve_test.wait(TIMEOUT)

        # Verify the playback status of the content
        ve_test.screens.playback.verify_streaming_stopped()
        ve_test.wait(TIMEOUT)

        # Verify the Notification message displayed correctly
        ve_test.check_notification_screen('shown', msg_code=E_STREAMING_OFFNET_ERROR_CODE,msg_text=E_STREAMING_OFFNET_ERROR_MSG)

        # Remove the zone
        removeZoneGroup(ve_test, config, SERVICE_ID, 'LINEAR')
        removed = True
        ve_test.wait(REFRESH_TIME)

        ve_test.appium.key_event("KEYCODE_DPAD_UP")
        ve_test.wait(TIMEOUT)


        ve_test.appium.key_event("KEYCODE_DPAD_DOWN")
        ve_test.wait(TIMEOUT)

        # Verify the Notification message displayed correctly
        ve_test.screens.playback.verify_streaming_playing()

    finally:
        if not removed:
            # Remove the changes made
            removeZoneGroup(ve_test, config, SERVICE_ID, 'LINEAR')
        
    ve_test.end()


#find ip of the device from configuartion file
def getDeviceIP(ve_test):
    ip_path = ve_test.configuration["device"]["ip"]
    ip = ip_path.split(':')
    return ip[0]

# This method fetches the Notification View, if it exists
def get_notification(elements):
    notification = None
    for element in elements:
        if 'name' in element and element['name'] == 'NotificationView':
            notification = element
            break
    return notification

# This method wil update the LCS according to the arguments passed
def setZoneGroup(ve_test, config, zoneGroupName, zoneGroupProvider, zoneName, restriction_type, restrictValues, isAllowed = False):
    
    url = 'http://' + config['he']['lcsIP']

    url = url + '/loc/zone/ZoneGroup'
    headers = {'Content-Type': 'application/xml' }
    type_check = restriction_type in ['SubNet', 'MetroCode', 'PostalCode', 'State', 'CountryCode', 'ASN']
    ve_test.log_assert(type_check, "The given restriction_type is not present. Given %s: " % type_check)

    root = ET.Element("ZoneGroup")
    root.set("xmlns", "urn:com:cisco:videoscape:conductor:loc")
    root.set("name", zoneGroupName)
    root.set("provider", zoneGroupProvider)

    classifier = ET.SubElement(root, "Classifier")
    classifier.set("type", "SIMPLE")
    classifier.text = zoneGroupProvider + "." + zoneGroupName

    zone = ET.SubElement(root, "Zone")
    zone.set("name", zoneName)

    for value in restrictValues:
        subzone = ET.SubElement(zone, restriction_type)
        subzone.text = value
    if zoneName is ZONE_BLACKLISTED:
        zone = ET.SubElement(root, "Zone")
        zone.set("name", ZONE_GEO_ALLOWED)
        subzone = ET.SubElement(zone, COUNTRY_CODE)
        subzone.text = ".*"

        zone = ET.SubElement(root, "Zone")
        zone.set("name", ZONE_ONNET_ALLOWED)
        subzone = ET.SubElement(zone, ASN)
        subzone.text = ".*"

    elif zoneName is ZONE_ONNET_ALLOWED:
        zone = ET.SubElement(root, "Zone")
        zone.set("name", ZONE_GEO_ALLOWED)
        subzone = ET.SubElement(zone, COUNTRY_CODE)
        subzone.text = ".*"

    elif zoneName is ZONE_GEO_ALLOWED:
        zone = ET.SubElement(root, "Zone")
        zone.set("name", ZONE_ONNET_ALLOWED)
        subzone = ET.SubElement(zone, ASN)
        subzone.text = ON_NET_ASN

        if isAllowed:
            subzone.text = ".*"

        zone = ET.SubElement(root, "Zone")
        zone.set("name", ZONE_BLACKLISTED)
        subzone = ET.SubElement(zone, SUBNET)
        subzone.text = GEO_RESTRICTED_IP

    elif ZONE_NETWORK_TYPE is zoneName:
        # Finding the country code
        milestones = ve_test.milestones
        #device_ip = milestones.getDeviceDetails()["network-wifi-ip"]
        device_ip = getDeviceIP(ve_test)
        country_code = getAttribute(ve_test, config, device_ip, "countryCode")
        asn = getAttribute(ve_test, config, device_ip, "asn")
        zone = ET.SubElement(root, "Zone")
        zone.set("name", ZONE_GEO_ALLOWED)
        subzone = ET.SubElement(zone, COUNTRY_CODE)
        subzone.text = country_code

        zone = ET.SubElement(root, "Zone")
        zone.set("name", ZONE_ONNET_ALLOWED)
        subzone = ET.SubElement(zone, ASN)
        subzone.text = asn

    bodyContent = ET.tostring(root)
    lcsResponse = requests.post(url, data=bodyContent, headers=headers)
    response_result = lcsResponse.status_code == 204
    ve_test.log_assert(response_result, "LCS Response did not return 204, it returned %s" % lcsResponse.status_code)

# This method is used to remove the changes made
def removeZoneGroup(ve_test, config, zoneGroupName, zoneGroupProvider):
    url = 'http://' + config['he']['lcsIP']
    url = url + '/loc/zone/ZoneGroup/' + zoneGroupProvider + '/' + zoneGroupName

    response = requests.delete(url)
    response_result = response.status_code == 204
    ve_test.log_assert(response_result, "LCS Response did not return 204, it returned %s" % response.status_code)

# This method helps in fetching the LCS related data
def getAttribute(ve_test, config, deviceIP, attribute):
    url = 'http://' + config['he']['lcsIP']
    url = url + '/loc/ipvideo/Location?IpAddress=' + deviceIP
    response = requests.get(url)
    response_result = response.status_code == 200
    ve_test.log_assert(response_result, "LCS Response did not return 200, it returned %s" % response.status_code)
    xml_data = response.text
    root = ET.fromstring(xml_data)
    attributes = root.attrib
    ve_test.log_assert(attribute in attributes,
                       "Attribute %s is not present in response. Response: %s" % (attribute, xml_data))
    return attributes[attribute]
