# 使用官方 Python 运行时作为父镜像
FROM python:3.10-slim

# 设置工作目录为 /app
WORKDIR /app

# 将当前目录内容复制到容器的 /app 中
COPY . /app

# 安装 requirements.txt 中指定的依赖
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir --upgrade -r requirements.txt

# 让端口 80 可用于外界
EXPOSE 8000

# 定义环境变量
# ENV NAME World

# 在容器启动时运行 Python 应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
