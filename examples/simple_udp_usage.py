"""Example usage of UDP communication handler and simulator."""

import logging
import time
from typing import List, Tuple

from plum.structure import Structure

from device_communication.base.packetizer import BaseFrameParser
from device_communication.base.packets import ExamplePacket
from device_communication.base.simulator import BaseSimulator
from device_communication.udp.communication_handlers import (
    UdpCommunicationHandler as BaseUdpCommunicationHandler,
)
from device_communication.udp.packetizer import (
    ThreadedUDPRequestHandler as BaseThreadedUDPRequestHandler,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


### communication handler part


class FrameParser(BaseFrameParser):
    """Frame parser for UDP communication."""

    @classmethod
    def parse_frames(
        cls, buffer: bytearray
    ) -> Tuple[List[bytearray], bytearray, bytearray]:
        # This is a placeholder implementation. Replace with actual parsing logic.
        return [buffer], bytearray(), bytearray()

    @classmethod
    def build_frame(cls, data: bytearray) -> bytearray:
        raise NotImplementedError()


class ThreadedUDPRequestHandler(BaseThreadedUDPRequestHandler):
    """Threaded UDP request handler."""

    FRAME_PARSER_CLS = FrameParser


class UdpCommunicationHandler(BaseUdpCommunicationHandler):
    """UDP communication handler."""

    THREADED_REQUEST_HANDLER_CLS = ThreadedUDPRequestHandler


### simulator part


class UdpSimulator(BaseSimulator):
    """UDP simulator."""

    STRUCTURE_CLS: type(Structure) = (
        ExamplePacket  # Replace with your actual packet class
    )


#### example usage

communication_handler = UdpCommunicationHandler(
    ip_address="127.0.0.1",
    in_port=54321,
    out_port=12345,
)
simulator = UdpSimulator(communication_handler)

with simulator.connect():
    msg = ExamplePacket.unpack(b"Hello")  # build plum message to be sent
    simulator.send(msg)

    time.sleep(1)
    pkts = simulator.receive()
    for pkt in pkts:
        pkt.dump()
