uvicorn main:app --host 0.0.0.0 --port 8001

mysql -hrm-2ze8try6287fyk6j3go.mysql.rds.aliyuncs.com -P3306 -uhotdog -p


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
sudo systemctl start fastapi
sudo systemctl enable fastapi
sudo systemctl restart fastapi
