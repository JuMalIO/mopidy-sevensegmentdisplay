import os
import tornado.template
import tornado.web


template_directory = os.path.join(os.path.dirname(__file__), 'templates')
template_loader = tornado.template.Loader(template_directory)


class BaseRequestHandler(tornado.web.RequestHandler):
    def initialize(self, config, core, worker):
        self.config = config
        self.core = core
        self.worker = worker

    def send_message(self, code):
        self.worker.response_code = code
        self.redirect('/sevensegmentdisplay/')


class MainRequestHandler(BaseRequestHandler):
    def get(self):
        self.write(template_loader.load('index.html').generate(
            config=self.config,
            core=self.core,
            worker=self.worker
        ))


class ApiRequestHandler(BaseRequestHandler):
    def post(self):
        state = str(self.get_argument('state', ''))
        if (state == 'play'):
            self.worker.play_music()
        elif (state == 'pause'):
            self.worker.pause_music()
        elif (state == 'stop'):
            self.worker.stop_music()
        elif (state == 'play_stop'):
            self.worker.play_stop_music()

        volume = int(self.get_argument('volume', 0))
        if (volume >= 1 and volume <= 100):
            self.worker.set_volume(volume)

        off = str(self.get_argument('off', ''))
        if (off == 'set'):
            hour = self.get_argument('hour', None)
            minute = self.get_argument('minute', None)
            self.worker.timer_off.set(
                None if hour is None or not hour else int(hour),
                None if minute is None or not minute else int(minute))
        elif (off == 'clear'):
            self.worker.timer_off.reset()
        elif (off == '-'):
            self.worker.timer_off.decrease()
        elif (off == '+'):
            self.worker.timer_off.increase()
        elif (off):
            self.worker.timer_off.set(int(off))

        on = str(self.get_argument('on', ''))
        if (on == 'set'):
            hour = self.get_argument('hour', None)
            minute = self.get_argument('minute', None)
            self.worker.timer_on.set(
                None if hour is None or not hour else int(hour),
                None if minute is None or not minute else int(minute))
        elif (on == 'clear'):
            self.worker.timer_on.reset()
        elif (on == '-'):
            self.worker.timer_on.decrease()
        elif (on == '+'):
            self.worker.timer_on.increase()
        elif (on):
            self.worker.timer_on.set(int(on))

        alert = str(self.get_argument('alert', ''))
        if (alert == 'add'):
            hour = self.get_argument('hour', None)
            minute = self.get_argument('minute', None)
            self.worker.timer_alert.add_timer(
                None if hour is None or not hour else int(hour),
                None if minute is None or not minute else int(minute))
        elif (alert == 'clear'):
            self.worker.timer_alert.reset()
        elif (alert == '-'):
            self.worker.timer_alert.decrease()
        elif (alert == '+'):
            self.worker.timer_alert.increase()
        elif (alert == 'run'):
            self.worker.run_alert()
        elif (alert):
            self.worker.run_alert(int(alert))

        preset = str(self.get_argument('preset', ''))
        if (preset != ''):
            self.worker.set_preset(preset)

        self.write(str(self.worker.get_volume()))
        self.write(self.worker.get_state())


def factory_decorator(worker):
    def app_factory(config, core):
        # since all the RequestHandler-classes get the same arguments ...
        def bind(url, klass):
            return (url, klass, {'config': config['sevensegmentdisplay'], 'core': core, 'worker': worker})

        return [
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static')}),
            bind('/', MainRequestHandler),
            bind('/api/', ApiRequestHandler)
        ]

    return app_factory
