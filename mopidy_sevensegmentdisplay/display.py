from max7219 import SevenSegmentDisplay, Symbols
from animation import Animation, BlinkAnimation, ScrollDownAnimation, ScrollUpAnimation, ScrollLeftAnimation, ScrollRightAnimation
import threading
import logging
from datetime import datetime


class Display:

    def __init__(self):
        self.brightness = None
        self.is_shutdown = False
        self.animation_thread = None
        self.display = SevenSegmentDisplay()
        self.lock = threading.Lock()

    def set_brightness(self, brightness):
        if (self.brightness != brightness):
            self.brightness = brightness
            self.display.set_brightness(brightness)

    def shutdown(self, is_shutdown=True):
        if (self.is_shutdown != is_shutdown):
            if (is_shutdown):
                self._kill_animation()
            self.is_shutdown = is_shutdown
            self.display.shutdown(is_shutdown)

    def draw(self, buffer):
        self._kill_animation()
        self.display.set_buffer(buffer)
        self.display.flush()

    def draw_animation(self, buffer, repeat=1, sleep=0.05):
        self._draw_animation(Animation(self.display, buffer, repeat, sleep))

    def draw_blink_animation(self, buffer, repeat=6, sleep=0.1):
        self._draw_animation(BlinkAnimation(self.display, buffer, repeat, sleep))

    def draw_scroll_left_animation(self, buffer, sleep=0.05):
        new_buffer = list(buffer)
        new_buffer.insert(0, Symbols.NONE)
        self._draw_animation(ScrollLeftAnimation(self.display, new_buffer, sleep))

    def draw_scroll_right_animation(self, buffer, sleep=0.05):
        new_buffer = list(buffer)
        new_buffer.append(Symbols.NONE)
        self._draw_animation(ScrollRightAnimation(self.display, new_buffer, sleep))

    def draw_scroll_up_animation(self, buffer, sleep=0.05):
        self._draw_animation(ScrollUpAnimation(self.display, buffer, sleep))

    def draw_scroll_down_animation(self, buffer, sleep=0.05):
        self._draw_animation(ScrollDownAnimation(self.display, buffer, sleep))

    def _draw_animation(self, animation):
        self.lock.acquire()
        try:
            if (self.animation_thread is not None):
                self.animation_thread.stop()
                self.animation_thread = None
            if (animation is not None):
                self.animation_thread = animation
                self.animation_thread.start()
        except Exception as inst:
            logging.error(inst)
        finally:
            self.lock.release()

    def _kill_animation(self):
        self._draw_animation(None)


class DisplayWithPowerSaving(Display):

    def __init__(self, display_min_brightness, display_max_brightness, display_off_time_from, display_off_time_to):
        super(Display, self).__init__()
        self.display_min_brightness = display_min_brightness
        self.display_max_brightness = display_max_brightness
        self.display_off_time_from = display_off_time_from
        self.display_off_time_to = display_off_time_to
        self.display_enabled = datetime.now()

    def is_power_saving_off(self):
        now = datetime.now()
        if (self._is_power_saving_off(now)):
            self._set_display_on()
            self._set_brightness(now)
            return True
        else:
            self._set_display_off()
            return False

    def set_power_saving_off(self):
        now = datetime.now()
        if (not self._is_power_saving_off(now)):
            self._set_display_on()
            self.display_enabled = now

    def _is_power_saving_off(self, now):
        return (self.display_enabled.day == now.day and
                self.display_enabled.month == now.month and
                self.display_enabled.year == now.year) or (not self._is_work_time(now))

    def _is_work_time(self, now):
        return now.weekday() < 5 and now.hour > self.display_off_time_from and now.hour < self.display_off_time_to

    # hour       - 9 10 11 12 13 14 15 16 17 18 19 20 -
    # brightness 2 3  4  5  6  7  8  8  7  6  5  4  3 2
    # when display_min_brightness=2 and display_max_brightness=8
    def _set_brightness(self, now):
        hour = now.hour
        brightness = self.display_min_brightness
        if (hour >= 9 and hour <= 20):
            if (hour < 15):
                brightness = int(round(
                    self.display_min_brightness + (self.display_max_brightness - self.display_min_brightness) / 6 * (hour - 9 + 1)))
            else:
                brightness = int(round(
                    self.display_min_brightness + (self.display_max_brightness - self.display_min_brightness) / 6 * (20 - hour + 1)))
        super(DisplayWithPowerSaving, self).set_brightness(brightness)

    def _set_display_on(self):
        super(DisplayWithPowerSaving, self).shutdown(False)

    def _set_display_off(self):
        super(DisplayWithPowerSaving, self).shutdown()
