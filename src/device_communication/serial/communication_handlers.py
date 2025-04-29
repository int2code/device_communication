"""Serial communication handlers."""

import logging
from contextlib import contextmanager
from queue import Empty
from typing import List, Optional

from serial import serial_for_url

from device_communication.base.communication_handlers import BaseCommunicationHandler
from device_communication.base.datatypes import ByteArrayWithTimestamp
from device_communication.serial.packetizer import SerialProtocol
from device_communication.serial.servers import ThreadedSerialServer

logger = logging.getLogger(__name__)


class SerialCommunicationHandler(BaseCommunicationHandler):
    """Layer between ApiClient and Server.

    Class that maintains the Serial Read/Write thread running. Connects API client (that
    implements client's methods) to server instance for writing and reading binary data
    over Serial port.

    """

    SERIAL_PROTOCOL_CLS = SerialProtocol

    def __init__(
        self, port_name: str, com_baud: int, timeout=5, name: Optional[str] = None
    ):
        super().__init__()
        self._server = None
        self._timeout = timeout
        self._port_name = port_name
        self._com_baud = com_baud

        self._name = name or repr(self)

    @property
    def name(self):
        """Name of communication handler."""
        return self._name

    @property
    def port_name(self):
        """Name of communication port."""
        return self._port_name

    def __repr__(self):
        return f"PORT: {self._port_name} ({self._com_baud})."

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

    def receive(self) -> List[ByteArrayWithTimestamp]:
        """Read incoming buffer."""
        if self._server is None:
            raise RuntimeError(
                "Before call `receive()` method connection must be establish. Use `connect()` "
                "as contextmanager to receive data."
            )
        while True:
            try:
                yield self._server.incoming_buffer.get_nowait()
            except Empty:
                break
            else:
                self._server.incoming_buffer.task_done()
                self.rx_count += 1

    def send(self, data: bytes) -> None:
        """Read incoming buffer."""
        if self._server is None:
            raise RuntimeError(
                "Before call `send()` method connection must be establish. Use `connect()` "
                "as contextmanager to send data."
            )
        self._server.protocol.send(data)
        self.tx_count += 1

    def _init_server(self):
        """Initialize serial and server thread."""
        serial = serial_for_url(self._port_name, self._com_baud, timeout=self._timeout)
        serial.flush()
        self._server = ThreadedSerialServer(serial, self.SERIAL_PROTOCOL_CLS)

    @contextmanager
    def connect(self):
        """Connect communication port."""
        self._init_server()
        with self._server:
            try:
                yield self
            finally:
                pass

    def make_connection(self):
        """Connect communication port in non context."""
        self._init_server()
        self._server.start()
        self._server.connect()
