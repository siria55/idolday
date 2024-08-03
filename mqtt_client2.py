#!/usr/bin/env python
#coding=utf-8
import hmac
import base64
from hashlib import sha1
import time
from paho.mqtt.client import MQTT_LOG_INFO, MQTT_LOG_NOTICE, MQTT_LOG_WARNING, MQTT_LOG_ERR, MQTT_LOG_DEBUG
# from paho.mqtt.client import CabackAp
from paho.mqtt.enums import CallbackAPIVersion
import paho.mqtt.client as mqtt


instanceId = "post-cn-lsk3uo7yv02"
ALIBABA_CLOUD_ACCESS_KEY_ID = 'LTAI5tLQxLqhF7ywAw797nwj'
ALIBABA_CLOUD_ACCESS_KEY_SECRET = 'XDS3TwzljwoCEdwf6AqkP9GiXe4cY5'
groupId = 'GID_TOAI'

#MQTT ClientID，由 GroupID 和后缀组成，需要保证全局唯一
client_id=groupId+'@@@'+'client'
topic = 'twowheels'
#MQTT 接入点域名，实例初始化之后从控制台获取
brokerUrl="{}.mqtt.aliyuncs.com".format(instanceId)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
# client.on_connect = on_connect
# client.on_message = on_message




def on_log(client, userdata, level, buf):
    if level == MQTT_LOG_INFO:
        head = 'INFO'
    elif level == MQTT_LOG_NOTICE:
        head = 'NOTICE'
    elif level == MQTT_LOG_WARNING:
        head = 'WARN'
    elif level == MQTT_LOG_ERR:
        head = 'ERR'
    elif level == MQTT_LOG_DEBUG:
        head = 'DEBUG'
    else:
        head = level
    print('%s: %s' % (head, buf))
def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    # client.subscribe(topic, 0)
    # for i in range(1, 11):
    #     print(i)
    #     rc = client.publish(topic, str(i), qos=0)
    #     print ('rc: %s' % rc)
    #     time.sleep(0.1)
def on_message(client, userdata, msg):
    print(msg.topic + ' ' + str(msg.payload))
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected disconnection %s' % rc)
        
        
        


userName ='Signature'+'|'+ALIBABA_CLOUD_ACCESS_KEY_ID+'|'+instanceId
password = base64.b64encode(hmac.new(ALIBABA_CLOUD_ACCESS_KEY_SECRET.encode(), client_id.encode(), sha1).digest()).decode()
# userName = 'Signature|LTAI5tLQxLqhF7ywAw797nwj|post-cn-lsk3uo7yv02'
# password = '2t7H13eG6kywjC9fSnuhoDyfvow='

client.on_log = on_log
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

client.username_pw_set(userName, password)

message = "Temperature: 25°C"
client.connect(brokerUrl, 1883, 60)
client.publish(topic, message)
client.disconnect()
print(f"Published message '{message}' to topic '{topic}'")







import paho.mqtt.client as mqtt

# 定义 MQTT Broker 信息
broker = "mqtt.eclipseprojects.io"  # 公共测试 Broker
port = 1883
topic = "home/livingroom/temperature"

# 创建一个 MQTT 客户端实例
client = mqtt.Client()

# 连接到 MQTT Broker
client.connect(broker, port, 60)

# 发布消息
message = "Temperature: 25°C111"
client.publish(topic, message)

# 断开连接
client.disconnect()

print(f"Published message '{message}' to topic '{topic}'")