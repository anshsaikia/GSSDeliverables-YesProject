import os
import commands
from enum import Enum

class AdbEventCodes(Enum):
    SYN_REPORT          = "0 0"       # end of report (0x0)
    ABS_MT_SLOT         = "3 47"      # MT slot being modified (0x2F)
    ABS_MT_TOUCH_MAJOR  = "3 48"      # width of finger tip in pixels (0x30)
    ABS_MT_TOUCH_MINOR  = "3 49"      # width of finger tip in pixels (0x31)
    ABS_MT_POSITION_X   = "3 53"      # x coordinate of the touch (0x35)
    ABS_MT_POSITION_Y   = "3 54"      # y coordinate of the touch (0x36)
    ABS_MT_TRACKING_ID  = "3 57"      # ID of the touch (important for multi-touch reports) (0x39)
    ABS_MT_PRESSURE     = "3 58"      # pressure of the touch (0x3A)
    BTN_TOUCH           = "1 330"     # Button touch (0-up,1-down) (0x14A)
    BTN_TOOL_FINGER     = "1 325"     # Button tool finger (0-up,1-down) (0x145)
    SLEEP               = "100"       # Sleep (custom)

class AdbWrapper(object):
    def __init__(self, test):
        self.test = test
        if self.test:
            self.device_id = self.test.device_id
        else:
            self.device_id = self.get_device_id()
        self.touch_device = self.get_touch_event_device()

    def shell(self, cmd):
        print cmd
        if os.name == 'nt' or os.name == 'posix':
            "windows usage"
            pipe = os.popen(cmd + ' 2>&1', 'r')
            text = pipe.read()
            pipe.close()
            return 0, text
        else:
            "UNIX usage"
            return commands.getstatusoutput(cmd)

    def remote_adb_shell(self, cmd):
        file = open("shell_commands.sh", "wb")
        file.write(cmd)
        file.close()
        self.shell(self.adb_prefix() + " push shell_commands.sh /sdcard/")
        self.shell(self.adb_prefix() + " shell sh /sdcard/shell_commands.sh")

    def adb_prefix(self):
        prefix = None
        if self.device_id:
            prefix = "adb -s " + self.device_id
        else:
            prefix = "adb"
        return prefix

    def adb_shell(self, cmd):
        full_cmd = self.adb_prefix() + " shell \"" + cmd + "\""
        return self.shell(full_cmd)

    def queue_event_touch(self, events, slot_id, x, y):
        touch_events = [[AdbEventCodes.ABS_MT_SLOT, slot_id],
                        [AdbEventCodes.ABS_MT_TRACKING_ID, slot_id+1000],
                        [AdbEventCodes.ABS_MT_POSITION_X, x],
                        [AdbEventCodes.ABS_MT_POSITION_Y, y],
                        [AdbEventCodes.ABS_MT_TOUCH_MAJOR, 5],
                        [AdbEventCodes.ABS_MT_TOUCH_MINOR, 5],
                        [AdbEventCodes.SYN_REPORT, 0]
                        ];
        events.extend(touch_events)

    def queue_event_move(self, events, slot_id, x, y):
        move_events = [[AdbEventCodes.ABS_MT_SLOT, slot_id],
                       [AdbEventCodes.ABS_MT_TRACKING_ID, slot_id+1000],
                       [AdbEventCodes.ABS_MT_POSITION_X, x],
                       [AdbEventCodes.ABS_MT_POSITION_Y, y],
                       [AdbEventCodes.SYN_REPORT, 0]
                       ];
        events.extend(move_events)

    def queue_event_release(self, events, slot_id):
        release_events = [[AdbEventCodes.ABS_MT_SLOT, slot_id+1000],
                          [AdbEventCodes.ABS_MT_TRACKING_ID, -1],
                          [AdbEventCodes.SYN_REPORT, 0]]
        events.extend(release_events)

    def queue_event_begin(self, events):
        begin_events = [[AdbEventCodes.BTN_TOUCH, 1],
                        [AdbEventCodes.SYN_REPORT, 0]]
        events.extend(begin_events)

    def queue_event_end(self, events):
        end_events = [[AdbEventCodes.BTN_TOUCH, 0],
                      [AdbEventCodes.SYN_REPORT, 0]]
        events.extend(end_events)

    def queue_event_sleep(self, events, msec):
        if msec:
            event = [AdbEventCodes.SLEEP, msec]
            events.append(event)

    def tap(self, x, y, msec=0):
        events = []
        self.queue_event_touch(events, 0, x, y)
        self.queue_event_sleep(events, msec)
        self.queue_event_release(events, 0)
        self.send_events(events)

    def swipe(self, start, end):
        events = []
        self.queue_event_begin(events)
        self.queue_event_touch(events, 0, start[0], start[1])
        self.queue_event_move(events, 0, end[0], end[1])
        self.queue_event_release(events, 0)
        self.queue_event_end(events)
        self.send_events(events)

    def multi_finger_swipe(self, *fingers):
        slot_index = 0
        events = []
        slot_index = 0
        for finger in fingers:
            self.queue_event_touch(events, slot_index, finger[0][0], finger[0][1])
            slot_index+=1
        self.queue_event_begin(events)
        slot_index = 0
        for finger in fingers:
            self.queue_event_move(events, slot_index, finger[1][0], finger[1][1])
            slot_index+=1
        slot_index = 0
        for finger in fingers:
            self.queue_event_release(events, slot_index)
            slot_index+=1
        self.queue_event_end(events)
        self.send_events(events)

    def clear(self):
        events = []
        self.queue_event_release(events, 0)
        self.queue_event_release(events, 1)
        self.send_events(events)

    def send_events(self, events):
        cmd = ""
        for event in events:
            eventCode = event[0]
            eventValue = str(event[1])
            if eventCode is AdbEventCodes.SLEEP:
                cmd += "sleep " + eventValue + "\r\n"
            else:
                cmd += "sendevent " + self.touch_device + " " + eventCode.value + " " + eventValue + "\r\n"
        self.remote_adb_shell(cmd)

    def get_touch_event_device(self):
        output = self.adb_shell("getevent -i")
        device = None
        if output:
            lines = output[1].split('\r\n')
            for line in lines:
                if 'device' in line:
                    device = line[line.rfind(": ")+2:]
                    device.strip()
                if 'name:' in line and 'touchscreen' in line:
                    break
        else:
            device = "/dev/input/event1"
        return device

    def get_device_id(self):
        device_id = None
        device_list = self.shell("adb devices | grep -v List | cut -f 1")[1].split()
        if device_list:
            device_id = device_list[0]
        return device_id
