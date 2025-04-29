"""UDP communication handlers."""

from contextlib import contextmanager
from queue import Empty
from typing import List, Optional

from device_communication.base.communication_handlers import BaseCommunicationHandler
from device_communication.udp.packetizer import ThreadedUDPRequestHandler
from device_communication.udp.servers import ThreadedUDPServer


class UdpCommunicationHandler(BaseCommunicationHandler):
    """Layer between user/client and Server

    Maintains UDP Server running while providing methods for reading and writing from and to the tar

    Class that maintains the UDP Server thread running. Connects user/client to server
    instance for writing and reading binary data.

    """

    # pylint: disable=too-many-arguments, too-many-instance-attributes, too-many-positional-arguments

    def __init__(
        self,
        ip_address,
        in_port: int,
        out_port: int,
        timeout: int = 5,
        name: Optional[str] = None,
    ):
        super().__init__()
        self._ip_address = ip_address
        self._out_port = out_port
        self._in_port = in_port
        self._timeout = timeout
        self._server = None

        self.name = name or repr(self)

    def __repr__(self):
        return f"IP: {self._ip_address}, RX: {self._in_port}, TX: {self._out_port}."

    @contextmanager
    def connect(self):
        """Context manger for run UDP server."""
        self._server = ThreadedUDPServer(
            (self._ip_address, self._in_port),
            (self._ip_address, self._out_port),
            ThreadedUDPRequestHandler,
        )
        with self._server:  # pylint: disable=duplicate-code
            try:
                yield self
            finally:
                pass

    def make_connection(self):
        """Run UDP server in non context."""
        self._server = ThreadedUDPServer(
            (self._ip_address, self._in_port),
            (self._ip_address, self._out_port),
            ThreadedUDPRequestHandler,
        )
        self._server.start()

    # pylint: disable=duplicate-code
    def flush(self):
        """Flush incoming buffer."""
        while True:
            try:
                self._server.incoming_buffer.get_nowait()
            except Empty:
                break
            else:
                self._server.incoming_buffer.task_done()
                self.rx_count += 1

    def receive(self) -> List[bytes]:
        """Read incoming buffer."""
        if self._server is None:
            raise RuntimeError(
                "Before call `receive()` method connection must be establish. Use `connect()` "
                "as contextmanager to receive data."
            )
        while True:
            try:
                yield self._server.incoming_buffer.get(timeout=0.005)
            except Empty:
                break
            else:
                self._server.incoming_buffer.task_done()
                self.rx_count += 1

    def send(self, data: bytes) -> None:
        """Send data."""
        if self._server is None:
            raise RuntimeError(
                "Before call `send()` method connection must be establish. Use `connect()` "
                "as contextmanager to send data."
            )
        self._server.write(data)
        self.tx_count += 1
