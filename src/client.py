"""Клиент"""
import asyncio
import re
import json
from aioconsole import ainput
from logger import initialize_logger


class Client:
    """Класс клиента
    :param server_ip: ip сервера
    :param server_port: порт сервера
    :param reader: StreamReader
    :param writer: StreamWriter
    :param logger: логгер
    """
    def __init__(self, server_ip, server_port):
        self.ip = server_ip
        self.port = server_port
        self.reader = None
        self.writer = None
        self.logger = initialize_logger('client')

    async def connect_to_server(self):
        """Подключение клиента к серверу"""
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.ip, self.port
            )
            await asyncio.gather(
                self.receive_messages(),
                self.enter_message()
            )
        except Exception as e:
            self.logger.error("Ошибка при подключении к серверу")

    async def receive_messages(self):
        """Принятие сообщения от сервера"""
        server_message = await self.get_server_message()
        info_str = 'Принято сообщение от сервера: ' + server_message['result']
        print(info_str)
        self.logger.info(info_str)

    async def get_server_message(self):
        """Чтение сообщения и его декодирование"""
        return json.loads((await self.reader.read(255)).decode('utf8'))   

    async def enter_message(self):
        """Ввод выражения"""
        client_message = None
        while True:
            client_message = await ainput(
                "Введите выражение: "
            )
            if re.match(r'^[\d+-/*()]+$', client_message):
                break
            else: 
                print("Выражение не должно содержать буквы или знаки кроме +-*/ !")
        self.writer.write(client_message.encode('utf8'))
        await self.writer.drain()

if __name__ == "__main__":
    host_ip = '127.0.0.1'
    port = '9090'
    client = Client(host_ip, port)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.connect_to_server())