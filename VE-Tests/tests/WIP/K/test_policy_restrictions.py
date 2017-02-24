from tests_framework.ve_tests.ve_test import VeTestApi

GEO_RESTRICTED_IP = '192.2.22.3'
ON_NET_ASN = '31334'

ZONE_BLACKLISTED = 'Restrict:Blacklist-IP'
ZONE_GEO_ALLOWED = "Allow:Geo-Location"
ZONE_ONNET_ALLOWED = "Allow:SP-OnNet"
ZONE_NETWORK_TYPE = "Requires:WiFi"
ZONE_IN_HOME="Check:In-Home"
ZONE_CITY_ALLOWED = "Allow:City"

SUBNET = 'SubNet'
COUNTRY_CODE = 'CountryCode'
ASN = 'ASN'
CITY = 'City'

TIMEOUT = 5
REFRESH_TIME = 20

# Update LCS and change the country code
# Verify whether the Video is restricted or not
def test_geo_location_restrict():
    ve_test = VeTestApi("main_hub:test_geo_restriction")
    ve_test.begin()

    zaplist = ve_test.screens.zaplist
    milestones = ve_test.milestones
    config = ve_test.configuration
    channel_id, channel_prop = ve_test.he_utils.getLinearContentABR('any')
    service_id = channel_prop['id']

    try:
        # Updating LCS with a country code, that doesn't exist. By doing this all country will be restricted
        ve_test.he_utils.setZoneGroup(ve_test, config, service_id, 'LINEAR', ZONE_GEO_ALLOWED, COUNTRY_CODE, ['ZZ'])
        ve_test.wait(REFRESH_TIME)
        zaplist.tune_to_channel_by_sek(channel_id, False)
        ve_test.wait(TIMEOUT)

        # Verify the playback status of the content
        ve_test.screens.playback.verify_streaming_stopped()

        # Verify the Notification message displayed correctly
        geo_block_message = ve_test.milestones.get_dic_value_by_key("DIC_ERROR_PLAYBACK_GEO_LOCATION",type="error")
        element = ve_test.milestones.getElement([('title_text', geo_block_message, '==')])
        ve_test.log_assert(element is not None, "Geolocation error message not matched")
    finally:
        # Remove the changes made
        ve_test.he_utils.removeZoneGroup(ve_test, config, service_id, 'LINEAR')

    ve_test.end()

def test_city_restrict():
    ve_test = VeTestApi("main_hub:test_city_restriction")
    ve_test.begin()
    
    zaplist = ve_test.screens.zaplist
    milestones = ve_test.milestones
    config = ve_test.configuration
    channel_id, channel_prop = ve_test.he_utils.getLinearContentABR('any')
    service_id = channel_prop['id']    
    
    try:
        # Updating LCS with a country code, that doesn't exist. By doing this all country will be restricted
        ve_test.he_utils.setZoneGroup(ve_test, config, service_id, 'LINEAR', ZONE_CITY_ALLOWED, CITY, ['ZZ'])
        ve_test.wait(REFRESH_TIME)
        zaplist.tune_to_channel_by_sek(channel_id, False)
        ve_test.wait(REFRESH_TIME)
        
        # Verify the playback status of the content
        ve_test.screens.playback.verify_streaming_stopped()
        
        # Verify the Notification message displayed correctly
        city_blocked_msg =  ve_test.milestones.get_dic_value_by_key("DIC_ERROR_PLAYBACK_DEVICE_OUT_OF_CITY")
        element = ve_test.milestones.getElement([('title_text', city_blocked_msg, '==')])
        ve_test.log_assert( element is not None , "City blocked error message not matched")
    finally:
        # Remove the changes made
        ve_test.he_utils.removeZoneGroup(ve_test, config, service_id, 'LINEAR')
    
    ve_test.end()


# Update LCS with the device's network subnet
# Verify whether the subnet is restricted from viewing the video or not
def test_blacklisted_ip():
    ve_test = VeTestApi("main_hub:test_blacklisted_ip")
    ve_test.wait(TIMEOUT)
    ve_test.begin()

    zaplist = ve_test.screens.zaplist
    milestones = ve_test.milestones
    config = ve_test.configuration
    channel_id, channel_prop = ve_test.he_utils.getLinearContentABR('any')
    service_id = channel_prop['id']
    # Create the network subnet
    device_ip = milestones.getDeviceDetails()["network-wifi-ip"]
    ip_subnet = "%s/16" % device_ip
    try:
        # Update LCS to blacklist the sub-net
        ve_test.he_utils.setZoneGroup(ve_test, config, service_id, 'LINEAR', ZONE_BLACKLISTED, SUBNET, [ip_subnet])
        ve_test.wait(REFRESH_TIME)
        zaplist.tune_to_channel_by_sek(channel_id, False)
        ve_test.wait(TIMEOUT)

        # Verify the playback status of the content
        ve_test.screens.playback.verify_streaming_stopped()

        # Verify the Notification message displayed correctly
        block_message = ve_test.milestones.get_dic_value_by_key("DIC_ERROR_PLAYBACK_BLACKLISTED",type="error")
        element = ve_test.milestones.getElement([('title_text',block_message, '==')])
        ve_test.log_assert(element is not None, "blacklist error message not matched")

    finally:
        # Remove the changes made
        ve_test.he_utils.removeZoneGroup(ve_test, config, service_id, 'LINEAR')
    ve_test.end()

