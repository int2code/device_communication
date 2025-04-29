"""Base framer class that takes care of parsing incoming data buffer and wraps
data to send with CRC, encoding, terminator byte etc.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple


class BaseFrameParser(ABC):
    """FrameParser base class

    Provides methods to parse frames from bytes buffer and to prepare outgoing data
    according to defined protocol (for instance add CRC, terminator, encoding, ...).

    """

    @classmethod
    @abstractmethod
    def build_frame(cls, data: bytearray) -> bytearray:
        """Frame data

        Calculate CRC, encode the data, append terminator etc. before sending the data.

        :param data: buffer to send
        :return: encoded data with CRC, terminator etc.

        """

    @classmethod
    @abstractmethod
    def parse_frames(
        cls, buffer: bytearray
    ) -> Tuple[List[bytearray], bytearray, bytearray]:
        """Parse given buffer to frames

        :param buffer: incoming data stream
        :returns:
            parsed frames found in buffer,
            remaining buffer,
            dropped data (CRC did not match)

        """
