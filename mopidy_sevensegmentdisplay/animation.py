import time
from threader import Threader


class Animation(Threader):

    def __init__(self, display, buffer, repeat, sleep):
        super(Animation, self).__init__()
        self.display = display
        self.buffer = buffer
        self.repeat = repeat
        self.sleep = sleep

    def run(self):
        for j in range(self.repeat):
            for i in range(len(self.buffer)):
                if (self.stopped()):
                        break
                self.display.set_buffer(self.buffer[i])
                self.display.flush()
                time.sleep(self.sleep)
            if (self.stopped()):
                break


class BlinkAnimation(Threader):

    def __init__(self, display, buffer, repeat, sleep):
        super(BlinkAnimation, self).__init__()
        self.display = display
        self.buffer = buffer
        self.repeat = repeat
        self.sleep = sleep

    def run(self):
        for j in range(self.repeat):
            if (self.stopped()):
                break
            if (j % 2 == 1):
                self.display.set_buffer(self.buffer)
            else:
                self.display.clear()
            self.display.flush()
            time.sleep(self.sleep)


class ScrollLeftAnimation(Threader):

    def __init__(self, display, buffer, sleep):
        super(ScrollLeftAnimation, self).__init__()
        self.display = display
        self.buffer = buffer
        self.sleep = sleep

    def run(self):
        for i in range(len(self.buffer)):
            if (self.stopped()):
                break
            self.display.scroll_left(self.buffer[i])
            self.display.flush()
            time.sleep(self.sleep)


class ScrollRightAnimation(Threader):

    def __init__(self, display, buffer, sleep):
        super(ScrollRightAnimation, self).__init__()
        self.display = display
        self.buffer = buffer
        self.sleep = sleep

    def run(self):
        length = len(self.buffer)
        for i in range(length):
            if (self.stopped()):
                break
            self.display.scroll_right(self.buffer[length - i - 1])
            self.display.flush()
            time.sleep(self.sleep)


class ScrollUpAnimation(Threader):
    FROM = -1
    TO = 4

    def __init__(self, display, buffer, sleep):
        super(ScrollUpAnimation, self).__init__()
        self.display = display
        self.buffer = buffer
        self.sleep = sleep

    def run(self):
        for i in range(self.FROM, self.TO):
            if (self.stopped()):
                break
            self.display.scroll_up(self.buffer, i)
            self.display.flush()
            time.sleep(self.sleep)


class ScrollDownAnimation(Threader):
    FROM = -1
    TO = 4

    def __init__(self, display, buffer, sleep):
        super(ScrollDownAnimation, self).__init__()
        self.display = display
        self.buffer = buffer
        self.sleep = sleep

    def run(self):
        for i in range(self.FROM, self.TO):
            if (self.stopped()):
                break
            self.display.scroll_down(self.buffer, i)
            self.display.flush()
            time.sleep(self.sleep)
