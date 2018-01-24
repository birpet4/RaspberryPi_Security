import tornado.ioloop
import tornado.web
import tornado.websocket
import multiprocessing as mp
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))


class BaseHandler(tornado.web.RequestHandler):

    PCA_RUNTIME = None


class MainHandler(BaseHandler):

    def get(self):
        self.render('index.html')


class ConfigureHandler(BaseHandler):

    CONFIG_PATH = 'config/prod/pca_system.json'

    def get(self):
        abs_path = os.path.join(os.path.dirname(__file__), '../..', ConfigureHandler.CONFIG_PATH)
        with open(abs_path, 'r') as file:
            config = file.read()

        self.render('configure.html', configuration=config)


class ControlHandler(BaseHandler):

    @staticmethod
    def status():
        if ControlHandler.PCA_RUNTIME:
            return 'Online'
        else:
            return 'Offline'

    def get(self):
        status = ControlHandler.status()
        self.render('control.html', status=status)


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

    def get(self):
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
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
