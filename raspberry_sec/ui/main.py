import tornado.ioloop
import tornado.web
import tornado.websocket
import multiprocessing as mp
import os, sys
import logging
import base64
import cv2
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from raspberry_sec.system.main import PCARuntime
from raspberry_sec.interface.producer import Type


class BaseHandler(tornado.web.RequestHandler):

    PCA_RUNTIME = 'pca'

    CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../..', 'config/prod/pca_system.json')

    def initialize(self, shared_data):
        self.shared_data = shared_data

    def get_pca_runtime(self):
        if self.shared_data.__contains__(BaseHandler.PCA_RUNTIME):
            return self.shared_data[BaseHandler.PCA_RUNTIME]
        else:
            return None

    def set_pca_runtime(self, value):
        self.shared_data[BaseHandler.PCA_RUNTIME] = value


class MainHandler(BaseHandler):

    LOGGER = logging.getLogger('MainHandler')

    def get(self):
        """
        Returns index.html
        """
        MainHandler.LOGGER.info('Handling GET message')
        self.render('index.html')


class ConfigureHandler(BaseHandler):

    LOGGER = logging.getLogger('ConfigureHandler')

    def get(self):
        """
        Returns the configure.html template
        """
        ConfigureHandler.LOGGER.info('Handling GET message')
        with open(BaseHandler.CONFIG_PATH, 'r') as file:
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
            with open(BaseHandler.CONFIG_PATH, 'w') as file:
                file.write(new_config)
            self.write('Success')
        else:
            self.write('Error')


class ControlHandler(BaseHandler):

    LOGGER = logging.getLogger('ControlHandler')

    def status(self):
        """
        Builds the dictionary the template engine will use for filling the html
        """
        status = dict()
        if self.get_pca_runtime():
            status['text'] = 'Online'
            status['start'] = 'disabled'
            status['stop'] = ''
        else:
            status['text'] = 'Offline'
            status['start'] = ''
            status['stop'] = 'disabled'
        return status

    def stop_pca(self):
        """
        Stops the service if still running
        """
        ControlHandler.LOGGER.info('Stopping PCA')
        runtime = self.get_pca_runtime()
        if runtime:
            runtime.stop()
            self.set_pca_runtime(None)

    def start_pca(self):
        """
        Starts the service
        """
        ControlHandler.LOGGER.info('Starting PCA')
        self.set_pca_runtime(PCARuntime(PCARuntime.load_pca(BaseHandler.CONFIG_PATH)))
        self.get_pca_runtime().start(logging.INFO)

    def get(self):
        """
        Returns control.html
        """
        ControlHandler.LOGGER.info('Handling GET message')
        status = self.status()
        self.render('control.html', status=status)

    def post(self):
        """
        Controls the PCA system
        """
        ControlHandler.LOGGER.info('Handling POST message')
        self.set_header('Content-Type', 'text/plain')
        on = 'true' == self.get_argument('on')

        if on:
            self.stop_pca()
            self.start_pca()
        else:
            self.stop_pca()


class FeedHandler(BaseHandler):

    LOGGER = logging.getLogger('FeedHandler')

    def get(self):
        """
        Returns feed.html
        """
        FeedHandler.LOGGER.info('Handling GET message')
        runtime = self.get_pca_runtime()
        if runtime:
            producers = [p.get_name() for p in runtime.pca_system.producer_set if Type.CAMERA == p.get_type()]
        else:
            producers = []

        self.render('feed.html', producers=producers)


class FeedWebSocketHandler(tornado.websocket.WebSocketHandler, BaseHandler):

    LOGGER = logging.getLogger('FeedWebSocketHandler')

    def open(self):
        """
        On opening a websocket
        """
        FeedWebSocketHandler.LOGGER.info('Opening web-socket')
        pass

    def img_to_str(self, img):
        """
        Converts the numpy ndarray into a HTML compatible png src
        :param img: numpy array
        :return: HTML compatible img src
        """
        resized = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
        png_encoded = cv2.imencode('.png', resized)[1]
        b64_encoded = base64.b64encode(png_encoded.tostring())
        return b64_encoded.decode('utf-8')

    def on_message(self, message):
        """
        On incoming message this method fetches an image from the given producer and sends it back
        :param message: name of the producer
        """
        FeedWebSocketHandler.LOGGER.info('Handling web-socket message')
        selected = message
        runtime = self.get_pca_runtime()

        if not runtime or not [p for p in runtime.pca_system.producer_set if p.get_name() == selected]:
            self.write_message('ERROR')
        else:
            producer = [p for p in runtime.pca_system.producer_set if p.get_name() == selected][0]
            proxy = runtime.pca_system.prod_to_proxy[producer]
            img = self.img_to_str(proxy.get_data())
            self.write_message('<img class="img-responsive center-block" src="data:image/png;base64,' + img + '">')

    def on_close(self):
        FeedWebSocketHandler.LOGGER.info('Closing web-socket')
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
    config = dict(shared_data=dict())
    settings = {
        'template_path': 'template',
        'static_path': 'static',
    }
    return tornado.web.Application([
        (r'/', MainHandler, config),
        (r'/configure', ConfigureHandler, config),
        (r'/control', ControlHandler, config),
        (r'/feed', FeedHandler, config),
        (r'/feed/websocket', FeedWebSocketHandler, config),
        (r'/about', AboutHandler, config),
        (r'/login', LoginHandler, config)
    ], **settings)


if __name__ == '__main__':
    mp.set_start_method('spawn')
    logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s - %(message)s', level=logging.INFO)
    app = make_app()
    app.listen(59787)
    tornado.ioloop.IOLoop.current().start()
