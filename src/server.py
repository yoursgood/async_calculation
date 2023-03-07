"""Сервер"""
import asyncio
import json
from logger import initialize_logger


class Server:
    """Класс сервера
    :param ip: ip, который будет использоваться
    :type server_ip: str
    :param port: порт сервера
    :type port: int
    :param loop: цикл событий
    """
    def __init__(self, ip, port, loop):
        self.ip = ip
        self.port = port
        self.loop = loop
        self.clients = {}
        self.logger = initialize_logger('server')
        self.logger.info(f"Инициализирован сервер {self.ip}:{self.port}")

    def start_server(self):
        """Запуск сервера"""
        try:
            server = asyncio.start_server(
                self.accept_client, self.ip, self.port
            )
            self.loop.run_until_complete(server)
            self.loop.run_forever()
        except Exception as e:
            self.logger.error("Ошибка при запуске сервера")
        
        self.shutdown_server()

    def accept_client(self, client_reader, client_writer):
        """Callback-функция, запускаемая при подключении клиента
        :param client_reader: StreamReader
        :param client_writer: StreamWriter
        """
        client = {'reader': client_reader, 'writer': client_writer}
        task = asyncio.create_task(self.process_message(client))
        self.clients[task] = client
        
        ip = client['writer'].get_extra_info('peername')[0]
        port = client['writer'].get_extra_info('peername')[1]
        
        self.logger.info(f"Подключен новый клиент: {ip}:{port}")
        task.add_done_callback(self.disconnect_client)
        
    async def decode_message(self, client):
        """Декодирование сообщения от клиента
        :param client: клиент, посылающий сообщение
        """
        return str((await  client['reader'].read(255)).decode('utf8'))
    
    async def process_message(self, client):
        """Прием сообщения пользователя, возвращение результатов вычисления
        Возвращает результат в случае верного ввода, иначе сообщение об ошибке
        :param client: клиент, посылающий сообщение
        """
        client_message = await self.decode_message(client)
        self.logger.info(f"Получено сообщение от клиента {client_message}")
        result = None
        info_str = None
        try:
            result = eval(client_message)
            info_str = (
                f"{client_message} = {result}"
            )
        except Exception as e:
            info_str = f"{client_message} не вычислено. "\
                       f"Произошла ошибка: {e}"
                       
        print(
            f"Клиент {client['writer'].get_extra_info('peername')[1]}, результат: {info_str}"
            )
        self.logger.info(info_str)
        json_message = self.to_json(client_message, info_str)
        client['writer'].write(json_message)
        await client['writer'].drain()
    
    def disconnect_client(self, task):
        """Отсоединение клиента
        :param task: задача
        """
        client = self.clients[task]
        del self.clients[task]
        client['writer'].close()
        self.logger.info("Соединение с клиентом закрыто")

    def shutdown_server(self):
        """Отключение сервера"""
        info_str = "Сервер отключен"
        print(info_str)
        self.logger.info(info_str)
        self.loop.stop()

    def to_json(self, message, res):
        """Функция для превращения данных для отправки в json и их кодирование
        :param message: сообщение, пришедее от клиента
        :param res: результат, вычисленный сервером
        """
        return json.dumps(
            {'expression': message, 'result': res}
        ).encode()


if __name__ == '__main__':
    host_ip = '127.0.0.1'
    port = '9090'
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server = Server(host_ip, port, loop)
    server.start_server()