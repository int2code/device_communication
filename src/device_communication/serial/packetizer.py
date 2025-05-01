"""Serial COM packetizers."""

import logging

from serial.threaded import Protocol

from device_communication.base.packetizer import BaseFrameParser

logger = logging.getLogger(__name__)


class SerialProtocol(Protocol):
    """Serial protocol parser dedicated to serial ReaderThread."""

    FRAME_PARSER_CLS: BaseFrameParser = BaseFrameParser

    def __init__(self):
        self.transport = None
        self._received_buffer = bytearray()
        self._out_of_packet_data = bytearray()

    def connection_made(self, transport):
        """Store threaded transport instance."""
        self.transport = transport

    def connection_lost(self, exc):
        """Forget threaded transport instance."""
        self.transport = None
        super().connection_lost(exc)

    def data_received(self, data):
        """Parse incoming packages form incoming data."""
        self._received_buffer.extend(data)
        parsed_frames, self._received_buffer, dropped = (
            self.FRAME_PARSER_CLS.parse_frames(self._received_buffer)
        )
        for frame in parsed_frames:
            self.handle_packet(frame)

        if dropped:
            self._out_of_packet_data.extend(dropped)
            self.handle_out_of_packet_data(dropped)

    def handle_packet(self, packet):
        """Process packets."""
        self.transport.incoming_buffer.put_nowait(packet)

    def handle_out_of_packet_data(self, data):
        """Process data that is received outside of packets."""
        logger.debug("Cannot parse received data: %s", data.hex(" "))

    def send(self, data):
        """Send data."""
        self.transport.write(data)
