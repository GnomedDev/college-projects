import asyncio
import contextlib

from websockets.server import WebSocketServerProtocol, serve

from shared import *


class ServerGrid:
    red_player: WebSocketServerProtocol
    yellow_player: WebSocketServerProtocol

    rows: int
    columns: int

class Server:
    waiting_clients: dict[int, WebSocketServerProtocol]
    current_games: list[ServerGrid]
    waiting_rooms: dict[int, str]
    last_id: int = 1

    async def new_client(self, connection: WebSocketServerProtocol):
        login_message = ClientServerMessage.parse_raw(await connection.recv())
        username = login_message.a["username"]
        assert login_message.c == "login"

        await connection.send(CurrentRooms(rooms=self.waiting_rooms).json())
        create_or_connect = ClientServerMessage.parse_raw(await connection.recv())

        if create_or_connect.c == "connect":
            create_or_connect.t
        else:
            self.waiting_rooms.keys()[-1]
            

    async def serve(self):
        async with serve(self.new_client, port=4000):
            with contextlib.suppress(KeyboardInterrupt):
                await asyncio.Future()

server = Server()

asyncio.run(Server().serve())
