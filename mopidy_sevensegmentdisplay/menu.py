from __future__ import division
from __future__ import unicode_literals

from datetime import datetime


class Menu:

    def __init__(self, display, menu, modules, display_min_brightness, display_max_brightness, display_off_time_from, display_off_time_to):
        self.display = display
        self.menu = menu
        self.modules = modules
        self.module_index = 0
        self.module_visible = 0
        self.sub_menu = menu
        self.sub_menu_index = 0
        self.sub_menu_visible = 0
        self.display_power_saver = DisplayPowerSaver(display, display_min_brightness, display_max_brightness, display_off_time_from, display_off_time_to)

    def run(self):
        if (self._is_sub_menu_visible()):
            return

        self._run_modules()

        if (self.display_power_saver.is_display_enabled()):
            self._draw_module()

    def _run_modules(self):
        for module in self.modules:
            module.run()

    def _draw_module(self):
        if (self.modules[self.module_index].is_visible(self.module_visible)):
            self.module_visible = self.module_visible + 1
            self.display.draw(self.modules[self.module_index].get_draw_buffer())
        else:
            self._next_module_index()
            self.display.draw_scroll_left_animation(self.modules[self.module_index].get_draw_buffer())

    def _next_module_index(self):
        self.module_visible = 0
        self.module_index = (self.module_index + 1) % len(self.modules)
        for i in range(self.module_index, len(self.modules)):
            if (self.modules[i].is_visible(self.module_visible)):
                self.module_index = i
                return
        for i in range(self.module_index):
            if (self.modules[i].is_visible(self.module_visible)):
                self.module_index = i
                return

    def _is_sub_menu_visible(self):
        if (self.sub_menu_visible <= 0):
            return False
        else:
            self.sub_menu_visible -= 1
            if (self.sub_menu_visible <= 0):
                self.display.draw_scroll_up_animation(self.modules[self.module_index].get_draw_buffer())
                self.sub_menu = self.menu
                self.sub_menu_index = 0
            return True

    def _close_sub_menu(self):
        if (self.sub_menu_visible > 1):
            self.sub_menu_visible = 1

    def click(self):
        self._set_sub_menu_visible()
        if ("sub_menu" in self.sub_menu[self.sub_menu_index]):
            self.sub_menu = self.sub_menu[self.sub_menu_index]["sub_menu"]
            self.sub_menu_index = 0
            self.display.draw_scroll_down_animation(self.sub_menu[self.sub_menu_index]["get_buffer"]())
        elif ("click" in self.sub_menu[self.sub_menu_index]):
            self.sub_menu[self.sub_menu_index]["click"]()
            if ("click_animation" in self.sub_menu[self.sub_menu_index]):
                self.display.draw_blink_animation(self.sub_menu[self.sub_menu_index]["get_buffer"]())
        else:
            self._close_sub_menu()

    def click_left(self):
        self._set_sub_menu_visible()
        if ("click_left" in self.sub_menu[self.sub_menu_index]):
            self.sub_menu[self.sub_menu_index]["click_left"]()
            if ("get_buffer" in self.sub_menu[self.sub_menu_index]):
                self.display.draw(self.sub_menu[self.sub_menu_index]["get_buffer"]())
        else:
            self.sub_menu_index = (self.sub_menu_index - 1) % len(self.sub_menu)
            if ("get_buffer" in self.sub_menu[self.sub_menu_index]):
                self.display.draw_scroll_right_animation(self.sub_menu[self.sub_menu_index]["get_buffer"]())

    def click_right(self):
        self._set_sub_menu_visible()
        if ("click_right" in self.sub_menu[self.sub_menu_index]):
            self.sub_menu[self.sub_menu_index]["click_right"]()
            if ("get_buffer" in self.sub_menu[self.sub_menu_index]):
                self.display.draw(self.sub_menu[self.sub_menu_index]["get_buffer"]())
        else:
            self.sub_menu_index = (self.sub_menu_index + 1) % len(self.sub_menu)
            if ("get_buffer" in self.sub_menu[self.sub_menu_index]):
                self.display.draw_scroll_left_animation(self.sub_menu[self.sub_menu_index]["get_buffer"]())

    def draw_sub_menu_animation(self, anim_dict):
        self._set_sub_menu_visible(anim_dict["length"])
        self.display.draw_animation(anim_dict["buffer"], anim_dict["repeat"], anim_dict["sleep"])

    def draw_sub_menu(self, buffer):
        self._set_sub_menu_visible()
        self.display.draw(buffer)

    def _set_sub_menu_visible(self, seconds=5):
        self.display_power_saver.set_display_enabled()
        self.sub_menu_visible = seconds
        self.module_index = 0
        self.module_visible = 0


class DisplayPowerSaver:

    def __init__(self, display, display_min_brightness=2, display_max_brightness=8, display_off_time_from=8, display_off_time_to=17):
        self.display = display
        self.display_min_brightness = display_min_brightness
        self.display_max_brightness = display_max_brightness
        self.display_off_time_from = display_off_time_from
        self.display_off_time_to = display_off_time_to
        self.now = datetime.now()
        self.now_weekday = self.now.weekday()
        self.enable = self.now

    def is_display_enabled(self):
        self.now = datetime.now()
        self.now_weekday = self.now.weekday()

        if (self._is_display_enabled()):
            self._set_display_on()
            self._set_brightness()
            return True
        else:
            self._set_display_off()
            return False

    def set_display_enabled(self):
        if (self._is_work_time()):
            self._set_display_on()
            self.enable = self.now

    def _is_display_enabled(self):
        day = self.now.day
        month = self.now.month
        year = self.now.year
        return (self.enable.day == day and self.enable.month == month and self.enable.year == year) or not (self._is_work_time())

    def _is_work_time(self):
        hour = self.now.hour
        return self.now_weekday < 5 and hour > self.display_off_time_from and hour < self.display_off_time_to

    # hour       - 9 10 11 12 13 14 15 16 17 18 19 20 -
    # brightness 2 3  4  5  6  7  8  8  7  6  5  4  3 2
    def _set_brightness(self):
        hour = self.now.hour
        brightness = self.display_min_brightness
        if (hour >= 9 and hour <= 20):
            if (hour < 15):
                brightness = int(round(self.display_min_brightness + (self.display_max_brightness - self.display_min_brightness) / 6 * (hour - 9 + 1)))
            else:
                brightness = int(round(self.display_min_brightness + (self.display_max_brightness - self.display_min_brightness) / 6 * (20 - hour + 1)))
        self.display.set_brightness(brightness)

    def _set_display_on(self):
        self.display.shutdown(False)

    def _set_display_off(self):
        self.display.shutdown()
