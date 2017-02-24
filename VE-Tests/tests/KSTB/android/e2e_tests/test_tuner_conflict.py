__author__ = 'sbouhman'

import logging
from tests_framework.ui_building_blocks.KSTB.dvrbooking import DVRBooking

def test_01_tuner_conflict():

    num_of_tuner = 4

    test = DVRBooking("test_tuner_conflict")
    test.ve_test.begin(screen=test.ve_test.screens.fullscreen)
    test.ve_test.screens.playback.dca(1,time_out=5)
    for i in range(num_of_tuner):
        if i > 0:
            logging.info("Goto next channel")
            test.ve_test.screens.zaplist.navigate("down")
            test.ve_test.screens.zaplist.to_nextchannel("down")

        logging.info("Goto to actionMenu")
        test.ve_test.screens.main_hub.navigate()

        logging.info("Start record and verify the program had been recorded")
        result = test.ve_test.start_record()
        test.ve_test.log_assert(result is True, str(result))
        test.ve_test.wait(3)

    logging.info("Goto next channel")
    test.ve_test.screens.zaplist.navigate("down")
    test.ve_test.screens.zaplist.to_nextchannel("down")

    logging.info("Goto to actionMenu")
    test.ve_test.screens.main_hub.navigate()

    logging.info("Start record")
    test.start_record(test_flag=False)

    logging.info('check that the Tuner_Conflict OSD appears')
    result = test.ve_test.is_notification_error(msg_text="Unfortunately, your recording cannot be booked at this moment because it conflicts with an existing scheduled recording.")
    test.ve_test.log_assert(result is True, str(result))
