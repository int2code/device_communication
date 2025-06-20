"""Example usage of TCP communication handler and simulator."""

import logging
import time
from typing import List, Tuple

from plum.structure import Structure

from device_communication.base.packetizer import BaseFrameParser
from device_communication.base.packets import ExamplePacket
from device_communication.base.simulator import BaseSimulator
from device_communication.tcp.communication_handlers import (
    TcpClientCommunicationHandler as BaseTcpCommunicationHandler,
)
from device_communication.tcp.packetizer import (
    ThreadedTCPRequestHandler as BaseThreadedTCPRequestHandler,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


### communication handler part


class FrameParser(BaseFrameParser):
    """Frame parser for TCP communication."""

    @classmethod
    def parse_frames(
        cls, buffer: bytearray
    ) -> Tuple[List[bytearray], bytearray, bytearray]:
        # This is a placeholder implementation. Replace with actual parsing logic.
        return [buffer], bytearray(), bytearray()

    @classmethod
    def build_frame(cls, data: bytearray) -> bytearray:
        raise NotImplementedError()


class ThreadedTCPRequestHandler(BaseThreadedTCPRequestHandler):
    """Threaded TCP request handler."""

    FRAME_PARSER_CLS = FrameParser


class TcpClientCommunicationHandler(BaseTcpCommunicationHandler):
    """TCP communication handler."""

    THREADED_REQUEST_HANDLER_CLS = ThreadedTCPRequestHandler


### simulator part


class TcpSimulator(BaseSimulator):
    """TCP simulator."""

    STRUCTURE_CLS: type(Structure) = (
        ExamplePacket  # Replace with your actual packet class
    )


#### example usage

communication_handler = TcpClientCommunicationHandler(
    server_address="127.0.0.1",
    server_port=12345,
    client_address="127.0.0.1",
    client_port=54321,
)
simulator = TcpSimulator(communication_handler)

with simulator.connect():
    msg = ExamplePacket.unpack(b"Hello")  # build plum message to be sent
    simulator.send(msg)

    time.sleep(1)
    pkts = simulator.receive()
    for pkt in pkts:
        pkt.dump()
