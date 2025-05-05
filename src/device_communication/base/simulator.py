"""Base Simulator."""

import logging
import time
from contextlib import contextmanager
from enum import IntEnum
from typing import List, Optional, Union

from plum.exceptions import UnpackError

from device_communication.base.communication_handlers import BaseCommunicationHandler

from device_communication.base.datatypes import PlumStructure
from device_communication.base.packets import ExamplePacket

logger = logging.getLogger(__name__)


class BaseSimulator:
    """Class for sending and receiving packages.

    :param communication_handler:
        instance of communication handler (COM or other for future)

    example of use:

    """

    STRUCTURE_CLS: type(PlumStructure) = ExamplePacket

    def __init__(
        self,
        communication_handler: type(BaseCommunicationHandler),
        name: Optional[str] = None,
    ) -> None:
        self._comm_handler = communication_handler
        self._msg_counter = 1

        self.logger = logger
        self.name = name or str(self._comm_handler)
        self.connected = False

    @property
    def rx_count(self) -> int:
        """Counter of received messages.

        NOTE: messages are only counted when `received()` method is called.

        """
        return self._comm_handler.rx_count

    @property
    def tx_count(self):
        """Counter of transited messages."""
        return self._comm_handler.tx_count

    def reset_counters(self):
        """Reset RX and TX counter."""
        self._comm_handler.reset_counters()

    def send(
        self,
        packet: PlumStructure,
    ):
        """Send given SEP message via given communication handler.

        :param packet: initialized PlumStructure object

        """
        raw_data = packet.ipack()
        self.logger.info("Sending following packet:\n%s", packet.dump)

        self._comm_handler.send(data=raw_data)

    def flush(self):
        """Flush incoming buffer."""
        self._comm_handler.flush()

    @contextmanager
    def connect(self):
        """Context manager for connecting handler to target."""
        with self._comm_handler.connect():
            self.connected = True
            try:
                yield
            finally:
                self.connected = False

    def receive(
        self,
        wait_for_pkt: Optional[Union[str, List[str], IntEnum, List[IntEnum]]] = None,
        timeout: float = 10.0,
    ) -> List[PlumStructure]:
        """Receive incoming packets via given communication handler.

        :param wait_for_pkt:
            name of packet that method will be waited. If not given first incoming frame
            will be returned

        :param timeout: time how log method is waiting when `wait_for_msg` param is given

        """
        if wait_for_pkt is not None:
            receive_func, args = self._receive_with_wait, [timeout]
        else:
            receive_func, args = self._receive, []

        pkts = list(receive_func(*args))

        for pkt in pkts:
            self.logger.info("Received following packets\n%s", pkt.dump)

        return pkts

    def _receive(self):
        raw_frames = self._comm_handler.receive()
        for pkt in raw_frames:
            msg = self.STRUCTURE_CLS.unpack(pkt)

            yield msg

    def _receive_with_wait(
        self,
        timeout: float,
        ignore_unpack_error=True,
    ):
        start_time = time.time()
        self.logger.debug("Waiting for packet: %ss", timeout)

        expected_pkts = []
        while start_time + timeout > time.time():
            try:
                pkts = self._receive()
            except TimeoutError:
                time.sleep(
                    0.05
                )  # idle - allow other processes time to perform their tasks
                continue
            except UnpackError:
                if ignore_unpack_error:
                    continue
                raise

            for pkt in pkts:
                expected_pkts.append(pkt)

            if expected_pkts:
                return expected_pkts

        raise TimeoutError(f"message not received within {timeout}s.")
