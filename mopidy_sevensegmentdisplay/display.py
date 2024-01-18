import threading
import logging
from datetime import datetime
from .max7219 import SevenSegmentDisplay, Symbols
from .animation import Animation, BlinkAnimation, ScrollDownAnimation, ScrollUpAnimation, ScrollLeftAnimation, ScrollRightAnimation


class Display(object):

    def __init__(self, display_enabled):
        self._brightness = None
        self._is_shutdown = not display_enabled
        self._animation_thread = None
        self._display = SevenSegmentDisplay() if display_enabled else None
        self._lock = threading.Lock()

    def set_brightness(self, brightness):
        if (self._display is None):
            return

        if (self._brightness != brightness):
            self._brightness = brightness
            self._display.set_brightness(brightness)

    def shutdown(self, is_shutdown=True):
        if (self._display is None):
            return

        if (self._is_shutdown != is_shutdown):
            if (is_shutdown):
                self._kill_animation()
            self._is_shutdown = is_shutdown
            self._display.shutdown(is_shutdown)

    def stop(self):
        if (self._display is None):
            return
        
        self.shutdown()
        self._display.stop()
        self._display = None


    def draw(self, buffer):
        if (self._display is None):
            return
        
        self._kill_animation()
        self._display.set_buffer(buffer)
        self._display.flush()

    def draw_animation(self, buffer, repeat=1, sleep=0.05):
        if (self._display is None):
            return

        self._draw_animation(Animation(self._display, buffer, repeat, sleep))

    def draw_blink_animation(self, buffer, repeat=6, sleep=0.1):
        if (self._display is None):
            return

        self._draw_animation(BlinkAnimation(self._display, buffer, repeat, sleep))

    def draw_scroll_left_animation(self, buffer, sleep=0.05):
        if (self._display is None):
            return

        new_buffer = list(buffer)
        new_buffer.insert(0, Symbols.NONE)
        self._draw_animation(ScrollLeftAnimation(self._display, new_buffer, sleep))

    def draw_scroll_right_animation(self, buffer, sleep=0.05):
        if (self._display is None):
            return

        new_buffer = list(buffer)
        new_buffer.append(Symbols.NONE)
        self._draw_animation(ScrollRightAnimation(self._display, new_buffer, sleep))

    def draw_scroll_up_animation(self, buffer, sleep=0.05):
        if (self._display is None):
            return

        self._draw_animation(ScrollUpAnimation(self._display, buffer, sleep))

    def draw_scroll_down_animation(self, buffer, sleep=0.05):
        if (self._display is None):
            return

        self._draw_animation(ScrollDownAnimation(self._display, buffer, sleep))

    def _draw_animation(self, animation):
        self._lock.acquire()
        try:
            if (self._animation_thread is not None):
                self._animation_thread.stop()
                self._animation_thread = None
            if (animation is not None):
                self._animation_thread = animation
                self._animation_thread.start()
        except Exception as inst:
            logging.error(inst)
        finally:
            self._lock.release()

    def _kill_animation(self):
        self._draw_animation(None)


class DisplayWithPowerSaving(Display):

    def __init__(self, display_enabled, display_min_brightness, display_max_brightness, display_off_time_from, display_off_time_to):
        super(DisplayWithPowerSaving, self).__init__(display_enabled)
        self._display_min_brightness = display_min_brightness
        self._display_max_brightness = display_max_brightness
        self._display_off_time_from = display_off_time_from
        self._display_off_time_to = display_off_time_to
        self._display_power_on = datetime.now()

    def is_power_on(self):
        now = datetime.now()
        if (self._is_power_on(now)):
            self._set_power_on()
            self._set_brightness(now)
            return True
        else:
            self._set_power_off()
            return False

    def set_power_on(self):
        now = datetime.now()
        if (not self._is_power_on(now)):
            self._set_power_on()
            self._display_power_on = now

    def _is_power_on(self, now):
        return (self._display_power_on.day == now.day and
                self._display_power_on.month == now.month and
                self._display_power_on.year == now.year) or (not self._is_work_time(now))

    def _is_work_time(self, now):
        return now.weekday() < 5 and now.hour > self._display_off_time_from and now.hour < self._display_off_time_to

    # hour       - 9 10 11 12 13 14 15 16 17 18 19 20 -
    # brightness 2 3  4  5  6  7  8  8  7  6  5  4  3 2
    # when display_min_brightness=2 and display_max_brightness=8
    def _set_brightness(self, now):
        hour = now.hour
        brightness = self._display_min_brightness
        if (hour >= 9 and hour <= 20):
            if (hour < 15):
                brightness = int(round(
                    self._display_min_brightness + (self._display_max_brightness - self._display_min_brightness) / 6 * (hour - 9 + 1)))
            else:
                brightness = int(round(
                    self._display_min_brightness + (self._display_max_brightness - self._display_min_brightness) / 6 * (20 - hour + 1)))
        super(DisplayWithPowerSaving, self).set_brightness(brightness)

    def _set_power_on(self):
        super(DisplayWithPowerSaving, self).shutdown(False)

    def _set_power_off(self):
        super(DisplayWithPowerSaving, self).shutdown()
