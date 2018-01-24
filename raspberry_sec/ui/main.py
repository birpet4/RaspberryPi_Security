import tornado.ioloop
import tornado.web
import tornado.websocket
import multiprocessing as mp
import os, sys
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from raspberry_sec.system.main import PCARuntime


class BaseHandler(tornado.web.RequestHandler):

    PCA_RUNTIME = None

    CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../..', 'config/prod/pca_system.json')


class MainHandler(BaseHandler):

    def get(self):
        self.render('index.html')


class ConfigureHandler(BaseHandler):

    LOGGER = logging.getLogger('ConfigureHandler')

    def get(self):
        """
        Returns the configure.html template
        """
        ConfigureHandler.LOGGER.info('Handling GET message')
        with open(ConfigureHandler.CONFIG_PATH, 'r') as file:
            config = file.read()

        self.render('configure.html', configuration=config)

    def post(self):
        """
        Saves the configuration
        """
        ConfigureHandler.LOGGER.info('Handling POST message')
        self.set_header('Content-Type', 'text/plain')

        new_config = self.get_argument('cfg_content')
        if new_config:
            with open(ConfigureHandler.CONFIG_PATH, 'w') as file:
                file.write(new_config)
            self.write('Success')
        else:
            self.write('Error')


class ControlHandler(BaseHandler):

    LOGGER = logging.getLogger('ControlHandler')

    @staticmethod
    def status():
        """
        Builds the dictionary the template engine will use for filling the html
        """
        status = dict()
        if ControlHandler.PCA_RUNTIME:
            status['text'] = 'Online'
            status['start'] = 'disabled'
            status['stop'] = ''
        else:
            status['text'] = 'Offline'
            status['start'] = ''
            status['stop'] = 'disabled'
        return status

    @staticmethod
    def stop_pca():
        """
        Stops the service if still running
        """
        if ControlHandler.PCA_RUNTIME:
            ControlHandler.PCA_RUNTIME.stop()
            ControlHandler.PCA_RUNTIME = None

    @staticmethod
    def start_pca():
        """
        Starts the service
        """
        ControlHandler.PCA_RUNTIME = PCARuntime(PCARuntime.load_pca(ControlHandler.CONFIG_PATH))
        ControlHandler.PCA_RUNTIME.start(logging.INFO)

    def get(self):
        """
        Returns control.html
        """
        ControlHandler.LOGGER.info('Handling GET message')
        status = ControlHandler.status()
        self.render('control.html', status=status)

    def post(self):
        """
        Controls the PCA system
        """
        ControlHandler.LOGGER.info('Handling POST message')
        self.set_header('Content-Type', 'text/plain')
        on = 'true' == self.get_argument('on')

        if on:
            ControlHandler.stop_pca()
            ControlHandler.start_pca()
        else:
            ControlHandler.stop_pca()


class FeedHandler(BaseHandler):

    def get(self):
        self.render('feed.html', producers=['1', '2'])


class FeedWebSocketHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        pass

    def on_message(self, message):
        self.write_message('HI' + message)

    def on_close(self):
        pass


class AboutHandler(BaseHandler):

    LOGGER = logging.getLogger('AboutHandler')

    def get(self):
        """
        Returns about.html
        """
        AboutHandler.LOGGER.info('Handling GET message')
        self.render('about.html')


class LoginHandler(BaseHandler):

    def get(self):
        self.render('login.html')


def make_app():
    settings = {
        'template_path': 'template',
        'static_path': 'static',
    }
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/configure', ConfigureHandler),
        (r'/control', ControlHandler),
        (r'/feed', FeedHandler),
        (r'/feed/websocket', FeedWebSocketHandler),
        (r'/about', AboutHandler),
        (r'/login', LoginHandler),
    ], **settings)


if __name__ == '__main__':
    mp.set_start_method('spawn')
    logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s - %(message)s', level=logging.INFO)
    app = make_app()
    app.listen(59787)
    tornado.ioloop.IOLoop.current().start()
