"""UDP servers implementation"""

import logging
import socketserver
import threading
from queue import Queue
from typing import Optional, Tuple

from device_communication.udp.packetizer import ThreadedUDPRequestHandler

logger = logging.getLogger(__name__)


class ThreadedUDPServer(socketserver.UDPServer):
    """
    Threaded UDP Server.

    :param server_address: Address and port for the server to bind to.
    :param peer_address: Address and port of the peer to communicate with.
    :param request_handler_cls: Class to handle incoming requests.
    :param name: Optional name for the server instance.
    :param bind_and_activate: Whether to bind and activate the server immediately.

    """

    timeout = 0.1

    def __init__(
        self,
        server_address: Tuple[str, int],
        peer_address: Tuple[str, int],
        request_handler_cls: type(ThreadedUDPRequestHandler),
        name: str = "",
        bind_and_activate: bool = True,
    ):
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
