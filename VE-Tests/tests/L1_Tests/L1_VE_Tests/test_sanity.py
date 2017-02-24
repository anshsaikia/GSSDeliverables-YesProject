from tests_framework.ve_tests.ve_test import VeTestApi
import pytest


@pytest.mark.commit
@pytest.mark.level1
@pytest.mark.delivery_criteria
@pytest.mark.ve_tests_repo_delivery_criteria
def test_sanity_navigation():
    """navigate to all of the screen"""
    test = VeTestApi("test_sanity")
    test.begin(autoPin=True)
    screens = test.screens
    if test.supported_screens:
        screens.navigate(test.supported_screens)
    else:
        '''navigate to main screens'''
        mainScreens = [screens.main_hub,
                       screens.fullscreen,
                       screens.zaplist,
                       screens.timeline,
                       screens.guide]
        screens.navigate(mainScreens)

        '''navigate to extra screens'''
        extraScreens = [screens.linear_action_menu,
                        screens.vod_action_menu,
                        screens.settings,
                        screens.search,
                        screens.library,
                        screens.store]
        screens.navigate(extraScreens)
    test.end()


@pytest.mark.commit
@pytest.mark.level1
def test_sanity_playback_clear():
    """test_sanity_playback_clear"""
    test = VeTestApi("test_sanity_playback_clear")
    test.begin(screen=test.screens.zaplist, autoPin=True)

    playback = test.screens.playback
    playback_time=5
    # play clear content from zaplist
    playback.play_linear_clear_content(playback_time=playback_time, screen=test.screens.zaplist)

    test.end()


# with DRM playback
@pytest.mark.commit
@pytest.mark.level1
def test_sanity_playback_encrypted():
    """test_sanity_playback_encrypted"""
    test = VeTestApi("test_sanity_playback_encrypted")
    test.begin(screen=test.screens.zaplist, autoPin=True)

    playback = test.screens.playback
    playback_time=5
    # play encrypted content from zaplist
    playback.play_linear_encrypted_content(playback_time=playback_time, screen=test.screens.zaplist)

    test.end()


@pytest.mark.commit
@pytest.mark.level1
def test_sanity_deauthorize_encrypted_channel():
    """test_sanity_deauthorize_authorize_encrypted_channel"""
    test = VeTestApi("test_sanity_deauthorize_authorize_encrypted_channel")
    test.begin()

    # Set variables
    playback = test.screens.playback
    hh_id = test.configuration["he"]["generated_household"]
    services = test.he_utils.get_abr_linear_services_from_cmdc()
    subscription = {}

    # find encrypted channel and its offers
    encryptedChannelSek, encryptedChannel = test.he_utils.getLinearContentABR("encrypted")
    encryptedChannellcn = encryptedChannel['logicalChannelNumber']
    offersToRemove = encryptedChannel['offers']
    offersIds = list(set(offersToRemove))

    test.log('offersIds: %s' %offersIds)
    test.log('Tuning to channel: %s   with offers: %s' %(encryptedChannelSek, offersToRemove))
    test.log('tuning to channel %d before removing offers' % encryptedChannellcn)

    # play the encrypted content from zaplist
    test.screens.zaplist.tune_to_channel_by_sek(encryptedChannelSek)
    test.wait(5)

    # De-authorize encrypted channel from offers using BOA
    test.log('remove offers: %s' %offersToRemove)
    test.log('removing offers from channel %d' % encryptedChannellcn)

    for index in range(len(offersIds)):
        res = test.he_utils.getOfferDetails(offersIds[index])
        test.log('offerkey: %s' %(res['offers'][0]['externalKey']))
        subscription[index] = res['offers'][0]['externalKey']
        test.log('subscription[index]: %s' % subscription[index])
        test.he_utils.deleteAuthorizationSubscriptionUsingBoa(hh_id, subscription[index], "KD-SERVICES")

    test.wait(5)

    # tune to another channel  - go out of encrypted channel, then will return to it to verify offer deauthorized
    test.log('Tuning to another channel - go out of encrypted channel to verify offer deauthorized')
    test.screens.zaplist.scroll_channels(2)
    elements = test.milestones.getElements()
    current_centered_event_view = test.screens.zaplist.get_centered_event_view(elements)
    test.appium.tap_element(current_centered_event_view)
    test.wait(5)

    # tune back to encrypted channel after re-authorization
    test.log('Tuning again to encrypted channel: %s   with offer: %s' %(encryptedChannelSek, offersToRemove))
    test.screens.zaplist.tune_to_channel_by_sek(encryptedChannelSek, verify_streaming_started=False)
    test.wait(5)

    # Wait to error notification  - not authorized
    test.screens.notification.verify_entitlement_error_notification()
    test.wait(3)
    test.startup_screen.navigate()

    # authorize encrypted channel to offer again using BOA
    test.log('Adding back offers: %s' %offersToRemove)
    test.say('setting offers back into channel %d' % encryptedChannellcn)

    for index in range(len(subscription)):
        test.he_utils.addAuthorizationSubscriptionUsingBoa(hh_id, "SUBSCRIPTION", subscription[index],"KD-SERVICES")

    # tune to another channel - go out of encrypted channel, then will return to it to verify re-authorization
    test.log('Tuning to another channel - go out of encrypted channel, then return to it to verify re-authorization')

    test.screens.zaplist.scroll_channels(2)
    elements = test.milestones.getElements()
    current_centered_event_view = test.screens.zaplist.get_centered_event_view(elements)
    test.appium.tap_element(current_centered_event_view)
    test.wait(5)

    # tune back to encrypted channel after re-authorization
    test.log('Tuning again to encrypted channel: %s   with offer: %s' % (encryptedChannelSek, offersToRemove))
    test.screens.zaplist.tune_to_channel_by_sek(encryptedChannelSek)

    test.wait(3)

    test.end()
