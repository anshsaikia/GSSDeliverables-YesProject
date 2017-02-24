__author__ = 'zhamilto'

class VeTestMirror(object):
    '''
    classdocs
    '''
    def __init__ (self,test):
        self.test = test

    def is_mirror(self):
        is_mirror = False
        device_details = self.test.milestones.getDeviceDetails()
        if 'mirror' in device_details:
            is_mirror = device_details['mirror']
        return is_mirror

    def direction(self, direction):
        is_mirror = self.is_mirror()
        if is_mirror:
            if direction == "left":
                direction = "right"
            elif direction == "right":
                direction = "left"
        return direction

    def is_sort_reverse(self, sortKey):
        reverse = False
        is_mirror = self.is_mirror()
        if is_mirror and sortKey == "x_pos":
            reverse = True
        return reverse

    def bar(self, left, division):
        is_mirror = self.is_mirror()
        if is_mirror:
            window_width, window_height = self.test.milestones.getWindowSize()
            left = window_width - ((window_width - left) / division)
        else:
            left /= division
        return left

    def offset(self, left, offset):
        is_mirror = self.is_mirror()
        if is_mirror:
            left -= offset
        else:
            left += offset
        return left

    def get_x(self, element):
        is_mirror = self.is_mirror()
        if is_mirror:
            return element['x_pos'] + element['width'] - 1
        else:
            return element['x_pos']

    def element_within_column(self, element, column_element):
        result = False
        element_left = ((element['x_pos'] + 5) / 10) * 10
        element_right = ((element['x_pos'] + element['width'] + 5) / 10) * 10
        column_element_left = ((column_element['x_pos'] + 5) / 10) * 10
        column_element_right = ((column_element['x_pos'] + column_element['width'] + 5) / 10) * 10
        is_mirror = self.is_mirror()
        if is_mirror:
            result = element_left < column_element_right and element_right > column_element_left and element_right >= column_element_right and column_element_left != element_right and column_element_right != element_left
        else:
            result = element_left < column_element_right and element_right > column_element_left and element_left <= column_element_left and column_element_left != element_right and column_element_right != element_left
        self.test.log("result: " + str(result) + " element: " + str(element_left) + " - " + str(element_right) + " column_element: " + str(column_element_left) + " - " + str(column_element_right))
        return result

    def element_after_element(self, first_element, second_element, no_overlap=True):
        result = False
        is_mirror = self.is_mirror()
        if is_mirror:
            if no_overlap:
                result = first_element['x_pos'] + first_element['width'] <= second_element['x_pos']
            else:
                result = first_element['x_pos'] <= second_element['x_pos']
        else:
            if no_overlap:
                result = first_element['x_pos'] >= second_element['x_pos']
            else:
                result = first_element['x_pos'] + first_element['width'] >= second_element['x_pos']
        self.test.log("element_after_element: " + str(result) + " = " + str(first_element['x_pos']) + ":" + first_element['title_text'] + " < " + str(second_element['x_pos']) + ":" + second_element['title_text'])
        return result

    def in_edge_of_screen(self, element):
        is_mirror = self.is_mirror()
        if is_mirror:
            window_width, window_height = self.test.milestones.getWindowSize()
            return element['x_pos'] + element['width'] == window_width
        else:
            return element['x_pos'] == 0

    def coords(self, left, top):
        is_mirror = self.is_mirror()
        if is_mirror:
            window_width, window_height = self.test.milestones.getWindowSize()
            left = window_width - left
        return left, top

    # only call when coordinates are independent from element positions
    def swipe_area(self, left, top, right, bottom, duration=0):
        left, top = self.coords(left, top)
        right, bottom = self.coords(right, bottom)
        self.test.appium.swipe_area(left, top, right, bottom, duration)

    # only call when coordinates are independent from element positions
    def tap(self, left, top):
        left, top = self.coords(left, top)
        self.test.appium.tap(left, top)
