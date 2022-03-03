from __future__ import annotations, print_function
from datetime import date
from typing import TextIO, Tuple
from enum import Enum
from colorama import Fore, Style
from flask import Flask, jsonify, request
from flask.wrappers import Response, Request
from http import HTTPStatus
import os
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from gevent.pywsgi import WSGIServer

class SocketType(Enum):
    socketio = 0
    WSGIServer = 1
    
app = Flask(__name__)
# TODO P1 v1.0: Read from Env File (Check the clickshop code for example...) - for secret config, 
# not for how to set config on a flask app
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


HOST = app.config['GEMBER_BIND_HOST']  # or try '0.0.0.0'
PORT = app.config['GEMBER_PORT']
use_https = False
ssl_args = {}
if use_https:
    ssl_args = {
        'keyfile': app.config.get('GEMBER_HTTPS_KEYFILE'),
        'certfile': app.config.get('GEMBER_HTTPS_CERTFILE')
    }
wsConnType = SocketType.WSGIServer
    
if __name__ == '__main__':
    # from httpRoutes import *
    
    # https://kracekumar.com/post/54437887454/ssl-for-flask-local-development/
    
    # ------------------------------------------Socketio----------------------------------------------------
    
    if wsConnType == SocketType.socketio:
        from flask_socketio import SocketIO, send, emit
        socketio = SocketIO(app)
        socketio.run(app, host=HOST, port=PORT) # BUG: eventlet doesnt support ssl_context kwargs.
        # socketio.run(app, host=HOST, port=PORT, ssl_context='adhoc') 
        
        # NOTE: The default Flask development server doesn't support websockets so you'll need to use another server. Thankfully it's simple to get eventlet working with Flask. All you should have to do is install the eventlet package using pip.
        # $ (conda venv) conda install -c conda-forge eventlet
        # Once eventlet is installed socketio will detect and use it when running the server.
        # You can use chrome to double check what transport method is being used. 
        #   Open your chrome dev tools Ctrl+Shift+I in Windows and go to the Network tab. 
        #   On each network request you should see either transport=polling or transport=websocket
        # If running flask app on Heroku, use these links to set up SSL:
        # https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-18-04
        # https://stackoverflow.com/questions/53992331/cant-connect-to-flask-socketio-via-wss-but-works-via-ws
        

    # -------------------------BASIC Server-------------------------
    
    if wsConnType == SocketType.WSGIServer:
        class WSEchoApplication(WebSocketApplication):
            def on_open(self):
                print(Fore.YELLOW,"Connection opened",Style.RESET_ALL)

            def on_message(self, message):
                print(Fore.CYAN,message,Style.RESET_ALL)
                self.ws.send(message)

            def on_close(self, reason):
                print(Fore.YELLOW,reason,Style.RESET_ALL)
                
        
        
        
        httpEchoApplication = app
            
    
        try:
            import logging
            # import subprocess
            # from capturer import CaptureOutput
            # , filename='app.log'
            # logging.basicConfig(level=logging.DEBUG)
            # Link to the original issue with Socket-IO using flutter: https://stackoverflow.com/questions/60348534/connecting-flask-socket-io-server-and-flutter
            logging.getLogger().setLevel(logging.DEBUG)
            logging.getLogger().addHandler(logging.FileHandler('gpAppLog.log'))
            if use_https:
                logging.debug(Fore.BLUE + 'Running HTTPS' + Style.RESET_ALL)
                https_server = WSGIServer((HOST,PORT), 
                                          Resource({
                                              '/': httpEchoApplication, 
                                              '/websocket': WSEchoApplication
                                              }),
                                          handler_class=WebSocketHandler, 
                                          **ssl_args)
                https_server.serve_forever()
            else:
                # with CaptureOutput() as capturer:
                logging.debug(Fore.YELLOW + 'Running HTTP' + Style.RESET_ALL)
                _app = Resource({
                    '/': httpEchoApplication, 
                    '/websocket': WSEchoApplication
                }) # Turn EchoApplication into MyApp 
                http_server = WSGIServer((HOST,PORT), 
                                         _app, 
                                         handler_class=WebSocketHandler)
                http_server.serve_forever()
        except Exception as e:
            logging.debug(
                Fore.RED + f'WebApp level exception at app.py of: \n\t{e}' + Style.RESET_ALL)