def test_network_type_check_allow():
    ve_test = VeTestApi("main_hub:test_network_type_check_allow")
    ve_test.begin()

    zaplist = ve_test.screens.zaplist
    milestones = ve_test.milestones
    config = ve_test.configuration
    channel_id, channel_prop = ve_test.he_utils.getLinearContentABR('any')
    service_id = channel_prop['id']

    try:
        # Updating LCS with the correct ASN
        ve_test.he_utils.setZoneGroup(ve_test, config, service_id, 'LINEAR', ZONE_NETWORK_TYPE, COUNTRY_CODE, [])
        ve_test.wait(REFRESH_TIME)
        zaplist.tune_to_channel_by_sek(channel_id, False)
        ve_test.wait(TIMEOUT)
        # Verify whether the device is allowed to view the video or not
        ve_test.screens.playback.verify_streaming_playing()
    finally:
        # Remove the changes made
        ve_test.he_utils.removeZoneGroup(ve_test, config, service_id, 'LINEAR')
    ve_test.end()

#SPNET E2E
def test_on_net_restrict_new():
    ve_test = VeTestApi("main_hub:test_off_net")
    ve_test.begin()

    # Getting the device's ASN
    device_ip = ve_test.milestones.getDeviceDetails()["network-wifi-ip"]
    config = ve_test.configuration
    asn = ve_test.he_utils.getAttribute(ve_test, config, device_ip, "asn")

    zaplist = ve_test.screens.zaplist
    milestones = ve_test.milestones
    config = ve_test.configuration
    channel_id, channel_prop = ve_test.he_utils.getLinearContentABR('any')
    service_id = channel_prop['id']

    try:

        ve_test.he_utils.setZoneGroup(ve_test, config, service_id, 'LINEAR', ZONE_ONNET_ALLOWED, ASN, [str(int(asn) + 1)])
        ve_test.wait(REFRESH_TIME)
        ve_test.screens.zaplist.tune_to_channel_by_sek(channel_id, False)
        ve_test.wait(TIMEOUT)

        # Verify the playback status of the content
        ve_test.screens.playback.verify_streaming_stopped()

        # Verify the Notification message displayed correctly
        block_message = ve_test.milestones.get_dic_value_by_key("DIC_ERROR_PLAYBACK_OFF_NETWORK",type="error")
        element = ve_test.milestones.getElement([('title_text', block_message, '==')])
        ve_test.log_assert(element is not None, "off net error message not matched")

    finally:
        # Remove the changes made
        ve_test.he_utils.removeZoneGroup(ve_test, config, service_id, 'LINEAR')
    ve_test.end()


#INHOME E2E
def test_in_home_out_home():
    ve_test = VeTestApi("main_hub:test_in_home_out_home")
    ve_test.begin()

    # Getting the device's ASN
    device_ip = ve_test.milestones.getDeviceDetails()["network-wifi-ip"]
    config = ve_test.configuration
    asn = ve_test.he_utils.getAttribute(ve_test, config, device_ip, "asn")
    CHANNEL_ID, channel_prop = ve_test.he_utils.getLinearContentABR('any')
    SERVICE_ID = channel_prop['id']

    try:

        #Combining INHOME & GEO Policy, New Flag, ZONE_IN_HOME_GEO
        ve_test.he_utils.setZoneGroup(ve_test, config, SERVICE_ID, 'LINEAR', ZONE_IN_HOME, ASN,[str(int(asn))] )
        ve_test.wait(REFRESH_TIME)
        ve_test.screens.zaplist.tune_to_channel_by_sek(CHANNEL_ID, False)
        ve_test.wait(TIMEOUT)

        # Verify the playback status of the content
        ve_test.screens.playback.verify_streaming_stopped()

        # Verify the Notification message displayed correctly
        block_message = ve_test.milestones.get_dic_value_by_key("DIC_ERROR_PLAYBACK_DEVICE_OUT_OF_HOME",type="error")
        element = ve_test.milestones.getElement([('title_text', block_message, '==')])
        ve_test.log_assert(element is not None, "in home/out home error message not matched")

    finally:
        # Remove the changes made
        ve_test.he_utils.removeZoneGroup(ve_test, config, SERVICE_ID, 'LINEAR')
    ve_test.end()