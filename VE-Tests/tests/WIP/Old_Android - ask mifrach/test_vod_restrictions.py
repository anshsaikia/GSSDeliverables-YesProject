__author__ = 'sridv'

import json
import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition
from tests_framework.he_utils.he_utils import VodContentType

TIMEOUT = 5
REFRESH_TIME = 30

# Update LCS by setting the country code to an invalid value
# Verify the restriction of video with geo-location restriction error msg.
# This test case also checks priority of geo location restriction over off net restriction.
@pytest.mark.MF1409_1410_1197_VoD_Content_Restriction
@pytest.mark.MF1409_1410_1197_VoD_Content_Restriction_regression
def test_vod_geo_location_restrict():
    ve_test = VeTestApi("main_hub:test_vod_geo_location_restrict")
    ve_test.begin()
    he_utils = ve_test.he_utils

    config = ve_test.configuration
    asset = ve_test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.ENCRYPTED, VodContentType.LOW_RATED], {'policy':'false'})

    #PDS modification
    uri_param='geoLocation'
    pds_response=ve_test.he_utils.getPSDresponse(config,uri_param )
    pds_response_modified='[{"contentType":["SVOD","TVOD"],"deviceType":"COMPANION","definition": {"EQ": ["inCountry", "true"]}}]'
    ve_test.he_utils.setPSDrequest(config, uri_param, pds_response_modified)

    try:
        # Updating LCS with a country code, that doesn't exist. By doing this, every country will be restricted
        he_utils.setZoneGroup(ve_test, config, he_utils.ZONE_NAME_GLOBAL, 'VOD', he_utils.ZONE_GEO_ALLOWED, he_utils.COUNTRY_CODE, ['ZZ'])
        ve_test.wait(REFRESH_TIME)

        ve_test.screens.store.play_vod_by_title(asset['title'], False)
        ve_test.wait(TIMEOUT)

        # Verify that the video is restricted i.e., playback of the content is stopped
        ve_test.screens.playback.verify_streaming_stopped()

        # Verify that the notification message is displayed correctly
        notification = ve_test.screens.notification
        notification.verify_notification_message_by_key('DIC_ERROR_PLAYBACK_GEO_LOCATION')

    finally:
        # Removing geo-location based restriction
        he_utils.removeZoneGroup(ve_test, config, he_utils.ZONE_NAME_GLOBAL, 'VOD')
        he_utils.setZoneGroup(ve_test, config, he_utils.ZONE_NAME_GLOBAL, 'VOD', he_utils.ZONE_GEO_ALLOWED, he_utils.COUNTRY_CODE, ['.*'])
        ve_test.wait(REFRESH_TIME)
        #set PDS values        
        ve_test.he_utils.setPSDrequest(config, uri_param, json.dumps(pds_response))
        
        ve_test.screens.store.play_vod_by_title(asset['title'])
        ve_test.wait(TIMEOUT)
              
        # Verify that the video is allowed
        ve_test.screens.playback.verify_streaming_playing()

    ve_test.end()

