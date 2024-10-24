uvicorn main:app --host 0.0.0.0 --port 8000

mysql -hrm-2ze8try6287fyk6j3go.mysql.rds.aliyuncs.com -P3306 -uhotdog -p

TOAItoai1234

systemd /etc/systemd/system/idolday.service
```
[Unit]
Description=idolday service
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/idolday
ExecStart=/root/idolday/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers=5
Restart=always

[Install]
WantedBy=multi-user.target
```

启动和启用服务：

bash
sudo systemctl stop idolday
sudo systemctl start idolday
sudo systemctl enable idolday
sudo systemctl status idolday
sudo systemctl restart idolday

moonshot api key
sk-vJWtg3lpODHLl7niiRBGSpGmPTOEWzdtpVewW9flswfVQDYv # 个人号
sk-gu1UoYqojz3IwJTvB4Fqc5zpcg2mKt0dCyH9xuLAnll8UeL9 # 法人号

依赖的系统包：
ffmpeg
memcached

docker 运行
docker build -t fastapiapp .
docker run -d --name fastapiapp_container -p 8000:8000 fastapiapp

## 测试

python -m pytest
