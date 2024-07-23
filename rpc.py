import base64
import json
import logging
import os
import sys
import threading
from multiprocessing import AuthenticationError
from multiprocessing.connection import Client, Listener

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "deps.zip"))

from jsonrpc.dispatcher import Dispatcher
from jsonrpc.manager import JSONRPCResponseManager

try: # python 2
    from SocketServer import BaseRequestHandler, BaseServer, ThreadingMixIn
except ImportError: # python 3
    from socketserver import BaseRequestHandler, BaseServer, ThreadingMixIn

__all__ = ["add_method"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class MultiProcessingSever(BaseServer):
    def __init__(self, server_address, RequestHandlerClass, authkey=None):
        BaseServer.__init__(self, server_address, RequestHandlerClass)
        self.authkey = authkey

    def serve_forever(self, seperate_thread=True):
        if seperate_thread:
            t = threading.Thread(target=self.serve_forever, args=(False,))
            t.setDaemon(True)
            t.start()
        else:
            self.server_activate()
            self.__shutdown_request = False
            try:
                while not self.__shutdown_request:
                    self.handle_request()
            finally:
                self.__shutdown_request = False

    def handle_request(self):
        self._handle_request_noblock()

    def server_activate(self):
        #  on unix unlink the socket first,
        if os.name != "nt" and os.path.exists(self.server_address):
            os.unlink(self.server_address)
        self.socket = Listener(self.server_address, authkey=self.authkey)

    def server_close(self):
        self.__shutdown_request = True
        client = Client(self.server_address)
        self.socket.close()

    def get_request(self):
        while not self.__shutdown_request:
            try:
                return self.socket.accept(), self.socket.last_accepted
            except (AuthenticationError, EOFError, IOError):
                pass

    def close_request(self, request):
        request.close()


class JsonRpcRequestHandler(BaseRequestHandler):
    def handle(self):
        logger.debug("client %s connected", self.request)
        while True:
            try:
                data = self.request.recv_bytes()
            except EOFError:
                logger.debug("client %s disconnected ", self.request)
                break
            response = JSONRPCResponseManager.handle(data, self.server.dispatcher)
            if response:
                self.request.send_bytes(response.json.encode())


class RPCServer(ThreadingMixIn, MultiProcessingSever):
    daemon_threads = True

    @property
    def dispatcher(self):
        if not hasattr(self, "_dispatcher"):
            self._dispatcher = Dispatcher()
        return self._dispatcher

    def add_method(self, method, name=None):
        return self.dispatcher.add_method(method, name)

    def remove_method(self, name):
        self.dispatcher.pop(name, None)


CREDENTIALS_FILE = os.path.expanduser(os.path.join("~", ".voicerpc.json"))

# protect against reloads
try:
    SERVERS
except NameError:
    SERVERS = {}


def get_credentials(service):
    if not os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "w") as f:
            f.write("{}")
    with open(CREDENTIALS_FILE) as f:
        credentials = json.load(f)
    value = credentials.get(service, None)
    if value is None:
        value = os.urandom(16)
        credentials[service] = base64.b64encode(value).decode("ascii")
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(credentials, f)
    else:
        value = base64.b64decode(value.encode("ascii"))
    return value


def get_server_path(service):
    if os.name == "nt":
        return r"\\.\pipe\voicerpc\{}\{}".format(
            os.path.split(os.path.expanduser("~"))[-1], service
        )
    else:
        if not os.path.exists(os.path.expanduser("~/.voicerpc")):
            os.makedirs(os.path.expanduser("~/.voicerpc"), exist_ok=True)
        return os.path.expanduser(os.path.join("~/.voicerpc/{}.sock".format(service)))


def get_or_create_server(service):
    server = SERVERS.get(service, None)
    if server is None:
        server = RPCServer(
            get_server_path(service),
            JsonRpcRequestHandler,
            authkey=get_credentials(service),
        )
        server.serve_forever()
        logger.info(
            "Server for service %s started at %s", service, server.server_address
        )
        SERVERS[service] = server
    return server


def add_method(service="default"):
    server = get_or_create_server(service)
    return server.add_method
