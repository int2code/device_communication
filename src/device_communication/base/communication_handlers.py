"""Base class that takes care of the communication between ApiClient and class or thread
responsible for reading and writing from and to communication medium (this could be
Serial COM, UDPServer or even urllib PoolManager).
"""

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import List


class BaseCommunicationHandler(ABC):
    """Communication handler expected API"""

    def __init__(self):
        self.rx_count = 0
        self.tx_count = 0

    def reset_counters(self):
        """Reset RX and TX counter."""
        self.rx_count = 0
        self.tx_count = 0

    @abstractmethod
    def receive(self) -> List[bytes]:
        """Read incoming buffer."""

    @abstractmethod
    def send(self, data) -> None:
        """Write outgoing data."""

    @abstractmethod
    def flush(self):
        """Flush incoming buffer."""

    @abstractmethod
    @contextmanager
    def connect(self):
        """Open connection in context manager."""

    @abstractmethod
    def make_connection(self):
        """Open connection in non context - alternative to `connect()`."""
