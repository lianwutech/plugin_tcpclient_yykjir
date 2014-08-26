#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
通道管理类
内部有一个device_id和内部对象id的映射表和基于内部对象id的内部对象字典
支持的通道类型有Serial、HttpServer、TcpServer、UdpServer、HttpClient、TcpClient、UdpClient
"""

import os
import sys

from libs.base_channel import *
from libs.utils import cur_file_dir, words_capitalize


class ChannelManager(object):
    def __init__(self, plugin_manager):
        self.mapper_dict = dict()
        self.channel_class_dict = dict()
        self.channel_dict = dict()
        self.device_dict = dict()
        self.plugin_manager = plugin_manager

    def load(self, channel_params):
        # 扫描通道库
        # 通过扫描目录来获取支持的协议库
        cur_dir = cur_file_dir()
        if cur_dir is not None:
            channel_lib_path = cur_dir + "/channels"
            file_list = os.listdir(channel_lib_path)
            for file_name in file_list:
                file_path = os.path.join(channel_lib_path, file_name)
                if os.path.isfile(file_path) and ".py" in file_name:
                    channel_name, ext = os.path.splitext(file_name)
                    # 确保协议名称为小写
                    channel_name = channel_name.lower()
                    # 加载库
                    module_name = "channels." + channel_name
                    module = __import__(module_name)
                    class_name = words_capitalize(channel_name) + "Channel"
                    class_object = getattr(module, class_name)
                    self.channel_class_dict[channel_name] = class_object
        # 加载参数
        for device_network in channel_params:
            network_name = device_network.get("network_name", "")
            protocol = device_network.get("protocol", "")
            channels = device_network.get("channels", [])
            for channel in channels:
                channel_name = channel.get("name", "")
                channel_type = channel.get("type", "")
                channel_params = channel.get("params", "{}")
                preconfigured_devices = channel.get("preconfigured_devices", [])

                # 创建通道对象
                if channel_type in self.channel_class_dict:
                    channel_class_object = self.channel_class_dict[channel_type]
                    self.channel_dict[channel_name] = channel_class_object(network_name,
                                                                           channel_name,
                                                                           protocol,
                                                                           channel_params,
                                                                           self)
                else:
                    logger.error("channel type(%s) is not exist. Please check!")
                    sys.exit(1)

                # 通道启动
                try:
                    self.channel_dict[channel_name].run()
                except Exception, e:
                    logger.error("channel(%s) run fail. error info: %r" % (channel_name, e))

                # 通道与设备的映射管理建立
                for device_info in preconfigured_devices:
                    device_id = "%s/%s/%s" % (network_name,
                                              device_info.get("device_addr", ""),
                                              device_info.get("device_port"))
                    self.mapper_dict[device_id] = channel_name

        # 检查通道启动情况，如果有通道退出，则系统退出。
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

    def process_data(self, network, channel, protocol, data_msg):
        """
        所有通道共用的数据处理通道
        :param channel:
        :param protocol:
        :param msg:
        :return:
        """
        device_info, device_data = self.plugin_manager.process_data_by_protocol(protocol, data_msg)
        # 判断设备是否存在，没有则新增设备
        device_id = "%s/%s/%s" % (network,
                                  device_info.get("device_addr", ""),
                                  device_info.get("device_port"))
        if device_id not in self.mapper_dict:
            self.plugin_manager.add_device(network, channel, protocol, device_info)
        # 发送数据
        self.plugin_manager.send_data(device_id, device_data)

    def send_cmd(self, device_id, device_cmd):
        if device_id in self.mapper_dict:
            channel_name = self.mapper_dict[device_id]
            device_info = self.device_dict[device_id]
            if channel_name in self.channel_dict:
                channel = self.channel_dict.get(channel_name, None)
                if not channel.isAlive():
                    logger.error("channel(%s) is not alive, restart." % channel_name)
                    channel.run()
                # 消息发送
                return channel.send_cmd(device_info, device_cmd)
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
