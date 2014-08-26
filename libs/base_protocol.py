#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
基础协议类
"""


class BaseProtocol(object):
    def process_data(self, msg):
        return {}, {}

    def process_cmd(self, msg):
        return ""

