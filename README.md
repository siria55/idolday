uvicorn main:app --host 0.0.0.0 --port 8000

mysql -hrm-2ze8try6287fyk6j3go.mysql.rds.aliyuncs.com -P3306 -uhotdog -p

TOAItoai1234

systemd /etc/systemd/system/fastapi.service
```
[Unit]
Description=FastAPI Service
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/bothub
ExecStart=/root/bothub/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动和启用服务：

bash
sudo systemctl stop fastapi
sudo systemctl start fastapi
sudo systemctl enable fastapi
sudo systemctl status fastapi
sudo systemctl restart fastapi

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
