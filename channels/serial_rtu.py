#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
串口RTU通道类
通过调用管理类对象的process_data函数实现信息的发送。
"""

import logging

import serial
from libs.base_channel import BaseChannel


logger = logging.getLogger('yykj_serial')


class SerialRtuChannel(BaseChannel):
    def __init__(self, network, name, protocol, params, manager):
        BaseChannel.__init__(network, name, protocol, params, manager)
        self.port = params.get("port", "")
        self.stopbits = params.get("stopbits", serial.STOPBITS_ON)
        self.parity = params.get("parity", serial.PARITY_NONE)
        self.bytesize = params.get("bytesize", serial.EIGHTBITS)
        self.baudrate = params.get("baudrate", 9600)
        self.timeout = params.get("timeout", 1)

    def run(self):
        pass

    def send_cmd(self, data):
        pass
