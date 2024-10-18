import os
import pika
import json
import aria2p

# 从环境变量中读取RabbitMQ连接信息
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')
vhost = '/baize'
queue_name = 'download_queue'

# 从环境变量中读取aria2连接信息
aria2_host = os.getenv('ARIA2_HOST', 'localhost')
aria2_port = os.getenv('ARIA2_PORT', '6800')
aria2_secret = os.getenv('ARIA2_SECRET', '')

# 连接到aria2
aria2 = aria2p.Client(
    host=f'http://{aria2_host}',
    port=int(aria2_port),
    secret=aria2_secret
)


def create_download_task(download_type, url, save_path):
    options = {'dir': save_path}

    if download_type == 'http':
        # HTTP下载
        print(f"Starting HTTP download: {url} -> {save_path}")
        aria2.add_uris([url], options=options)
    elif download_type == 'magnet':
        # 磁力链接下载
        print(f"Starting magnet download: {url} -> {save_path}")
        aria2.add_magnets([url], options=options)
    else:
        print(f"Unknown download type: {download_type}")


def on_message(channel, method, properties, body):
    print("Received message:", body)
    try:
        message = json.loads(body)
        download_type = message.get('type')
        url = message.get('url')
        save_path = message.get('save_path')

        # 调用aria2创建下载任务
        create_download_task(download_type, url, save_path)

        # 确认消息处理成功
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print("Failed to process message:", e)
        channel.basic_nack(delivery_tag=method.delivery_tag)


# 连接到RabbitMQ
credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
parameters = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, virtual_host=vhost,
                                       credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# 声明队列
channel.queue_declare(queue=queue_name, durable=True)

# 订阅队列消息
channel.basic_consume(queue=queue_name, on_message_callback=on_message)

print('Waiting for messages...')
channel.start_consuming()
