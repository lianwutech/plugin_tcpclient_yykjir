#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
插件管理类
内部包含3个对象：通道管理对象、MQTT管理对象、协议管理对象
内部基于device_id进行协调
通道管理对象实现指令发送
MQTT管理对象实现数据发送
协议管理对象实现消息的编解码
每个管理对象内部有一个device_id和内部对象id的映射表和基于内部对象id的内部对象字典
插件管理类管理整个设备信息
"""

from channel_manager import *
from mqtt_manager import *
from protocol_manager import *


class PluginManager(object):
    def __init__(self):
        self.channel_manager = None
        self.protocol_manager = None
        self.mqtt_manager = None
        self.devices_dict = dict()

    def load(self, params):
        """
        加载参数
        :param params:
        :return:
        """
        # 启动顺序，协议管理对象、Mqtt管理对象、通道管理对象
        self.protocol_manager = ProtocolManger(self)
        self.protocol_manager.load(params)
        self.mqtt_manager = MQTTManager(self)
        self.mqtt_manager.load(params)
        self.channel_manager = ChannelManager(self)
        self.channel_manager.load(params)
        # 增加设备信息
        pass

    def add_device(self, network, channel, protocol, device_info):
        device_info["channel"] = channel
        if "protocol" not in device_info:
            device_info["protocol"] = protocol
        device_id = "%s/%s/%s" % (network,
                                  device_info.get("device_addr", ""),
                                  device_info.get("device_port"))
        self.devices_dict[device_id] = device_info
        # 将设备信息插入到Mqtt管理对象
        self.mqtt_manager.add_device(device_id, device_info)
        # 将设备信息插入到通道管理对象
        self.channel_manager.add_device(channel, device_id)

    def send_cmd(self, device_id, cmd):
        return self.channel_manager.send_cmd(device_id, cmd)

    def send_data(self, device_id, data):
        return self.mqtt_manager.send_data(device_id, data)

    def process_data(self, device_id, msg):
        return self.protocol_manager.process_data(device_id, msg)

    def process_cmd(self, device_id, msg):
        return self.protocol_manager.process_cmd(device_id, msg)

    def process_data_by_protocol(self, channel, protocol, msg):
        # 获取设备信息
        #
        return self.protocol_manager.process_data_by_protocol(protocol, msg)

    def check_channel_status(self):
        return self.channel_manager.check_status()

    def check_mqtt_client_status(self):
        return self.mqtt_manager.check_status()

