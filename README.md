# device-communication

[![Documentation Status](https://readthedocs.org/projects/device-communication/badge/?version=latest)](https://device-communication.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/device-communication.svg)](https://pypi.org/project/device-communication/)
[![License](https://img.shields.io/pypi/l/device-communication.svg)](https://pypi.org/project/device-communication/)
[![Python Version](https://img.shields.io/pypi/pyversions/device-communication.svg)](https://pypi.org/project/device-communication/)
[![Build Status](https://travis-ci.com/roboticslab-uc3m/device-communication.svg?branch=master)](https://travis-ci.com/roboticslab-uc3m/device-communication)

This package provides base classes, API definitions and implementations to handle 
communication to devices over different types mediums and protocols (Serial, UDP, ...). 
`device-communication` does not provide specific implementations but rather general 
purpose solutions. The implementation of specific API, messages definitions, packetizer 
and other required objects should be moved to separate repositories related to specific 
device only.



