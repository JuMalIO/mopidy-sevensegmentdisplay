from max7219 import SevenSegmentDisplay, Symbols
from animation import Animation, BlinkAnimation, ScrollDownAnimation, ScrollUpAnimation, ScrollLeftAnimation, ScrollRightAnimation
import threading
import logging


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
