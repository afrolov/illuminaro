from __future__ import print_function

import json
import os
import logging
import argparse

import tornado.ioloop
import tornado.web
from tornado import websocket
from illuminaro.py23compat import iteritems

illuminaro_app_log = logging.getLogger("illuminaro.application")

ValueSet = argparse.Namespace


class IlluminaroAPIHandler(websocket.WebSocketHandler):
    def initialize(self, app, additional_arguments=None):
        self.app = app
        self.additional_arguments = additional_arguments if additional_arguments else dict()
        illuminaro_app_log.info('Illuminaro: API handler ready')

    def open(self):
        illuminaro_app_log.info('Illuminaro: WebSocket opened')

    def on_message(self, message):
        illuminaro_app_log.info('Illuminaro: got message: ' + str(message))
        if message is None:
            return
        messageObject = json.loads(message)

        # Initialize of update application values
        if messageObject['method'] == 'init':
            self.app.values = ValueSet(**messageObject['data'])
        elif messageObject['method'] == 'update':
            updated = False
            for k, v in iteritems(messageObject['data']):
                if self.app.values.__getattribute__(k) != v:
                    self.app.values.__setattr__(k, v)
                    updated = True
            if not updated:
                illuminaro_app_log.debug('Illuminaro: No new values, update ignored')
                return

        if self.app.server:
            updatedValues = ValueSet()
            self.app.server(self.app, self.app.values, updatedValues, **self.additional_arguments)
            responseValues = vars(updatedValues)
            responseString = json.dumps({'values': vars(updatedValues)})
            if self.app.debug:
                debugValues = responseValues.copy()
                for k, v in iteritems(debugValues):
                    if v.startswith('data:image'):
                        debugValues[k] = '<image data>'
                        illuminaro_app_log.debug('Illuminaro: response: ' + str(debugValues))
            self.write_message(responseString)

    def on_close(self):
        illuminaro_app_log.info('Illuminaro: WebSocket closed')


class IlluminaroInterfaceHandler(tornado.web.RequestHandler):
    def initialize(self, app, additional_arguments=None):
        self.app = app
        self.additional_arguments = additional_arguments if additional_arguments else dict()
        illuminaro_app_log.info('Illuminaro: interface handler ready')

    def get(self):
        illuminaro_app_log.debug("IlluminaroInterfaceHandler.get()")
        self.write(self.app.gui.render())


class IlluminaroApp:
    def __init__(self, gui, server=None, port=5000, **kwargs):
        self.gui = gui
        self.server = server
        self.port = port
        self.values = ValueSet()
        self.debug = kwargs['debug'] if 'debug' in kwargs else False
        if self.debug:
            illuminaro_app_log.setLevel(logging.DEBUG)
        illuminaro_app_log.debug('IlluminaroApp.__init__')
        self.application = tornado.web.Application([
            (r"/", IlluminaroInterfaceHandler, dict(app=self, additional_arguments=kwargs)),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': os.path.join(os.getcwd(),'static')}), # FIXME
            (r"/api", IlluminaroAPIHandler, dict(app=self, additional_arguments=kwargs)),
        ], **kwargs)

    def run(self):
        illuminaro_app_log.debug('IlluminaroApp.run')
        self.application.listen(self.port)
        ili = tornado.ioloop.IOLoop.instance()
        # To handle pesky Ctrl-C
        tornado.ioloop.PeriodicCallback(lambda: None, 500, ili).start()
        ili.start()


