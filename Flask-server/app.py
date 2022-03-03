from __future__ import annotations, print_function
from datetime import date
import logging
from typing import Any, TextIO, Tuple
from enum import Enum
from colorama import Fore, Style
from flask import Flask, jsonify, request
from flask.wrappers import Response
from http import HTTPStatus
import os
# from geventwebsocket.handler import WebSocketHandler
# from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
# from gevent.pywsgi import WSGIServer
from flask_socketio import SocketIO, send, emit
# from flask_socketio.exceptions


class SocketType(Enum):
    flask_socketio = 0
    gevents_socketio = 1
    WSGIServer = 2
    
wsConnType = SocketType.flask_socketio
use_https = False
app = Flask(__name__)

app.config['GEMBER_HTTPS_KEYFILE'] = '/private/etc/ssl/localhost/localhost.key'
app.config['GEMBER_HTTPS_CERTFILE'] = '/private/etc/ssl/localhost/localhost.crt'
app.config['GEMBER_BIND_HOST'] = '127.0.0.1'
app.config['GEMBER_PORT'] = 8444
app.secret_key = os.urandom(24)
app.config['SECRET_KEY'] = 'secret!'
app.config["ALLOW_THREADING"] = False
app.config['DEBUG_APP'] = True


def wrap_CORS_response(response: Response):
    response.headers['Access-Control-Allow-Origin'] = request.origin
    return response

@app.route('/')
def index():
    return wrap_CORS_response(response=Response('flask app connected over http',status=HTTPStatus.OK))


@app.route('/anon')
def anon():
    return wrap_CORS_response(response=Response(f'hi anon',status=HTTPStatus.OK))


@app.route('/name/<name>')
def indexwName(name):
    return wrap_CORS_response(response=Response(f'hi {name}', status=HTTPStatus.OK))

socketio = SocketIO(app, path='socket.io')

def handle_message(message:str):
    logging.debug(
        f'Client: [{message}], Server: [Message handled]')

@socketio.on('message')
def handle_message_socketio(message):
    '''Client sends us a message:str -> simply return the same message back to the client'''
    handle_message(message)
    send(
        f'Client: [{message}], Server: [This is my response :)]')


HOST = app.config['GEMBER_BIND_HOST']  # or try '0.0.0.0'
PORT = app.config['GEMBER_PORT']

ssl_args = {}
if use_https:
    ssl_args = {
        'keyfile': app.config.get('GEMBER_HTTPS_KEYFILE'),
        'certfile': app.config.get('GEMBER_HTTPS_CERTFILE')
    }
    

# https://kracekumar.com/post/54437887454/ssl-for-flask-local-development/



httpEchoApplication = app


    



 
# Link to the original issue with Socket-IO using flutter: https://stackoverflow.com/questions/60348534/connecting-flask-socket-io-server-and-flutter
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(logging.FileHandler('gpAppLog.log'))
if use_https:
    pass
    # logging.debug(Fore.BLUE + 'Running HTTPS' + Style.RESET_ALL)
    # https_server = WSGIServer((HOST,PORT), 
    #                             Resource({
    #                                 '/': httpEchoApplication, 
    #                                 '/websocket': WSEchoApplication
    #                                 }),
    #                             handler_class=WebSocketHandler, 
    #                             **ssl_args)
    # https_server.serve_forever()
else:
    # with CaptureOutput() as capturer:
    logging.debug(Fore.YELLOW + 'Running HTTP' + Style.RESET_ALL)
    if wsConnType == SocketType.WSGIServer:
        pass
    elif wsConnType == SocketType.flask_socketio:
        pass
    elif wsConnType == SocketType.gevents_socketio:
        # def not_found(start_response):
        #     start_response('404 Not Found', [])
        #     return ['<h1>Not Found</h1>']

        # from gevent import monkey
        # monkey.patch_all()

        # from socketio import socketio_manage
        # from socketio.server import SocketIOServer
        # from socketio.namespace import BaseNamespace
        # from socketio.mixins import RoomsMixin, BroadcastMixin

        # class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):

        #     def on_nickname(self, nickname):
        #         self.request['nicknames'].append(nickname)
        #         self.socket.session['nickname'] = nickname
        #         self.broadcast_event('announcement', '%s has connected' % nickname)
        #         self.broadcast_event('nicknames', self.request['nicknames'])
        #         # Just have them join a default-named room
        #         self.join('main_room')

        #     def recv_disconnect(self):
        #         # Remove nickname from the list.
        #         nickname = self.socket.session['nickname']
        #         self.request['nicknames'].remove(nickname)
        #         self.broadcast_event(
        #             'announcement', '%s has disconnected' % nickname)
        #         self.broadcast_event('nicknames', self.request['nicknames'])

        #         self.disconnect(silent=True)

        #     def on_user_message(self, msg):
        #         self.emit_to_room('main_room', 'msg_to_room',
        #                         self.socket.session['nickname'], msg)

        #     def recv_message(self, message):
        #         print("PING!!!", message)
        
        # class WSEchoApp2(WSEchoApplication):
        #     def __init__(self):
        #         self.buffer = []
        #         # Dummy request object to maintain state between Namespace
        #         # initialization.
        #         self.request = {
        #             'nicknames': [],
        #         }


        #     def __call__(self, environ, start_response):
        #         path = environ['PATH_INFO'].strip('/')

        #         if not path:
        #             start_response('200 OK', [('Content-Type', 'text/html')])
        #             return ['<h1>Welcome. '
        #                     'Try the <a href="/chat.html">chat</a> example.</h1>']

        #         if path.startswith('static/') or path == 'chat.html':
        #             try:
        #                 data = open(path).read()
        #             except Exception:
        #                 return not_found(start_response)

        #             if path.endswith(".js"):
        #                 content_type = "text/javascript"
        #             elif path.endswith(".css"):
        #                 content_type = "text/css"
        #             elif path.endswith(".swf"):
        #                 content_type = "application/x-shockwave-flash"
        #             else:
        #                 content_type = "text/html"

        #             start_response('200 OK', [('Content-Type', content_type)])
        #             return [data]

        #         if path.startswith("socket.io"):
        #             socketio_manage(environ, {'': ChatNamespace}, self.request)
        #         else:
        #             return not_found(start_response)
        
        pass
    else:
        raise Exception('Not implemented')


if __name__ == '__main__':
    # if wsConnType == SocketType.WSGIServer:
        # class WSEchoApplication(WebSocketApplication):
        #     def on_open(self):
        #         print(Fore.YELLOW, "Connection opened", Style.RESET_ALL)

        #     def on_message(self, message):
        #         print(Fore.CYAN, message, Style.RESET_ALL)
        #         self.ws.send(message)

        #     def on_close(self, reason):
        #         print(Fore.YELLOW, reason, Style.RESET_ALL)
        # WSGIServer((HOST, PORT),
        #            Resource({
        #                '/': httpEchoApplication,
        #                '/websocket': WSEchoApplication
        #            }),
        #            handler_class=WebSocketHandler).serve_forever()
    if wsConnType == SocketType.flask_socketio:
        socketio.run(httpEchoApplication, host=HOST, port=PORT)
    if wsConnType == SocketType.gevents_socketio:
        pass

