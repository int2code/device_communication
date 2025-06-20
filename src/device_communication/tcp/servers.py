"""TCP servers implementation."""

import logging
import socket
import socketserver
import threading
from queue import Queue
from typing import Optional, Tuple

from device_communication.tcp.packetizer import ThreadedTCPRequestHandler

logger = logging.getLogger(__name__)


class ThreadedTCPServer(socketserver.TCPServer):
    """Threaded TCP Server."""

    timeout = 0.1

    def __init__(
        self,
        server_address: Tuple[str, int],
        peer_address: Tuple[str, int],
        request_handler_cls: type(ThreadedTCPRequestHandler),
        name: str = "",
        bind_and_activate: bool = True,
    ):  # pylint: disable=too-many-arguments, too-many-positional-arguments
        super().__init__(
            server_address, request_handler_cls, bind_and_activate=bind_and_activate
        )

        self.incoming_buffer = Queue()
        self.name = (
            f"{name} [{server_address[1]}]" if name else f"[{server_address[1]}]"
        )
        self._server_thread = None
        self.peer_address = peer_address

    def start(self):
        """Start the server thread."""
        self._server_thread = threading.Thread(target=self.serve_forever, args=(0.1,))
        # Exit the server thread when the main thread terminates
        self._server_thread.daemon = True
        self._server_thread.start()
        logger.debug(
            "Server loop running in thread: %s, %s",
            self._server_thread.name,
            self.peer_address,
        )

    def stop(self):
        """Stop the server thread."""
        self.shutdown()
        self._server_thread.join()
        self.server_close()

    def __enter__(self):
        super().__enter__()
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        super().__exit__(exc_type, exc_val, exc_tb)

    def write(self, data, peer_address: Optional[Tuple[str, int]] = None):
        """Write data to peer.

        :param data: raw data to write
        :param peer_address: destination address, if not given peer address is used

        """
        _peer_address = peer_address or self.peer_address
        self.socket.sendto(data, _peer_address)


# pylint: disable=too-many-instance-attributes
class ThreadedTcpClient:
    """Threaded TCP Server."""

    timeout = 0.1
    address_family = socket.AF_INET
    allow_reuse_address = False
    allow_reuse_port = True

    def __init__(
        self,
        server_address: Tuple[str, int],
        request_handler_cls: type(ThreadedTCPRequestHandler),
        client_address: Optional[Tuple[str, int]] = None,
        name: str = "",
    ):
        self._server_address = server_address
        self._client_address = client_address

        self.socket = None

        self.incoming_buffer = Queue()
        self.name = (
            f"{name} [{server_address[1]}]" if name else f"[{server_address[1]}]"
        )
        self._request_handler_cls = request_handler_cls
        self._listener_thread = None
        self.__shutdown_request = False
        self.__is_shut_down = threading.Event()

    def _create_socket(self):
        client_socket = socket.socket(self.address_family, socket.SOCK_STREAM)
        if self.allow_reuse_address and hasattr(socket, "SO_REUSEADDR"):
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.allow_reuse_port and hasattr(socket, "SO_REUSEPORT"):
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        client_socket.settimeout(self.timeout)
        if self._client_address:
            client_socket.bind(self._client_address)
        return client_socket

    def _handle_request(self, data, addr):
        self._request_handler_cls(
            request=(data, addr),
            client_address=addr,
            server=self,
        )

    def _listen_forever(self):
        """Listen for incoming connections and handle them."""
        self.__is_shut_down.clear()
        while not self.__shutdown_request:
            try:
                data, addr = self.socket.recvfrom(1024)
                if data:
                    logger.debug("Received data: %s from %s", data, addr)
                    self._handle_request(data, addr)
            except socket.timeout:
                continue
            except Exception as e:  # pylint: disable=broad-except
                logger.error("Error in listening thread: %s", e)
                break
        self.__shutdown_request = False
        self.__is_shut_down.set()

    def start(self):
        """Start the server thread."""
        self.socket = self._create_socket()
        self.socket.connect(self._server_address)
        self._listener_thread = threading.Thread(target=self._listen_forever)
        # Exit the server thread when the main thread terminates
        self._listener_thread.daemon = True
        self._listener_thread.start()
        logger.debug(
            "Server loop running in thread: %s, %s",
            self._listener_thread.name,
            self._client_address,
        )

    def shutdown(self):
        """Stops the listen_forever loop.

        Blocks until the loop has finished. This must be called while
        serve_forever() is running in another thread, or it will
        deadlock.
        """
        self.__shutdown_request = True
        self.__is_shut_down.wait(timeout=5)

    def stop(self):
        """Stop the server thread."""
        self.shutdown()
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:  # pylint: disable=broad-except
                logger.error("Error closing socket: %s", e)
        if self._listener_thread:
            self._listener_thread.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def write(self, data, peer_address: Optional[Tuple[str, int]] = None):
        """Write data to peer.

        :param data: raw data to write
        :param peer_address: destination address, if not given peer address is used

        """
        _peer_address = peer_address or self._client_address
        self.socket.sendto(data, _peer_address)
