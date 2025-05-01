"""Additional/extended datatypes"""


class ByteArrayWithTimestamp(bytearray):
    """Bytearray with additional timestamp filed."""

    def __init__(self, *args, **kwargs):
        self.timestamp = kwargs.pop("timestamp", None)
        super().__init__(*args, **kwargs)
