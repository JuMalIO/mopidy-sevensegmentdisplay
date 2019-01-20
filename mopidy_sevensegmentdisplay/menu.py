from __future__ import division
from __future__ import unicode_literals


class Menu:

    def __init__(self, display, menu, modules):
        self.display = display
        self.menu = menu
        self.modules = modules
        self.module_index = 0
        self.module_visible = 0
        self.sub_menu = menu
        self.sub_menu_index = 0
        self.sub_menu_visible = 0

    def run(self):
        if (self._is_sub_menu_visible()):
            return

        self._run_modules()

        if (self.display.is_power_on()):
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
        if ("get_sub_menu" in self.sub_menu[self.sub_menu_index]):
            self.sub_menu = self.sub_menu[self.sub_menu_index]["get_sub_menu"]()
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
        self.display.set_power_on()
        self.sub_menu_visible = seconds
        self.module_index = 0
        self.module_visible = 0
