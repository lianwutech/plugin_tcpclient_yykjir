#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
协议管理类
内部有一个device_id和内部对象id的映射表和基于内部对象id的内部对象字典
"""

import os
import sys
import logging

from utils import cur_file_dir, words_capitalize


logger = logging.getLogger("")


class ProtocolManger(object):
    def __init__(self, plugin_manager):
        self.mapper_dict = dict()
        self.protocol_dict = dict()
        self.plugin_manager = plugin_manager

    def load(self, protocol_params):
        # 通过扫描目录来获取支持的协议库
        cur_dir = cur_file_dir()
        if cur_dir is not None:
            protocol_lib_path = cur_dir + "/protocols"
            file_list = os.listdir(protocol_lib_path)
            for file_name in file_list:
                file_path = os.path.join(protocol_lib_path, file_name)
                if os.path.isfile(file_path) and ".py" in file_name:
                    protocol_name, ext = os.path.splitext(file_name)
                    # 确保协议名称为小写
                    protocol_name = protocol_name.lower()
                    # 加载库
                    module_name = "protocol." + protocol_name
                    module = __import__(module_name)
                    class_name = words_capitalize(protocol_name) + "Protocol"
                    class_object = getattr(module, class_name)
                    self.protocol_dict[protocol_name] = class_object()

        # 根据配置生成具体对象
        for device_network in protocol_params:
            network_name = device_network.get("network_name", "")
            protocol_type = device_network.get("protocol_type", "").lower()
            # 确保协议类型字段存在
            if len(protocol_type) > 0:
                # 协议库存在则创建对应映射记录
                preconfigured_device_list = device_network.get("preconfigured_devices", [])
                for device_info in preconfigured_device_list:
                    device_protocol_type = device_info.get("protocol_type", protocol_type)
                    device_id = "%s/%s/%s" % (network_name,
                                              device_info.get("device_addr", ""),
                                              device_info.get("device_port"))
                    if device_protocol_type in self.protocol_dict:
                        self.mapper_dict[device_id] = device_protocol_type
                    else:
                        # 有协议库不存在，系统退出
                        logger.error("protocol(%s) lib don't exit." % device_protocol_type)
                        sys.exit(1)
            else:
                logger.error("params error. protocol_type is null.")

    def add_device(self, protocol_type, device_id):
        if protocol_type in self.protocol_dict:
            self.mapper_dict[device_id] = protocol_type

    def process_data(self, device_id, msg):
        """
        根据device_id进行数据处理，生成数据
        :param device_id:
        :param msg:
        :return:
        """
        if device_id in self.mapper_dict:
            protocol_type = self.mapper_dict[device_id]
            return self.protocol_dict[protocol_type].process_data(msg)
        else:
            logger.info("device_id(%s) is not exist")
            return None, None

    def process_cmd(self, device_id, msg):
        """
        根据device_id进行命令处理，生成要发送的命令字
        :param device_id:
        :param msg:
        :return:
        """
        if device_id in self.mapper_dict:
            protocol_type = self.mapper_dict[device_id]
            return self.protocol_dict[protocol_type].process_cmd(msg)
        else:
            logger.info("device_id(%s) is not exist" % device_id)
            return False

    def process_data_by_protocol(self, protocol, msg):
        """
        根据协议类型来进行消息处理，返回设备信息和数据。
        :param protocol_type:
        :param msg:
        :return:
        """
        if protocol in self.protocol_dict:
            return self.protocol_dict[protocol].process_data(msg)
        else:
            logger.info("protocol_type(%s) is not exist" % protocol)
            return None, None
