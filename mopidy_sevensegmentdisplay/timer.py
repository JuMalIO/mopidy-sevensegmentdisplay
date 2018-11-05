from __future__ import division
from __future__ import unicode_literals

from datetime import datetime, timedelta
from max7219 import Symbols


class Timer(object):
    VISIBLE_FOR_SECONDS = 2

    def __init__(self, callback, step, remove_min=True):
        self.callback = callback
        self.step = step
        self.half_step = int(step / 2)
        self.remove_min = remove_min
        self.now = self._datetime_now()
        self.timer = None

    def run(self):
        self.now = self._datetime_now()
        if (self.is_set()):
            if (self._is_time()):
                self.callback()
                self.reset()

    def is_set(self):
        return self.timer is not None

    def _datetime_now(self):
        return datetime.now().replace(second=0, microsecond=0)

    def _is_time(self):
        return self.now >= self.timer

    def reset(self):
        self.timer = None

    def increase(self):
        if (not self.is_set()):
            time_left = (self.step - self.now.minute % self.step) if self.remove_min else 0
            min = time_left + (self.step if time_left < self.half_step else 0)
            self.timer = self.now + timedelta(minutes = min)
        else:
            new_time = self.timer + timedelta(minutes = self.step)
            diff = new_time - self.now
            if (diff.days < 1):
                self.timer = new_time

    def decrease(self):
        if (self.is_set()):
            timer_minus_step = self.timer - timedelta(minutes = self.step)
            now_plus_half_step = self.now + timedelta(minutes = self.half_step)
            if (now_plus_half_step < timer_minus_step):
                self.timer = timer_minus_step
            else:
                self.timer = None

    def is_visible(self, seconds):
        return seconds < self.VISIBLE_FOR_SECONDS and self.is_set()


class TimerOff(Timer):
    TIMER_STEP = 30

    def __init__(self, callback):
        super(TimerOff, self).__init__(callback, self.TIMER_STEP)

    def get_draw_buffer(self):
        if (self.timer is None):
            return [
                Symbols.O,
                Symbols.F,
                Symbols.F,
                Symbols.NONE,
                Symbols.MIDDLE,
                Symbols.MIDDLE,
                Symbols.MIDDLE,
                Symbols.MIDDLE
            ]
        else:
            hour = self.timer.hour
            minute = self.timer.minute
            return [
                Symbols.O,
                Symbols.F,
                Symbols.F,
                Symbols.NONE,
                Symbols.NUMBER[int(hour / 10)],
                Symbols.NUMBER[hour % 10] + Symbols.DOT,
                Symbols.NUMBER[int(minute / 10)],
                Symbols.NUMBER[minute % 10]
            ]


class TimerOn(Timer):
    TIMER_STEP = 30

    def __init__(self, callback):
        super(TimerOn, self).__init__(callback, self.TIMER_STEP)

    def get_draw_buffer(self):
        if (self.timer is None):
            return [
                Symbols.O,
                Symbols.N,
                Symbols.NONE,
                Symbols.NONE,
                Symbols.MIDDLE,
                Symbols.MIDDLE,
                Symbols.MIDDLE,
                Symbols.MIDDLE
            ]
        else:
            hour = self.timer.hour
            minute = self.timer.minute
            return [
                Symbols.O,
                Symbols.N,
                Symbols.NONE,
                Symbols.NONE,
                Symbols.NUMBER[int(hour / 10)],
                Symbols.NUMBER[hour % 10] + Symbols.DOT,
                Symbols.NUMBER[int(minute / 10)],
                Symbols.NUMBER[minute % 10]
            ]


class TimerAlert:
    TIMER_STEP = 10

    def __init__(self, callback):
        self.callback = callback
        self.timer_index = 0
        self.timers = []

    def get_draw_buffer(self):
        if (len(self.timers) <= self.timer_index or self.timers[self.timer_index].timer is None):
            return [
                Symbols.T1,
                Symbols.T2,
                Symbols.NUMBER[self.timer_index],
                Symbols.NONE,
                Symbols.MIDDLE,
                Symbols.MIDDLE,
                Symbols.MIDDLE,
                Symbols.MIDDLE
            ]
        else:
            hour = self.timers[self.timer_index].timer.hour
            minute = self.timers[self.timer_index].timer.minute
            return [
                Symbols.T1,
                Symbols.T2,
                Symbols.NUMBER[self.timer_index],
                Symbols.NONE,
                Symbols.NUMBER[int(hour / 10)],
                Symbols.NUMBER[hour % 10] + Symbols.DOT,
                Symbols.NUMBER[int(minute / 10)],
                Symbols.NUMBER[minute % 10]
            ]

    def get_draw_menu_buffer(self):
        if (self._have_timers()):
            self.timer_index = len(self.timers) - 1
        else:
            self.timer_index = 0
        return self.get_draw_buffer()

    def run(self):
        for i in range(len(self.timers) - 1, -1, -1):
            if not self.timers[i].is_set():
                del self.timers[i]
            else:
                self.timers[i].run()

    def add_timer(self):
        if (len(self.timers) < 10):
            new_timer = Timer(self.callback, self.TIMER_STEP, False)
            if (self._have_timers()):
                new_timer.timer = self.timers[len(self.timers) - 1].timer
                for i in range(6):
                    new_timer.increase()
            self.timers.append(new_timer)

    def _have_timers(self):
        return len(self.timers) > 0

    def is_set(self):
        for timer in self.timers:
            if (timer.is_set()):
                return True
        return False

    def reset(self):
        self.timer_index = 0
        self.timers = []

    def increase(self):
        if (not self._have_timers()):
            self.add_timer()
        self.timers[len(self.timers) - 1].increase()

    def decrease(self):
        if (not self._have_timers()):
            self.add_timer()
        self.timers[len(self.timers) - 1].decrease()

    def is_visible(self, seconds):
        self.timer_index = seconds // Timer.VISIBLE_FOR_SECONDS
        return seconds < Timer.VISIBLE_FOR_SECONDS * len(self.timers)
