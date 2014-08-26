plugin_yykj_serial
==================

支持易运科技的硬件产品


关于配置项的说明：
[
    {
        "network_name": "network1", 
        "protocol": "", 
        "channels": [
            {
                "name": "tcpserver1", 
                "type": "tcp_server", 
                "params": {
                    "host": "127.0.0.1", 
                    "port": 10010
                }, 
                "preconfigured_devices": [
                    {
                        "device_type": "", 
                        "device_addr": "", 
                        "device_port": ""
                    }, 
                    {
                        "device_type": "", 
                        "device_addr": "", 
                        "device_port": "", 
                        "protocol": ""
                    }
                ]
            }, 
            {
                "name": "serial", 
                "type": "serial", 
                "params": {
                    "port": "/dev/ttyusb0", 
                    "baund": 9600
                }
            }
        ]
    }
]

具体运行时的设备情况存储在devices.txt中
支持的通道类型有Serial、HttpServer、TcpServer、UdpServer、HttpClient、TcpClient、UdpClient