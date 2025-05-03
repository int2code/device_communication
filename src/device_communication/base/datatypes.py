"""Additional/extended datatypes"""

from datetime import datetime

from plum.structure import Structure


class ByteArrayWithTimestamp(bytearray):
    """Bytearray with additional timestamp filed."""

    def __init__(self, *args, **kwargs):
        self.timestamp = kwargs.pop("timestamp", None)
        super().__init__(*args, **kwargs)


class PlumStructure(Structure):
    """Plum structure with additional timestamp field."""

    __timestamp = None

    @property
    def __timestamp__(self) -> datetime:
        """Metadata to store the time the message was created or received."""
        return self.__timestamp

    @__timestamp__.setter
    def __timestamp__(self, value: datetime):
        """Set metadata to store the time the message was created or received.

        :param value: timestamp

        """
        self.__timestamp = value
