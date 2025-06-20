"""UDP communication handlers."""

from contextlib import contextmanager
from queue import Empty
from typing import Optional, Any, Generator

from device_communication.base.communication_handlers import BaseCommunicationHandler
from device_communication.udp.packetizer import ThreadedUDPRequestHandler
from device_communication.udp.servers import ThreadedUDPServer


class UdpCommunicationHandler(BaseCommunicationHandler):
    """
    Layer between user/client and Server

    Maintains UDP Server running while providing methods for reading and writing from and to the tar

    Class that maintains the UDP Server thread running. Connects user/client to server
    instance for writing and reading binary data.

    :param ip_address: IP address of the UDP server.
    :param in_port: Port for receiving data.
    :param out_port: Port for sending data.
    :param timeout: Timeout for server operations.
    :param name: Optional name for the handler instance.
    :param bind_and_activate: Whether to bind and activate the server immediately.

    """

    # pylint: disable=too-many-arguments, too-many-instance-attributes, too-many-positional-arguments

    THREADED_REQUEST_HANDLER_CLS: type(ThreadedUDPRequestHandler) = (
        ThreadedUDPRequestHandler
    )

    def __init__(
        self,
        ip_address,
        in_port: int,
        out_port: int,
        timeout: int = 5,
        name: Optional[str] = None,
        bind_and_activate: bool = True,
    ):
        super().__init__()
        self._ip_address = ip_address
        self._out_port = out_port
        self._in_port = in_port
        self._timeout = timeout
        self._server = None

        self.name = name or repr(self)
        self._bind_and_activate = bind_and_activate

    def __repr__(self):
        return f"IP: {self._ip_address}, RX: {self._in_port}, TX: {self._out_port}."

    def _create_server(self):
        return ThreadedUDPServer(
            (self._ip_address, self._in_port),
            (self._ip_address, self._out_port),
            self.THREADED_REQUEST_HANDLER_CLS,
            bind_and_activate=self._bind_and_activate
        )

    @contextmanager
    def connect(self):
        """
        Context manager for running the UDP server.

        :yield: Instance of `UdpCommunicationHandler`.
        """
        self._server = self._create_server()
        with self._server:  # pylint: disable=duplicate-code
            try:
                yield self
            finally:
                pass

    def make_connection(self):
        """
        Run the UDP server outside of a context manager.
        """
        self._server = self._create_server()
        self._server.start()

    # pylint: disable=duplicate-code
    def flush(self):
        """
        Flush the incoming buffer by clearing all pending messages.
        """
        while True:
            try:
                self._server.incoming_buffer.get_nowait()
            except Empty:
                break
            else:
                self._server.incoming_buffer.task_done()
                self.rx_count += 1

    def receive(self) -> Generator[Any, Any, None]:
        """
        Read data from the incoming buffer.

        :raises RuntimeError: If the server is not running.
        :yield: Data from the incoming buffer.
        """
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
        """
        Send data to the server.

        :param data: Binary data to send.
        :raises RuntimeError: If the server is not running.
        """
        if self._server is None:
            raise RuntimeError(
                "Before call `send()` method connection must be establish. Use `connect()` "
                "as contextmanager to send data."
            )
        self._server.write(data)
        self.tx_count += 1
