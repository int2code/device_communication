"""UDP communication handlers."""

import socket
from contextlib import contextmanager
from queue import Empty
from typing import Optional, Any, Generator

from device_communication.base.communication_handlers import BaseCommunicationHandler
from device_communication.tcp.packetizer import ThreadedTCPRequestHandler
from device_communication.tcp.servers import ThreadedTcpClient


class TcpClientCommunicationHandler(BaseCommunicationHandler):
    """
    Initialize the TCP Client Communication Handler.

    :param server_address: IP address of the TCP server.
    :param server_port: Port for receiving data from the server.
    :param client_address: Optional IP address for the client.
    :param client_port: Optional port for the client.
    :param timeout: Timeout for server operations in seconds.
    :param name: Optional name for the handler instance.

    """

    # pylint: disable=too-many-arguments, too-many-instance-attributes, too-many-positional-arguments

    THREADED_REQUEST_HANDLER_CLS: type(ThreadedTCPRequestHandler) = (
        ThreadedTCPRequestHandler
    )
    THREADED_CLIENT_CLS: type(ThreadedTcpClient) = ThreadedTcpClient

    def __init__(
        self,
        server_address,
        server_port: int,
        client_address: Optional[str] = None,
        client_port: Optional[int] = None,
        timeout: int = 5,
        name: Optional[str] = None,
    ):
        super().__init__()
        self._ip_address = server_address
        self._server_port = server_port
        self._client_address = client_address
        self._client_port = client_port
        self._timeout = timeout
        self._server = None

        self.name = name or repr(self)

    def __repr__(self):
        return f"IP: {self._ip_address}, RX: {self._client_port}, TX: {self._server_port}."

    def _create_server(self):
        return self.THREADED_CLIENT_CLS(
            (self._ip_address, self._server_port),
            self.THREADED_REQUEST_HANDLER_CLS,
            (self._client_address, self._client_port),
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
