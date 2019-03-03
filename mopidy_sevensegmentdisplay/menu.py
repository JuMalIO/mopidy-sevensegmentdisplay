from __future__ import division
from __future__ import unicode_literals


class Menu:

    def __init__(self, display, menu, modules):
        self.display = display
        self.menu = menu
        self.modules = modules
        self.module_index = 0
        self.module_visible = 0
        self.sub_menu = None
        self.sub_menu_group = None
        self.sub_menu_index = 0
        self.sub_menu_visible = 0
        self._set_sub_menu(self.menu)

    def run(self):
        if (self.is_sub_menu_visible()):
            self.sub_menu_visible -= 1
            if (not self.is_sub_menu_visible()):
                self.display.draw_scroll_up_animation(self.modules[self.module_index].get_draw_buffer())
                self._set_sub_menu(self.menu)
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

    def _close_sub_menu(self):
        if (self.sub_menu_visible > 1):
            self.sub_menu_visible = 1

    def _get_buffer_and_draw(self, draw):
        if ("get_buffer" in self.sub_menu[self.sub_menu_index]):
            draw(self.sub_menu[self.sub_menu_index]["get_buffer"]())

    def _on_draw(self):
        if ("on_draw" in self.sub_menu[self.sub_menu_index]):
            self.sub_menu[self.sub_menu_index]["on_draw"]()

    def _click_animation(self):
        if ("click_animation" in self.sub_menu[self.sub_menu_index]):
            self._get_buffer_and_draw(self.display.draw_blink_animation)

    def is_sub_menu_visible(self):
        if (self.sub_menu_visible <= 0):
            return False
        else:
            return True

    def click(self):
        self._set_sub_menu_visible()

        if ("get_sub_menu" in self.sub_menu[self.sub_menu_index]):
            self._set_sub_menu(self.sub_menu[self.sub_menu_index])
            self._get_buffer_and_draw(self.display.draw_scroll_down_animation)
            self._on_draw()
        elif ("click" in self.sub_menu[self.sub_menu_index]):
            self.sub_menu[self.sub_menu_index]["click"]()
            self._click_animation()
        else:
            self._close_sub_menu()

    def click_left(self, item=None):
        self._set_sub_menu_visible()

        if (self._is_sub_menu(item)):
            return

        if ("click_left" in self.sub_menu[self.sub_menu_index]):
            self.sub_menu[self.sub_menu_index]["click_left"]()
            self._get_buffer_and_draw(self.display.draw)
        else:
            self.sub_menu_index = (self.sub_menu_index - 1) % len(self.sub_menu)
            self._get_buffer_and_draw(self.display.draw_scroll_right_animation)
            self._on_draw()

    def click_right(self, item=None):
        self._set_sub_menu_visible()

        if (self._is_sub_menu(item)):
            return

        if ("click_right" in self.sub_menu[self.sub_menu_index]):
            self.sub_menu[self.sub_menu_index]["click_right"]()
            self._get_buffer_and_draw(self.display.draw)
        else:
            self.sub_menu_index = (self.sub_menu_index + 1) % len(self.sub_menu)
            self._get_buffer_and_draw(self.display.draw_scroll_left_animation)
            self._on_draw()

    def draw_sub_menu_animation(self, anim_dict):
        self._set_sub_menu_visible(anim_dict["length"])
        self.display.draw_animation(anim_dict["buffer"], anim_dict["repeat"], anim_dict["sleep"])

    def draw_sub_menu(self, item):
        self._set_sub_menu_visible()

        if (self._is_sub_menu(item)):
            return

        self._get_buffer_and_draw(self.display.draw)

    def _is_sub_menu(self, item):
        if (item is not None and self.sub_menu_group != item["group"]):
            self._set_sub_menu(item)
            self._get_buffer_and_draw(self.display.draw_scroll_down_animation)
            return True
        return False

    def _set_sub_menu(self, item):
        self.sub_menu = item["get_sub_menu"]()
        self.sub_menu_group = item["group"] if "group" in item else None
        self.sub_menu_index = 0

    def _set_sub_menu_visible(self, seconds=5):
        self.display.set_power_on()
        self.sub_menu_visible = seconds
        self.module_index = 0
        self.module_visible = 0
