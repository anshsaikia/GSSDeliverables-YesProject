from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.he_utils.he_utils import VodContentType
from tests_framework.ui_building_blocks.KD.notification import Notification
import fabric.api as fab

inHomeRestrictedChannel = '503'
nonRestrictedChannel = '504'

def networks(net_info):
    return {
        "inHomeWifi":  {"name": net_info['in_home_router_ssid'],  "password": net_info['in_home_router_passwd'],
                       "routerIp": net_info['in_home_router_ip'] + ":" + net_info['in_home_router_appium_port']},

        "outHomeWifi": {"name": net_info['out_home_router_ssid'], "password": net_info['out_home_router_passwd'],
                        "routerIp": net_info['out_home_router_ip'] + ":" + net_info['out_home_router_appium_port']}
    }


def changeWifiNetwork(test, netType):
    deviceId = test.device_id
    wifiParams = networks(test.configuration['network'])[netType]
    fab.local("adb -s {0} shell am broadcast -a \"CHANGE_WIFI\" -n com.cisco.healthcheckapp/.HealthCheckRequestsHandler --es \"NETWORK_NAME\" {name} --es \"WIFI_PASSWORD\" {password}".format(deviceId, **wifiParams))
    test.wait(15)
    test.configuration['device']['ip'] = wifiParams['routerIp']


def test_proximity_to_stb_basic():
    fab.env.disable_known_hosts = True
    fab.env.password = 'erdk'

    ve_test = VeTestApi("proximity_check:test_proximity_to_stb_basic")

    fab.env.host_string = 'root@'+ve_test.configuration['network']['in_home_router_ip']
    fab.env.port = ve_test.configuration['network']['in_home_router_stb_ssh_port']
    fab.run("systemctl stop vgdrmprocess.service")
    ve_test.wait(5)
    ve_test.begin()
    ve_test.log_assert('drm-sac4-proximity' in ve_test.milestones.getProximityInfo(), "sac4 is not enabled")
    ve_test.log_assert(not ve_test.milestones.getProximityInfo()['drm-sac4-proximity'], "Have proximity when shouldn't")
    fab.run("systemctl start vgdrmprocess.service")
    ve_test.wait(40)

    ve_test.log_assert(ve_test.milestones.getProximityInfo()['drm-sac4-proximity'], "Didn't get proximity")
    ve_test.end()


def test_proximity_stb_shutdown_20_minutes():
    fab.env.disable_known_hosts = True
    fab.env.password = 'erdk'

    ve_test = VeTestApi("proximity_check:test_proximity_stb_shutdown_20_minutes")

    fab.env.host_string = 'root@'+ve_test.configuration['network']['in_home_router_ip']
    fab.env.port = ve_test.configuration['network']['in_home_router_stb_ssh_port']

    ve_test.begin()
    ve_test.log_assert('drm-sac4-proximity' in ve_test.milestones.getProximityInfo(), "sac4 is not enabled")
    ve_test.wait(5)
    ve_test.log_assert(ve_test.milestones.getProximityInfo()['drm-sac4-proximity'], "Didn't get proximity")
    #fab.run("shutdown -H now", warn_only=True)
    ve_test.log("Simulating shutdown by stopping vgdrmproccess")
    fab.run("systemctl stop vgdrmprocess.service")
    ve_test.wait(60*21)  # waiting for 21 minutes
    ve_test.log_assert(not ve_test.milestones.getProximityInfo()['drm-sac4-proximity'], "Have proximity when shouldn't")

    ve_test.end()


def test_proximity_stb_have_proximity_25_minutes():
    ve_test = VeTestApi("proximity_check:test_proximity_stb_have_proximity_25_minutes")
    ve_test.begin()
    ve_test.log_assert('drm-sac4-proximity' in ve_test.milestones.getProximityInfo(), "sac4 is not enabled")
    ve_test.wait(5)
    ve_test.log_assert(ve_test.milestones.getProximityInfo()['drm-sac4-proximity'], "Didn't get proximity")

    for i in range(1, 25):
        ve_test.log_assert(ve_test.milestones.getProximityInfo()['drm-sac4-proximity'], "Didn't get proximity")
        ve_test.wait(60)

    ve_test.end()


def test_proximity_to_stb_change_network():
    ve_test = VeTestApi("proximity_check:test_proximity_to_stb_change_network")

    changeWifiNetwork(ve_test, 'inHomeWifi')
    ve_test.begin()
    ve_test.wait(10)
    ve_test.log_assert('drm-sac4-proximity' in ve_test.milestones.getProximityInfo(), "sac4 is not enabled")
    ve_test.log_assert(ve_test.milestones.getProximityInfo()['drm-sac4-proximity'], "Didn't get proximity")

    changeWifiNetwork(ve_test, 'outHomeWifi')
    ve_test.log_assert('drm-sac4-proximity' in ve_test.milestones.getProximityInfo(), "No sac4 response from selenium")
    ve_test.log_assert(not ve_test.milestones.getProximityInfo()['drm-sac4-proximity'], "Have proximity when shouldn't")

    changeWifiNetwork(ve_test, 'inHomeWifi')
    ve_test.log_assert(ve_test.milestones.getProximityInfo()['drm-sac4-proximity'], "Didn't get proximity")

    ve_test.end()


