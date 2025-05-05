"""Provides packet structures for device communication."""

from plum.items import ItemsX
from plum.structure import member

from device_communication.base.datatypes import PlumStructure


class ExamplePacket(PlumStructure):
    """Structure describing general packet."""

    payload: int = member(fmt=ItemsX(name="varies"))
