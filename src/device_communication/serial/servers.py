"""Serial servers implementation to communicate over Serial"""

from queue import Queue

from serial.threaded import ReaderThread


class ThreadedSerialServer(ReaderThread):
    """Serial server for reading and writing data over Serial port.

    Uses `serial.Serial` and `serial.threaded.Protocol` instances to pack/unpack
    outgoing and incoming messages.

    """

    def __init__(self, serial_instance, protocol_factory, name=""):
        super().__init__(serial_instance, protocol_factory)
        self.incoming_buffer = Queue()
        self.name = f"{name} [{serial_instance.name}]" if name else serial_instance.name