def test_enforce_out_home_linear_verify_keepAlive_on_network_change():
    """
    US19840: Given that the device status is in-home, when I am already tuned to channel A (restricted only to in-home) and the
    device status changes to out of home, then error message appears immediately
    """
    ve_test = VeTestApi("proximity_check:test_enforce_out_home_linear_verify_keepAlive_on_network_change")

    changeWifiNetwork(ve_test, 'inHomeWifi')
    ve_test.begin()
    ve_test.wait(10)
    ve_test.log_assert('drm-sac4-proximity' in ve_test.milestones.getProximityInfo(), "sac4 is not enabled")

    channel_id = ve_test.he_utils.services[inHomeRestrictedChannel]['serviceEquivalenceKey']
    ve_test.screens.zaplist.tune_to_channel_by_sek(channel_id, verify_streaming_started=True)

    ve_test.wait(10)
    changeWifiNetwork(ve_test, 'outHomeWifi')
    ve_test.log_assert('drm-sac4-proximity' in ve_test.milestones.getProximityInfo(), "No sac4 response from selenium")
    ve_test.wait(10)
    notification = ve_test.screens.notification
    notification.verify_notification_message_by_key("DIC_ERROR_PLAYBACK_DEVICE_OUT_OF_HOME")

    ve_test.end()


def test_enforce_out_home_linear_verify_nonRestricted_on_network_change():
    """
    US19840: Given that the device status is in-home, when I am already tuned to channel B (Not restricted to in home) and the
    device status changes to out-of-home, then I continue watching the content
    """
    ve_test = VeTestApi("proximity_check:test_enforce_out_home_linear_verify_nonRestricted_on_network_change")

    changeWifiNetwork(ve_test, 'inHomeWifi')
    ve_test.begin()
    ve_test.wait(10)
    ve_test.log_assert('drm-sac4-proximity' in ve_test.milestones.getProximityInfo(), "sac4 is not enabled")

    channel_id = ve_test.he_utils.services[nonRestrictedChannel]['serviceEquivalenceKey']
    ve_test.screens.zaplist.tune_to_channel_by_sek(channel_id, verify_streaming_started=True)

    ve_test.wait(10)
    changeWifiNetwork(ve_test, 'outHomeWifi')
    ve_test.log_assert('drm-sac4-proximity' in ve_test.milestones.getProximityInfo(), "No sac4 response from selenium")
    ve_test.wait(10)
    ve_test.screens.playback.verify_streaming_playing()

    ve_test.end()


def test_enforce_out_home_linear_channel_change():
    """
    US18889:
    1. Given that I boot the app and device's status is out of-home, when I tune to last viewed channel (restricted only
    to in-home), then I get error message
    2. Given that the device's status is out of home, when I channel change to channel A (restricted only to in-home),
    then I get error message notification
    3. Given that the device's status is out of home, when I channel change to channel B (Not restricted to in home),
    then I can view the content
    4. Given that an out of home error was raised, when I navigate to another channel (not restricted to in-home), then
    I can view the content
    5. Given that an out of home error was raised, when I navigate to another channel (restricted to in-home), then same
    error message is raised again.
    """
    ve_test = VeTestApi("proximity_check:test_enforce_out_home_linear_verify_nonRestricted_on_network_change")

    # step 1 (+2 ?)
    changeWifiNetwork(ve_test, 'outHomeWifi')
    ve_test.begin()
    ve_test.wait(10)
    ve_test.log_assert('drm-sac4-proximity' in ve_test.milestones.getProximityInfo(), "sac4 is not enabled")

    channel_id = ve_test.he_utils.services[inHomeRestrictedChannel]['serviceEquivalenceKey']
    ve_test.screens.zaplist.tune_to_channel_by_sek(channel_id, verify_streaming_started=False)
    ve_test.wait(10)
    notification = ve_test.screens.notification
    notification.verify_notification_message_by_key("DIC_ERROR_PLAYBACK_DEVICE_OUT_OF_HOME")

    # step 3+4 (intentionally before 2)
    channel_id = ve_test.he_utils.services[nonRestrictedChannel]['serviceEquivalenceKey']
    ve_test.screens.zaplist.tune_to_channel_by_sek(channel_id, verify_streaming_started=True)

    # step 5
    channel_id = ve_test.he_utils.services[inHomeRestrictedChannel]['serviceEquivalenceKey']
    ve_test.screens.zaplist.tune_to_channel_by_sek(channel_id, verify_streaming_started=False)
    ve_test.wait(10)
    notification = ve_test.screens.notification
    notification.verify_notification_message_by_key("DIC_ERROR_PLAYBACK_DEVICE_OUT_OF_HOME")

    ve_test.end()


def test_enforce_out_home_vod():

    ve_test = VeTestApi("proximity_check:test_enforce_out_home_vod")
    changeWifiNetwork(ve_test, 'inHomeWifi')

    ve_test.begin()
    he_utils = ve_test.he_utils

    config = ve_test.configuration
    start_vod_play(ve_test,False)
    ve_test.wait(10)
    changeWifiNetwork(ve_test, 'outHomeWifi')
    ve_test.wait(10)
    notification = ve_test.screens.notification
    notification.verify_notification_message_by_key("DIC_ERROR_PLAYBACK_DEVICE_OUT_OF_HOME")


def start_vod_play(ve_test, is_playback):
    action_menu = ve_test.screens.vod_action_menu
    asset = ve_test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.ENCRYPTED, VodContentType.LOW_RATED], {'policy':'false'})
    ve_test.log_assert('title' in asset and asset['title'], "Unable to get a VOD content")
    ve_test.screens.store.play_vod_by_title(asset['title'])
    ve_test.screens.store.navigate_to_vod_asset_by_title(asset['title'])
    ve_test.wait(10)
    action_menu.play_asset()
    ve_test.wait(10)
    ve_test.screens.playback.verify_streaming_playing()

