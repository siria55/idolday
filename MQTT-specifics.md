## 上传声音

```
client to server
{
    "command": "request_upload"
}

server to client
{
    "command": "request_upload"
    "upload_url": "oss_url",
    "voice_id": "xxx",
}

上传完成后 client 告知 server
{
    "command": "nofity_upload",
    "voice_id": "xxx",
}
```

## OTA
```
client to server
{
    "command": "request_update",
    "version": "xxx" 
}

server to client
{
    "command": "request_update",
    "firmware_url": "xxx",
}
```

## server 向 client 发出的行为指令（下列都是 server to client）


```
移动类
{
    "command": "action",
    "action": "move_forward|move_backward|turn_left|turn_right",
    "value": {
        "duration": 10,   // 其中duration是行进/旋转持续时间, speed字段如果是前后则为移动的速度 单位mm/s,如果是左右转的角度（度为单位）
        "speed": 5,
    }
}
播放声音
{
    "command": "action",
    "action": "sound_play",
    "value": {
        "url": "xxxxxx",
        "loop": true|false
    }
}
表情
{
    "command": "action",
    "action": "screen_emoji",
    "value": {
        "emoji_name": "xxx",
    }
}
音量设定
{
    "command": "action",
    "action": "volumn_set",
    "value": 0-100, // 的音量值
}

增大|减小音量
{
    "command": "action",
    "action": "volumn_up|volumn_down"  // 设备获得指令后增大/降低音量，如果已经是0/100就不调节
}

带时间序列的组合动作
{
    "command": "action",
    "action": "combine",
    "value": [
        {
            "time": 0,
            "action": xxx
            "value": xxx
        },...   // 数组的一个元素是前面 action 中的一种
    ]
}
```

## 高级控制
直接对舵机旋转/声音播放/表情变化的高级控制
```
{
    "command": "action",
    "action": "advance_control",
    "value": [
        {
            "time": 0,
            "motor_action": [
                {
                    "motor_id": 0, 二轮定义为左0右1，表示需要改变状态的马达id
                    "value": {
                        "pwm: "xxx", float 0-1的占空比
                        "duration": xxx 毫秒
                    },
                },
                {
                    "motor_id": 1, 二轮定义为左0右1，表示需要改变状态的马达id
                    "value": {
                        "pwm: "xxx", float 0-1的占空比
                        "duration": xxx 毫秒
                    },
                }
            ]
            "sound_action": [
                {
                    "speaker_id": 0,
                    "value": {
                        "url": "xxxxxx",
                        "loop": true|false
                    },
                    "speaker_id": 1,
                    "value": {
                        "url": "xxxxxx",
                        "loop": true|false
                    }
                }
            ],
            "screen_action": [
                {
                    screen_id:0,//屏幕id，一个屏就是0，多个再议
                    value:{
                        "url": "xx",  // 位图序列下载的静态资源url
                        "duration: "2000" 毫秒
                    }
                    loop:true/false
                },
                {}, ...
            ]
        }
    ]
}
```
