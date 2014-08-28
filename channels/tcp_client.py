#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
TCP-Client通道类
通过调用管理类对象的process_data函数实现信息的发送。
"""
import logging

from libs.base_channel import BaseChannel


logger = logging.getLogger('yykj_serial')


class TcpClientChannel(BaseChannel):
    def __init__(self, network, channel_name, channel_protocol, channel_params, manager, channel_type):
        self.status = None
        BaseChannel.__init__(network, channel_name, channel_protocol, channel_params, manager, channel_type)

    def run(self):
        logger.debug("TcpClientChannel has runned.")
        return

    def isAlive(self):
        return True

    def send_cmd(self, device_info, device_cmd):
        pass