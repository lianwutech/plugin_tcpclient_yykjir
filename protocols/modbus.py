#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
modbus协议类
"""

import logging

from libs.base_protocol import BaseProtocol


logger = logging.getLogger('yykj_serial')


class ModbusProtocol(BaseProtocol):
    def process_data(self, data_msg):
        """
        返回device_data
        :param data_msg:
        :return:
        """
        if "device_info" in data_msg:
            device_info = data_msg["device_info"]
        else:
            device_info = None

        if "device_data" in data_msg:
            device_data = data_msg["device_data"]
        else:
            device_data = None

        return device_info, device_data

    def process_cmd(self, device_cmd):
        """
        返回cmd_msg
        :param device_cmd:
        :return:
        """
        return device_cmd

