from __future__ import unicode_literals

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
            config = self.config['sevensegmentdisplay'],
            core = self.core,
            worker = self.worker
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
        elif (state == 'invert'):
           self.worker.play_stop_music()
        volume = int(self.get_argument('volume', 0))
        if (volume >= 1 and volume <= 100):
           self.worker.set_volume(volume)
        sleep = int(self.get_argument('sleep', 0))
        if (sleep > 0):
           self.worker.increase_timer()
        elif (sleep < 0):
           self.worker.decrease_timer()
        self.write(str(self.worker.get_volume()))
        self.write(self.worker.get_state())


def factory_decorator(worker):
    def app_factory(config, core):
        # since all the RequestHandler-classes get the same arguments ...
        bind = lambda url, klass: (url, klass, {'config': config, 'core': core, 'worker': worker})

        return [
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static')}),
            bind('/', MainRequestHandler),
            bind('/api/', ApiRequestHandler)
        ]

    return app_factory
