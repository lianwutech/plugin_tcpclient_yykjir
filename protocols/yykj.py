#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
YYkj协议类
"""

import logging

from libs.base_protocol import BaseProtocol


logger = logging.getLogger('yykj_serial')


class YykjProtocol(BaseProtocol):
    def process_data(self, data_msg):
        """
        返回device_data
        :param data_msg:
        :return:
        """
        result = True
        device_info = None
        device_data = None
        if "device_info" in data_msg:
            device_info = data_msg["device_info"]

        if device_info is not None:
            if "device_data" in data_msg:
                device_data = data_msg["device_data"]
            if device_data is not None:
                if device_info["device_type"] == "easy_run.infrared":
                    if "01:Begin" in device_data:
                        device_data = ""
                    elif "01:StudyOK" in device_data:
                        device_data = "01:StudyOK"
                    elif "01:StudyER" in device_data:
                        device_data = "01:StudyER"
                    elif "01:Send_OK" in device_data:
                        device_data = "01:Send_OK"
                    elif "01:Send_ER" in device_data:
                        device_data = "01:Send_ER"
                    else:
                        logger.error("Unknown infrared message(%s). " % device_data)
                        result = False
                else:
                    logger.error("Unknown device type(%s)" % device_info["device_type"])
                    result = False

        return result, device_info, device_data

    def process_cmd(self, device_cmd):
        """
        返回cmd_msg
        :param device_cmd:
        :return:
        """
        device_cmd = device_cmd.strip()
        if len(device_cmd) != 6 or ('S' not in device_cmd and 'F' not in device_cmd):
            device_cmd = None
        return device_cmd

