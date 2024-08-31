from fastapi.testclient import TestClient

import msgpack

from ..main import app

from ..mqtt.test_client import get_mq_client
from ..database import get_db

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 404

res = {
    "status_code": 200,
    "device_id": "hhh",
    "mqtt_client_id": "GID_TOAI@@@hhh",
    "mqtt_broker_url": "post-cn-lsk3uo7yv02.mqtt.aliyuncs.com",
    "mqtt_port": 1883,
    "mqtt_username": "Token|LTAI5tLQxLqhF7ywAw797nwj|post-cn-lsk3uo7yv02",
    "mqtt_password": "RW|LzMT+XLFl5s/YWJ/MlDz4t/Lq5HC1iGU1P28HAMaxYzmBSHQsWXgdISJ1ZJ+2cxaMED19DyqgtZ6hMXT2v/Kbzkdyt06avPgbJGYgJWUr5piesdvDY0i8fAAvwixnwBfYnosgd308tbvooOIjF1CZbbT9jN7u6zbapNrisZN9ntTEtL5yIEK2CQgoJWL8b3AwXp1M60Hjp+oi27VLLD/3EnVgGDRZD+dFuw1XcoIaXil0ruD7MtJ2E4kEPXvRnhpdqvyabOF170S2wbZObWHENkwvkpgh2KXQXrpfocrsr2mVqt1V+/oIsCAJgNV4tX7ybNe0hsYT9T49dyq7aqbVZ1wj8BnE4v4",
    "get_topic": "soundbox/hhh/get",
    "post_topic": "soundbox/hhh/post",
    "firmware_version": "1.0.0"
}

def test_mqtt_auth():
    response = client.post("/api/v1/devices/auth-mqtt", json={"device_id": "hhh", "device_token": "f8e930f261602b52cea21897306bc88f"})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data['status_code'] == res['status_code']
    assert res_data['device_id'] == 'hhh'

    mqtt_client_id = res_data['mqtt_client_id']
    mqtt_broker_url = res_data['mqtt_broker_url']
    mqtt_port = res_data['mqtt_port']
    mqtt_username = res_data['mqtt_username']
    mqtt_password = res_data['mqtt_password']
    get_topic = res_data['get_topic']
    post_topic = res_data['post_topic']


def test_mq_msg():
    client = get_mq_client()
    client.publish('soundbox/hhh/post', msgpack.packb({"command": "online"}))
    client.publish('soundbox/hhh/post', msgpack.packb({"command": "lost"}))


def test_user_login():
    response = client.post("/api/v1/login", json={"phone_number": "15129037418", "password": "112233"})
    assert response.status_code == 200
