#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
通道管理类
内部有一个device_id和内部对象id的映射表和基于内部对象id的内部对象字典
支持的通道类型有Serial、HttpServer、TcpServer、UdpServer、HttpClient、TcpClient、UdpClient
"""
import sys

from channel import *


class ChannelManager(object):
    def __init__(self, plugin_manager):
        self.mapper_dict = dict()
        self.channel_dict = dict()
        self.plugin_manager = plugin_manager

    def load(self, channel_params):
        # 加载参数
        for device_network in channel_params:
            network_name = device_network.get("network_name", "")
            protocol = device_network.get("protocol", "")
            channels = device_network.get("channels", [])
            for channel in channels:
                channel_name = channel.get("name", "")
                channel_type = channel.get("channel_type", "")
                channel_params = channel.get("params", "{}")
                preconfigured_devices = channel.get("preconfigured_devices", [])

                if channel_type == const.SerialChannelType:
                    self.channel_dict[channel_name] = SerialChannel(network_name,
                                                                    channel_name,
                                                                    protocol,
                                                                    channel_params,
                                                                    self)
                elif channel_type == const.HttpServerChannelType:
                    self.channel_dict[channel_name] = HttpServerChannel(network_name,
                                                                        channel_name,
                                                                        protocol,
                                                                        channel_params,
                                                                        self)
                elif channel_type == const.TcpServerChannelType:
                    self.channel_dict[channel_name] = TcpServerChannel(network_name,
                                                                       channel_name,
                                                                       protocol,
                                                                       channel_params,
                                                                       self)
                elif channel_type == const.UdpServerChannelType:
                    self.channel_dict[channel_name] = UdpServerChannel(network_name,
                                                                       channel_name,
                                                                       protocol,
                                                                       channel_params,
                                                                       self)
                elif channel_type == const.HttpClientChannelType:
                    self.channel_dict[channel_name] = HttpClientChannel(network_name,
                                                                        channel_name,
                                                                        protocol,
                                                                        channel_params,
                                                                        self)
                elif channel_type == const.TcpClientChannelType:
                    self.channel_dict[channel_name] = TcpClientChannel(network_name,
                                                                       channel_name,
                                                                       protocol,
                                                                       channel_params,
                                                                       self)
                elif channel_type == const.UdpClientChannelType:
                    self.channel_dict[channel_name] = UdpClientChannel(network_name,
                                                                       channel_name,
                                                                       protocol,
                                                                       channel_params,
                                                                       self)

                # 线程启动
                try:
                    self.channel_dict[channel_name].run()
                except Exception, e:
                    logger.error("channel(%s) run fail. error info: %r" % (channel_name, e))

                for device_info in preconfigured_devices:
                    device_id = "%s/%s/%s" % (network_name,
                                              device_info.get("device_addr", ""),
                                              device_info.get("device_port"))
                    self.mapper_dict[device_id] = channel_name

        for channel_name in self.channel_dict:
            if not self.channel_dict[channel_name].isAlive():
                logger.fatal("channel(%s) is not run. please check。" % channel_name)
                sys.exit(1)

    def add_device(self, channel_name, device_id):
        if device_id in self.mapper_dict:
            if channel_name in self.channel_dict:
                self.mapper_dict[device_id] = channel_name
                return True
            else:
                logger.error("channel(%s) is not exist." % channel_name)
                return False
        else:
            logger.info("device(%s) is exist." % device_id)
            return False

    def process_data(self, network, channel, protocol, msg):
        """
        所有通道共用的数据处理通道
        :param channel:
        :param protocol:
        :param msg:
        :return:
        """
        device_info, devcice_data = self.plugin_manager.protocol_manager.process_data_by_protocol(protocol, msg)
        # 判断设备是否存在，没有则新增设备
        device_id = "%s/%s/%s" % (network,
                                  device_info.get("device_addr", ""),
                                  device_info.get("device_port"))
        if device_id not in self.mapper_dict:
            self.plugin_manager.add_device(network, channel, protocol, device_info)
        # 发送数据
        self.plugin_manager.send_data(device_id, devcice_data)

    def send_cmd(self, device_id, cmd):
        if device_id in self.mapper_dict:
            channel_name = self.mapper_dict[device_id]
            if channel_name in self.channel_dict:
                channel = self.channel_dict.get(channel_name, None)
                if not channel.isAlive():
                    logger.error("channel(%s) is not alive, restart." % channel_name)
                    channel.run()
                # 消息发送
                return channel.send_cmd(cmd)
            else:
                logger.error("channel(%s) is not exist." % channel_name)
                return False
        else:
            logger.error("device(%s) is not exist." % device_id)
            return False

    def check_status(self):
        """
        检查通道运行状态
        :return:
        """
        status_dict = dict()
        for channel_name in self.channel_dict:
            if self.channel_dict[channel_name].isALive():
                status_dict[channel_name] = "run"
            else:
                status_dict[channel_name] = "stop"
                logger.error("channel(%s) is not alive, restart." % channel_name)
                self.channel_dict[channel_name].run()
        return status_dict