# Update LCS with an ASN that doesn't exist
# Verify the restriction of video with off-net error msg
@pytest.mark.MF1409_1410_1197_VoD_Content_Restriction
def test_vod_off_net_restrict():
    ve_test = VeTestApi("main_hub:test_vod_off_net_restrict")
    ve_test.begin()
    he_utils = ve_test.he_utils

    milestones = ve_test.milestones
    config = ve_test.configuration
    asset = ve_test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.ENCRYPTED, VodContentType.LOW_RATED], {'policy':'false'})

    #PDS modification
    uri_param='network'
    pds_response=ve_test.he_utils.getPSDresponse(config,uri_param )
    pds_response_modified='[ {"contentType": ["SVOD","TVOD"], "serviceProvider": ["'+asset['provider']+'"],"deviceType":"COMPANION","definition": {"AND": {"EQ-1": ["networkType","wifi" ],"EQ-2": ["onSPNet","true" ],"NE-1": ["blacklist","true" ] }}}]'
    ve_test.he_utils.setPSDrequest(config, uri_param, pds_response_modified)
     
    # Getting the device's ASN
    device_ip = milestones.getDeviceDetails()["network-wifi-ip"]
    asn = he_utils.getZoneAttribute(ve_test, config, device_ip, "asn")
    try:
        # Updating LCS with an ASN that doesn't exist, thereby restricting all SP
        he_utils.setZoneGroup(ve_test, config, he_utils.ZONE_NAME_GLOBAL, 'VOD', he_utils.ZONE_ONNET_ALLOWED, he_utils.ASN, [str(int(asn) + 1)])
        ve_test.wait(REFRESH_TIME)

        ve_test.screens.store.play_vod_by_title(asset['title'], False)
        ve_test.wait(TIMEOUT)

        # Verify that the video is restricted i.e., playback of the content is stopped
        ve_test.screens.playback.verify_streaming_stopped()

        # Verify that the notification message is displayed correctly
        notification = ve_test.screens.notification
        notification.verify_notification_message_by_key('DIC_ERROR_PLAYBACK_OFF_NETWORK')

    finally:
        # Removing off net content restriction
         he_utils.removeZoneGroup(ve_test, config, he_utils.ZONE_NAME_GLOBAL, 'VOD')
         he_utils.setZoneGroup(ve_test, config, he_utils.ZONE_NAME_GLOBAL, 'VOD', he_utils.ZONE_ONNET_ALLOWED, he_utils.ASN, ['.*'])
         ve_test.wait(REFRESH_TIME)
         
         #set PDS values
         ve_test.he_utils.setPSDrequest(config, uri_param,json.dumps(pds_response))
         
         ve_test.screens.store.play_vod_by_title(asset['title'])
         ve_test.wait(TIMEOUT)
                 
        # Verify that the video is allowed
         ve_test.screens.playback.verify_streaming_playing()

    ve_test.end()

# Update LCS by setting blacklisted IP to the device's network subnet
# Verify that the video is restricted with blacklist ip error msg
@pytest.mark.MF1409_1410_1197_VoD_Content_Restriction
def test_vod_blacklisted_ip():
    ve_test = VeTestApi("main_hub:test_vod_blacklisted_ip")
    ve_test.begin()
    he_utils = ve_test.he_utils

    milestones = ve_test.milestones
    config = ve_test.configuration
    asset = ve_test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.ENCRYPTED, VodContentType.LOW_RATED], {'policy':'false'})

    #PDS modification
    uri_param='network'
    pds_response=ve_test.he_utils.getPSDresponse(config,uri_param )
    pds_response_modified='[ {"contentType":["SVOD","TVOD"], "serviceProvider": ["'+asset['provider']+'"],"deviceType":"COMPANION","definition": {"AND": {"EQ-1": ["networkType","wifi" ],"EQ-2": ["onSPNet","true" ],"NE-1": ["blacklist","true" ] }}}]'
    
    ve_test.he_utils.setPSDrequest(config, uri_param, pds_response_modified)
    # Create the network subnet
    device_ip = milestones.getDeviceDetails()["network-wifi-ip"]
    ip_subnet = "%s/16" % device_ip
    try:
        # Update LCS to blacklist the device's sub-net
        he_utils.setZoneGroup(ve_test, config, he_utils.ZONE_NAME_GLOBAL, 'VOD', he_utils.ZONE_BLACKLISTED, he_utils.SUBNET, [ip_subnet])
        ve_test.wait(REFRESH_TIME)

        ve_test.screens.store.play_vod_by_title(asset['title'], False)
        ve_test.wait(TIMEOUT)

        # Verify that the video is restricted i.e., playback of the content is stopped
        ve_test.screens.playback.verify_streaming_stopped()

        # Verify that the notification message is displayed correctly
        notification = ve_test.screens.notification
        notification.verify_notification_message_by_key('DIC_ERROR_PLAYBACK_BLACKLISTED')

    finally:
        # Removing subnet based content restriction
         he_utils.removeZoneGroup(ve_test, config, he_utils.ZONE_NAME_GLOBAL, 'VOD')
         he_utils.setZoneGroup(ve_test, config, he_utils.ZONE_NAME_GLOBAL, 'VOD', he_utils.ZONE_GEO_ALLOWED, he_utils.COUNTRY_CODE, ['.*'])
         ve_test.wait(REFRESH_TIME)
         #set PDS values
         ve_test.he_utils.setPSDrequest(config, uri_param, json.dumps(pds_response))
         
         ve_test.screens.store.play_vod_by_title(asset['title'])
         ve_test.wait(TIMEOUT)

        # Verify that the video is allowed
         ve_test.screens.playback.verify_streaming_playing()

    ve_test.end()
