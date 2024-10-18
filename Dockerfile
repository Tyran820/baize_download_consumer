# 使用Python 3.10的官方slim版本作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录下的consumer.py文件到容器中
COPY baize_download_consumer.py /app/baize_download_consumer.py

# 安装程序所需的依赖库
RUN pip install pika aria2p

# 暴露aria2的RPC端口
EXPOSE 6800

# 设置环境变量的默认值（如果需要，可以在docker-compose或运行时进行覆盖）
ENV RABBITMQ_HOST=localhost \
    RABBITMQ_PORT=5672 \
    RABBITMQ_USER=guest \
    RABBITMQ_PASSWORD=guest \
    ARIA2_HOST=localhost \
    ARIA2_PORT=6800 \
    ARIA2_SECRET=

# 运行Python consumer程序
CMD ["python", "/app/baize_download_consumer.py"]
