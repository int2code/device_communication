"""TCP packetizers."""

import socketserver

from device_communication.base.packetizer import BaseFrameParser


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """Threaded TCP RequestHandler."""

    FRAME_PARSER_CLS: BaseFrameParser = BaseFrameParser

    def __init__(self, request, client_address, server):
        self._received_buffer = bytearray()
        super().__init__(request, client_address, server)

    def handle(self):
        data, _ = self.request
        self._received_buffer.extend(data)
        parsed_frames, self._received_buffer, _ = self.FRAME_PARSER_CLS.parse_frames(
            self._received_buffer
        )

        for frame in parsed_frames:
            self.server.incoming_buffer.put_nowait(frame)
