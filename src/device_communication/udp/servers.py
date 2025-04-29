"""UDP servers implementation"""

import logging
import socketserver
import threading
from queue import Queue
from typing import Optional, Tuple

from device_communication.udp.packetizer import ThreadedUDPRequestHandler

logger = logging.getLogger(__name__)


class ThreadedUDPServer(socketserver.UDPServer):
    """Threaded UDP Server."""

    daemon_threads = True
    timeout = 0.1

    def __init__(
        self,
        server_address: Tuple[str, int],
        peer_address: Tuple[str, int],
        RequestHandlerClass: ThreadedUDPRequestHandler,
        name="",
    ):
        super().__init__(server_address, RequestHandlerClass)
        self.incoming_buffer = Queue()
        self.name = (
            f"{name} [{server_address[1]}]" if name else f"[{server_address[1]}]"
        )
        self._server_thread = None
        self.peer_address = peer_address
        self._lock = threading.Lock()
        self.__is_shut_down = threading.Event()
        self.__shutdown_request = False

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
        self.shutdown()
        self._server_thread.join()
        super().__exit__(exc_type, exc_val, exc_tb)

    def serve_forever(self, poll_interval=0.01):
        """Handle one request at a time until shutdown.

        Polls for shutdown every poll_interval seconds. Ignores
        self.timeout. If you need to do periodic tasks, do them in
        another thread.
        """
        self.__is_shut_down.clear()
        while not self.__shutdown_request:
            self.handle_request()
            self.service_actions()
            if self.__shutdown_request:
                break

        self.__shutdown_request = False
        self.__is_shut_down.set()

    def shutdown(self):
        """Stops the serve_forever loop.

        Blocks until the loop has finished. This must be called while
        serve_forever() is running in another thread, or it will
        deadlock.
        """
        self.__shutdown_request = True
        self.__is_shut_down.wait()

    def write(self, data, peer_address: Optional[Tuple[str, int]] = None):
        """Write data to peer.

        :param data: raw data to write
        :param peer_address: destination address, if not given peer address is used

        """
        _peer_address = peer_address or self.peer_address
        self.socket.sendto(data, _peer_address)
