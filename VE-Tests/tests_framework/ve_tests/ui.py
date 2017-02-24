import difflib

__author__ = 'rweinste'

from operator import itemgetter
from tests_framework.ve_tests.tests_conf import DeviceType

class element_item:
    def __init__ (self):
        pass

class VeTestUI(object):
    '''
    classdocs
    '''
    def __init__ (self,test):
        self.test = test

    def swipe_element(self,direction):
        direction = self.test.mirror.direction(direction)
        if(direction =="up"):
            self.test.appium.swipe_area(236, 600 ,236, 0)
        elif (direction =="down"):
            self.test.appium.swipe_area(236, 100, 236, 760)
        elif (direction == "left"):
            self.test.appium.swipe_area(236, 213, 100, 213)
        elif (direction == "right"):
            self.test.appium.swipe_area(100, 213, 236, 213)

    def swipe_element_with_length(self,direction,length):
        direction = self.test.mirror.direction(direction)
        divide_by=1
        if (length=="short"):
            divide_by=3

        if(direction =="up"):
            self.test.appium.swipe_area(236, 600 ,236, 600-600/divide_by)
        elif(direction =="down"):
            self.test.appium.swipe_area(236, 100, 236, 100+660/divide_by)
        elif (direction == "right"):
            self.test.appium.swipe_area(100, 213 ,100+136/divide_by, 213)
        elif (direction == "left"):
            self.test.appium.swipe_area(236 - 136/ divide_by , 213, 236, 213)

    def verify_screen(self, name):
        elements = self.test.milestones.getElements()
        return self.test.milestones.verifyElement([("screen", name, "==")],elements)

    def verify_full_screen(self):
        elements = self.test.milestones.getElements()
        return not self.test.milestones.verify_element_by_key(elements,"screen")

    def get_column_events(self, elementName, column_index, elements=None, filterKey=None, filterValue=None):
        events = self.get_sorted_events(elementName, 'x_pos', elements, filterKey, filterValue)
        self.test.log_assert(events, "Cannot find events")
        first_event = events[column_index]
        columns = []
        for event in events:
            if event['y_pos'] == first_event['y_pos']:
                columns.append(event)
        self.test.log_assert(column_index < len(columns), "Column index (" + str(column_index) + ") out of range (" + str(len(columns)) + ")")
        self.test.log("columns =" + str(columns))
        column_events = []
        for event in events:
            if event['x_pos'] == columns[column_index]['x_pos']:
                column_events.append(event)
        self.test.log("column_events[" + str(column_index) + "] =" + str(column_events))
        return column_events

    def get_sorted_elements(self, elementName, sortKey, elements, filterKey=None, filterValue=None):
        sorted_elements = []
        for element in elements:
            if "name" not in element:
                continue
            if element["name"] != elementName:
                continue
            if filterKey and filterKey not in element:
                continue
            if filterKey and filterValue and element[filterKey] != filterValue:
                continue
            sorted_elements.append(element)
        sorted_elements = sorted(sorted_elements, key=itemgetter(sortKey), reverse=self.test.mirror.is_sort_reverse(sortKey))
        return sorted_elements

    def get_sorted_events(self, elementName, sortKey, elements, filterKey=None, filterValue=None):
        if not elements:
            elements = self.test.milestones.getElements()
        sorted_elements = []
        for element in elements:
            if "name" not in element:
                continue
            if element["name"] != elementName:
                continue
            if filterKey and filterKey not in element:
                continue
            if filterKey and filterValue and element[filterKey] != filterValue:
                continue
            if 'channel_id' in element and (element["channel_id"] is None or element["channel_id"] == ''):
                continue
            if 'title_text' in element and element["title_text"] is None:
                continue
            sorted_elements.append(element)
        sorted_elements = sorted(sorted_elements, key=itemgetter(sortKey), reverse=self.test.mirror.is_sort_reverse(sortKey))
        return sorted_elements

    def get_center_elements(self, elementName, elements, filter=None):
        center_element = self.get_center_element(elementName, elements, filter)
        center_elements = []
        window_width, window_height = self.test.milestones.getWindowSize()
        screen_center_y = window_height / 2
        elements = self.get_sorted_elements(elementName, 'x_pos', elements)
        for element in elements:
            if element["y_pos"] != center_element["y_pos"]:
                continue
            center_elements.append(element)
        return elements

    def get_vertical_element(self, elementName, elements, index, filter=None):
        self.test.log_assert(elements or len(elements), "No elements passed")
        current = -1
        device_details = self.test.milestones.getDeviceDetails()
        screen_center_y = device_details["screen-height"] / 2
        if self.test.verbose:
            self.test.log("screen vertical center: " + str(screen_center_y))
        elements = self.get_sorted_elements(elementName, 'y_pos', elements, filter)
        self.test.log_assert(elements, "Cannot find any elements on-screen, elementName: %s, filter: %s" %(elementName, filter))
        ''' find the center element '''
        for element in elements:
            current+=1
            height = element["height"]
            if ('parent-height' in element) and (element['parent-height'] > 0):
                height = element['parent-height']
            if element["y_pos"] + (height / 2) > screen_center_y:
                break
        '''calculate absolute index by relative index'''
        elementIndex = index + current
        self.test.log_assert(elementIndex < len(elements), "Not enough items below, index: " +
                             str(index) + " current: " + str(current) + " count: " + str(len(elements)))
        self.test.log_assert(elementIndex >= 0, "Not enough items above, index: " +
                             str(index) + " current: " + str(current))
        return elements[elementIndex]

    def get_center_element(self, elementName, elements, filter=None):
        return self.get_vertical_element(elementName, elements, 0, filter)

    def fullscreen_element(self):
        window_width, window_height = self.test.milestones.getWindowSize()
        element = {
            "x_pos": 0,
            "y_pos": 0,
            "width": window_width,
            "height": window_height
        }
        return element

    def one_finger_swipe(self, direction):
        direction = self.test.mirror.direction(direction)
        division = 4
        if self.test.device_type == DeviceType.SMARTPHONE and self.test.platform == "iOS":
            division = 2
        element = self.fullscreen_element()
        self.test.appium.swipe_element(element, element["height"]/division, direction)

    def two_finger_swipe(self, direction):
        direction = self.test.mirror.direction(direction)
        division = 4
        if self.test.device_type == DeviceType.SMARTPHONE and self.test.platform == "iOS":
            division = 2
        element = self.fullscreen_element()
        self.test.appium.two_fingers_swipe_element(element,element["height"]/division, direction)

    def top_tap(self):
        window_width, window_height = self.test.milestones.getWindowSize()

        element = {
            "x_pos": window_width / 2,
            "y_pos": window_height / 4,
            "width": 0,
            "height": 0
        }

        self.test.appium.tap_element(element)

    def center_tap(self, elements=None):
        window_width, window_height = self.test.milestones.getWindowSize(elements)

        element = {
            "name" : "center tap",
            "x_pos": window_width / 2,
            "y_pos": window_height / 2,
            "width": 0,
            "height": 0
        }

        self.test.appium.tap_element(element)

    def side_bar_swipe(self, direction):
        direction = self.test.mirror.direction(direction)
        if direction == "left":
            window_width, window_height = self.test.milestones.getWindowSize()
            self.test.appium.swipe_area(20, window_height / 2, window_width - 20, window_height / 2)
        elif direction == "right":
            window_width, window_height = self.test.milestones.getWindowSize()
            self.test.appium.swipe_area(window_width - 20, window_height / 2, 20, window_height / 2)

    def get_element_by_value(self, elements, key, value):
        for element in elements:
            if key in element and element[key] == value:
                return element
        return None

    def get_element_containing_value(self, elements, key, value):
        for element in elements:
            if key in element and element[key] and value in element[key]:
                return element
        return None

    def get_label_containing(self, text, elements=None):
        if elements == None:
            elements = self.test.milestones.getElements()
        return self.get_element_containing_value(elements, "title_text", text)

    def tap_element(self, name, elements=None):
        if elements == None:
            elements = self.test.milestones.getElements()
        element = self.get_element_by_value(elements, "id", name)
        self.test.log_assert(element, "Cannot find element: " + name)
        self.test.appium.tap_element(element)

    def tap_center_element(self, name, elements=None):
        if elements == None:
            elements = self.test.milestones.getElements()
        element = self.get_element_by_value(elements, "id", name)
        self.test.log_assert(element, "Cannot find element: " + name)
        self.test.appium.tap_center_element(element)

    def get_label(self, label, elements=None):
        if elements is None:
            elements = self.test.milestones.getElements()
        element = self.get_element_by_value(elements, "title_text", label)
        self.test.log_assert(element, "Cannot find label: " + label)
        return element

    def tap_label(self, label, elements=None):
        element = self.get_label(label, elements)
        self.test.appium.tap_element(element)

    def element_exists(self, name, elements=None):
        exists = False
        if elements is None:
            elements = self.test.milestones.getElements()
        element = self.get_element_by_value(elements, "id", name)
        if element:
            exists = True
        return exists

    def element_verify(self, name, elements=None,assert_msg=" element doesnt exist"):
        if elements is None:
            elements = self.test.milestones.getElements()
        element = self.get_element_by_value(elements, "id", name)
        self.test.log_assert(element,name + assert_msg)
        return element

    def label_exists(self, label, elements=None):
        exists = False
        if elements == None:
            elements = self.test.milestones.getElements()
        element = self.get_element_by_value(elements, "title_text", label)
        if element:
            exists = True
        return exists

    def label_exists_with_wait(self, label, elements=None, timeout=5):
        if elements == None:
            elements = self.test.milestones.getElements()
        for i in range(0, timeout):
            element = self.get_element_by_value(elements, "title_text", label)
            if element:
                return True
            self.test.wait(1)
            elements = self.test.milestones.getElements()
        return False

    def wait_for_label(self, name, timeout=30):
        label_exists = False
        for repeat in range(0, timeout):
            label_exists = self.label_exists(name)
            if label_exists:
                break
            self.test.wait(1)
        self.test.log_assert(label_exists, "Element " + name + " not being displayed on the screen")

    def wait_for_label_removed(self, name, elements=None, timeout=30):
        label_exists = False
        for repeat in range(0, timeout):
            label_exists = self.label_exists(name)
            if not label_exists:
                break
            self.test.wait(1)
        self.test.log_assert(not label_exists, "Element " + name + " not being removed from the screen")

    def wait_for_element(self, name, elements=None, timeout=30):
        element_exists = False
        for repeat in range(0, timeout):
            element_exists = self.element_exists(name)
            if element_exists:
                break
            self.test.wait(1)
        self.test.log_assert(element_exists, "Element " + name + " not being displayed on the screen")

    def wait_for_element_removed(self, name, elements=None, timeout=30):
        element_exists = False
        for repeat in range(0, timeout):
            element_exists = self.element_exists(name)
            if not element_exists:
                break
            self.test.wait(1)
        self.test.log_assert(not element_exists, "Element " + name + " not being removed from the screen")

    def localized_label_exists(self, dict_key, uppercase=True, elements=None):
        dic_value = self.test.milestones.get_dic_value_by_key(dict_key)
        if uppercase:
            dic_value = dic_value.upper()
        return self.label_exists(dic_value, elements)

    def get_localized_label(self, dict_key, uppercase=True, elements=None):
        dic_value = self.test.milestones.get_dic_value_by_key(dict_key)
        if uppercase:
            dic_value = dic_value.upper()
        return self.get_label(dic_value, elements)

    def tap_localized_label(self, dict_key, uppercase=True, elements=None):
        dic_value = self.test.milestones.get_dic_value_by_key(dict_key)
        if uppercase:
            dic_value = dic_value.upper()
        self.tap_label(dic_value, elements)

    def localized_id_exists(self, dict_key, uppercase=True, elements=None):
        dic_value = self.test.milestones.get_dic_value_by_key(dict_key)
        if uppercase:
            dic_value = dic_value.upper()
        return self.element_exists(dic_value, elements)

    def tap_localized_id(self, dict_key, uppercase=True, elements=None):
        dic_value = self.test.milestones.get_dic_value_by_key(dict_key)
        if uppercase:
            dic_value = dic_value.upper()
        self.tap_element(dic_value, elements)

    def verify_text(self, id, text, elements=None):
        if elements == None:
            elements = self.test.milestones.getElements()
        element = self.get_element_by_value(elements, "id", id)
        self.test.log_assert(element, "Cannot find element: " + id)
        self.test.log_assert(element['title_text'] == text, "Element " + id + " has text '" + element['title_text'] + "' instead of " + text + "'")

    def verify_button(self, button_type, is_present, retry=0):
        i=0
        while True:
            milestones = self.test.milestones
            elements = milestones.getElements()

            key_value = milestones.get_dic_value_by_key(button_type.value)
            button = milestones.getElement([("title_text", key_value.upper(), "==")], elements)
            i += 1
            if is_present:
                if button:
                    return button
                if i >= retry:
                    self.test.log_assert(button , "%s = %s button is not present" %(button_type, key_value.upper()))
                    return button
            else:
                if not button:
                    return button
                if i >= retry:
                    self.test.log_assert(not button , "%s = %s button is present" %(button_type, key_value.upper()))
                    return button
            self.test.wait(1)

    def is_button_exist(self,title,key, operator='=='):
        milestones = self.test.milestones
        elements = milestones.getElements()
        return milestones.getElement([(key, title, operator)], elements)

    def verify_button_by_title(self, title, is_present, key="title_text", assertFlag=True, operator='=='):
        button = self.is_button_exist(title,key,operator)
        if assertFlag:
            if is_present:
                self.test.log_assert(button, title + " button is not present")
                return button
            else:
                self.test.log_assert(not button, title + " button is present")
        else:
            if button:
                return True
            else:
                return False

    def verify_and_press_button_by_title(self, title, key="title_text", wait = True, operator='=='):
        record_button = self.verify_button_by_title(title, is_present=True, key=key, operator=operator)
        self.test.appium.tap_element(record_button)
        if wait:
            self.test.milestones.getElements()  # wait

    def verify_button_by_id(self, title, is_present, key="id"):
        button = self.is_button_exist(title,key)
        if is_present:
            self.test.log_assert(button, title + " button is not present")
            return button
        else:
            self.test.log_assert(not button, title + " button is present")

    def verify_and_press_button_by_id(self, title, key="id", wait = True):
        record_button = self.verify_button_by_id(title, is_present=True, key=key)
        self.test.appium.tap_element(record_button)
        if wait:
            self.test.milestones.getElements()  # wait

    def verify_and_press_button_by_dic_title(self, key_title, key="title_text", wait = True):
        title = self.test.milestones.get_dic_value_by_key(key_title)
        self.verify_and_press_button_by_title(title)

    def remove_special_chars(self, string):
        string = string.replace(u'\u202a', '')
        string = string.replace(u'\u202c', '')
        return string

    def detailed_compare(self, a, b, error):
        #First remove unicode characters
        a = self.remove_special_chars(a)
        b = self.remove_special_chars(b)
        #Compare results
        if a == b:
            return
        #Detailed explanation of changes
        response = ""
        for i,s in enumerate(difflib.ndiff(a, b)):
            if s[0]==' ': continue
            elif s[0]=='-':
                response += '\nDelete "{}" ({}) from position {}'.format(s[-1],s[-1].__repr__(),i)
            elif s[0]=='+':
                response += '\nAdd "{}" ({}) to position {}'.format(s[-1],s[-1].__repr__(),i)
        self.test.log_assert(False, error + " between '" + a + "' (" + str(len(a)) + ") and '" + b + "' (" + str(len(b)) + ") details: " + response)

    def get_property_list(self, list, name):
        props = []
        for item in list:
            if name in item:
                props.append(item[name])
        return props
