#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
    modbus网络的串口数据采集插件
    1、device_id的组成方式为ip_port_slaveid
    2、设备类型为0，协议类型为modbus
    3、devices_info_dict需要持久化设备信息，启动时加载，变化时写入
    4、device_cmd内容：json字符串
"""

import os
import sys
import time
import json
import serial
import paho.mqtt.client as mqtt
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import threading
import logging
import ConfigParser
try:
    import paho.mqtt.publish as publish
except ImportError:
    # This part is only required to run the example from within the examples
    # directory when the module itself is not installed.
    #
    # If you have the module installed, just use "import paho.mqtt.publish"
    import os
    import inspect
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../src")))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    import paho.mqtt.publish as publish
from json import loads, dumps

from libs.utils import *
from libs.modbusdefine import *

# 设置系统为utf-8  勿删除
reload(sys)
sys.setdefaultencoding('utf-8')

# 全局变量
# 设备信息字典
devices_info_dict = dict()

# 切换工作目录
# 程序运行路径
procedure_path = cur_file_dir()
# 工作目录修改为python脚本所在地址，后续成为守护进程后会被修改为'/'
os.chdir(procedure_path)

# 日志对象
logger = logging.getLogger('yykj_serial')
hdlr = logging.FileHandler('./yykj_serial.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

# 加载配置项
config = ConfigParser.ConfigParser()
config.read("./yykj_serial.cfg")
serial_port = config.get('serial', 'port')
serial_baund = int(config.get('serial', 'baund'))
mqtt_server_ip = config.get('mqtt', 'server')
mqtt_server_port = int(config.get('mqtt', 'port'))
mqtt_client_id = config.get('mqtt', 'client_id')
gateway_topic = config.get('gateway', 'topic')
device_network = config.get('device', 'network')
data_protocol = config.get('device', 'protocol')

# 获取本机ip
ip_addr = get_ip_addr()

# 加载设备信息字典
devices_info_file = "devices.txt"


def load_devices_info_dict():
    if os.path.exists(devices_info_file):
        devices_file = open(devices_info_file, "r+")
        content = devices_file.read()
        devices_file.close()
        try:
            devices_info_dict.update(json.loads(content))
        except Exception, e:
            logger.error("devices.txt内容格式不正确")
    else:
        devices_file = open(devices_info_file, "w+")
        devices_file.write("{}")
        devices_file.close()
    logger.debug("devices_info_dict加载结果%r" % devices_info_dict)


# 新增设备
def check_device(device_id, device_type, device_addr, device_port):
    # 如果设备不存在则设备字典新增设备并写文件
    if device_id not in devices_info_dict:
        # 新增设备到字典中
        devices_info_dict[device_id] = {
            "device_id": device_id,
            "device_type": device_type,
            "device_addr": device_addr,
            "device_port": device_port
        }
        logger.debug("发现新设备%r" % devices_info_dict[device_id])
        #写文件
        devices_file = open(devices_info_file, "w+")
        devices_file.write(dumps(devices_info_dict))
        devices_file.close()


def publish_device_data(device_id, device_type, device_addr, device_port, device_data):
    # device_data: 16进制字符串
    # 组包
    device_msg = {
        "device_id": device_id,
        "device_type": device_type,
        "device_addr": device_addr,
        "device_port": device_port,
        "data_protocol": data_protocol,
        "data": device_data
    }

    # MQTT发布
    publish.single(topic=gateway_topic,
                   payload=json.dumps(device_msg),
                   hostname=mqtt_server_ip,
                   port=mqtt_server_port)
    logger.info("向Topic(%s)发布消息：%s" % (gateway_topic, device_msg))


# 串口数据读取线程
def process_mqtt():
    """
    :param device_id 设备地址
    :return:
    """
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, rc):
        logger.info("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        mqtt_client.subscribe("%s/#" % device_network)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        logger.info("收到数据消息" + msg.topic + " " + str(msg.payload))
        # 消息只包含device_cmd，为json字符串
        try:
            cmd_msg = json.loads(msg.payload)
            device_cmd = json.loads(cmd_msg["command"])
        except Exception, e:
            device_cmd = None
            logger.error("消息内容错误，%r" % msg.payload)

        # 根据topic确定设备
        device_info = devices_info_dict.get(msg.topic, None)
        # 对指令进行处理
        if device_info is not None:
            if device_cmd["func_code"] == const.fc_read_coils or device_cmd["func_code"] == const.fc_read_discrete_inputs:
                req_result = modbus_client.read_coils(device_cmd["addr"],
                                                      device_cmd["count"],
                                                      unit=int(device_info["device_addr"]))
                device_data = {
                    "func_code": device_cmd["func_code"],
                    "addr": device_cmd["addr"],
                    "count": device_cmd["count"],
                    "values": req_result.bits
                }

            elif device_cmd["func_code"] == const.fc_write_coil:
                req_result = modbus_client.write_coil(device_cmd["addr"],
                                                      device_cmd["value"],
                                                      unit=int(device_info["device_addr"]))
                res_result = modbus_client.read_coils(device_cmd["addr"],
                                                      1,
                                                      unit=int(device_info["device_addr"]))
                device_data = {
                    "func_code": device_cmd["func_code"],
                    "addr": device_cmd["addr"],
                    "count": 1,
                    "values": req_result.bits[0:1]
                }
            elif device_cmd["func_code"] == const.fc_write_coils:
                req_result = modbus_client.write_coils(device_cmd["addr"],
                                                   device_cmd["values"],
                                                   unit=int(device_info["device_addr"]))
                counter = len(device_cmd["values"])
                res_result = modbus_client.read_coils(device_cmd["addr"],
                                                      counter,
                                                      unit=int(device_info["device_addr"]))
                device_data = {
                    "func_code": device_cmd["func_code"],
                    "addr": device_cmd["addr"],
                    "count": counter,
                    "values": res_result.bits
                }
            elif device_cmd["func_code"] == const.fc_write_register:
                req_result = modbus_client.write_register(device_cmd["addr"],
                                                      device_cmd["value"],
                                                      unit=int(device_info["device_addr"]))
                res_result = modbus_client.read_holding_registers(device_cmd["addr"],
                                                      1,
                                                      unit=int(device_info["device_addr"]))
                device_data = {
                    "func_code": device_cmd["func_code"],
                    "addr": device_cmd["addr"],
                    "count": 1,
                    "values": res_result.registers[0:1]
                }
            elif device_cmd["func_code"] == const.fc_write_registers:
                result = modbus_client.write_registers(device_cmd["addr"],
                                                       device_cmd["values"],
                                                       unit=int(device_info["device_addr"]))
                counter = len(device_cmd["values"])
                res_result = modbus_client.read_input_registers(device_cmd["addr"],
                                                      counter,
                                                      unit=int(device_info["device_addr"]))
                device_data = {
                    "func_code": device_cmd["func_code"],
                    "addr": device_cmd["addr"],
                    "count": counter,
                    "values": res_result.registers
                }
            elif device_cmd["func_code"] == const.fc_read_holding_registers:
                res_result = modbus_client.read_holding_registers(device_cmd["addr"],
                                                                  device_cmd["count"],
                                                                  unit=int(device_info["device_addr"]))
                device_data = {
                    "func_code": device_cmd["func_code"],
                    "addr": device_cmd["addr"],
                    "count": device_cmd["count"],
                    "values": res_result.registers
                }
            elif device_cmd["func_code"] == const.fc_read_input_registers:
                res_result = modbus_client.read_input_registers(device_cmd["addr"],
                                                                device_cmd["count"],
                                                                unit=int(device_info["device_addr"]))
                device_data = {
                    "func_code": device_cmd["func_code"],
                    "addr": device_cmd["addr"],
                    "count": device_cmd["count"],
                    "values": res_result.registers
                }
            else:
                logger.error("不支持的modbus指令：%d" % device_cmd["func_code"])
                device_data = None

            logger.debug("return device_data:%r" % device_data)
            if device_data is not None:
                publish_device_data(device_info["device_id"],
                                    device_info["device_type"],
                                    device_info["device_addr"],
                                    device_info["device_port"],
                                    json.dumps(device_data))
        else:
            logger.error("设备不存在，消息主题:%s" % msg.topic)


    mqtt_client = mqtt.Client(client_id=mqtt_client_id)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(mqtt_server_ip, mqtt_server_port, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    mqtt_client.loop_forever()


if __name__ == "__main__":

    # 初始化modbus客户端
    modbus_client = ModbusClient(method='rtu', port=serial_port, baudrate=serial_baund, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, timeout=1)
    modbus_client.connect()

    # 初始化mqtt监听
    mqtt_thread = threading.Thread(target=process_mqtt)
    mqtt_thread.start()

    # 加载设备数据
    load_devices_info_dict()

    # 发送设备信息
    for device_id in devices_info_dict:
        device_info = devices_info_dict[device_id]
        publish_device_data(device_info["device_id"],
                            device_info["device_type"],
                            device_info["device_addr"],
                            device_info["device_port"],
                            "")
    while True:
        #如果线程停止则创建
        if not mqtt_thread.is_alive():
            mqtt_thread = threading.Thread(target=process_mqtt)
            mqtt_thread.start()

        # res_result = modbus_client.read_input_registers(0, 1, unit=1)
        # print json.dumps(res_result.registers)

        logger.debug("处理完成，休眠5秒")
        time.sleep(2)
