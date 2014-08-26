#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
通道类
通过调用管理类对象的process_data函数实现信息的发送。
"""

import logging
import threading

import const


const.SerialChannelType = "Serial"
const.HttpServerChannelType = "HttpServer"
const.TcpServerChannelType = "TcpServer"
const.UdpServerChannelType = "UdpServer"
const.HttpClientChannelType = "HttpClient"
const.TcpClientChannelType = "TcpClient"
const.UdpClientChannelType = "UdpClient"

logger = logging.getLogger('yykj_serial')


class BaseChannel(threading.Thread):
    """
    基础设备通信类
    针对每种通信模式实现各自的内容
    """

    def __init__(self, network, name, protocol, params, manager):
        self.name = name
        self.protocol = protocol
        self.params = params
        self.network = network
        self.manager = manager
        threading.Thread.__init__(self)

    def run(self):
        pass

    def send_cmd(self, data):
        pass


class SerialChannel(BaseChannel):
    """
    串口通道
    """

    def __init__(self, network, name, protocol, params, manager):
        self.status = None
        BaseChannel.__init__(network, name, protocol, params, manager)

    def run(self):
        pass

    def send_cmd(self, data):
        pass


class HttpServerChannel(BaseChannel):
    """
    HttpServer通道
    """

    def __init__(self, network, name, protocol, params, manager):
        self.status = None
        BaseChannel.__init__(network, name, protocol, params, manager)

    def run(self):
        pass

    def send_cmd(self, data):
        pass


class TcpServerChannel(BaseChannel):
    def __init__(self, network, name, protocol, params, manager):
        self.status = None
        BaseChannel.__init__(network, name, protocol, params, manager)

    def run(self):
        pass

    def send_cmd(self, data):
        pass


class UdpServerChannel(BaseChannel):
    def __init__(self, network, name, protocol, params, manager):
        self.status = None
        BaseChannel.__init__(network, name, protocol, params, manager)

    def run(self):
        pass

    def send_cmd(self, data):
        pass


class HttpClientChannel(BaseChannel):
    def __init__(self, network, name, protocol, params, manager):
        self.status = None
        BaseChannel.__init__(network, name, protocol, params, manager)

    def run(self):
        logger.debug("HttpClientChannel has runned.")
        return

    def isAlive(self):
        return True

    def send_cmd(self, data):
        pass


class TcpClientChannel(BaseChannel):
    def __init__(self, network, name, protocol, params, manager):
        self.status = None
        BaseChannel.__init__(network, name, protocol, params, manager)

    def run(self):
        logger.debug("TcpClientChannel has runned.")
        return

    def isAlive(self):
        return True

    def send_cmd(self, data):
        pass


class UdpClientChannel(BaseChannel):
    def __init__(self, network, name, protocol, params, manager):
        self.status = None
        BaseChannel.__init__(network, name, protocol, params, manager)

    def run(self):
        logger.debug("UdpClientChannel has runned.")
        return

    def isAlive(self):
        return True

    def send_cmd(self, data):
        pass
