import asyncio

from websockets.client import WebSocketClientProtocol, connect

from shared import *


class ClientGrid:
    __slots__ = ("rows", "columns", "client_player", "current_player", "inner")

    rows: int
    columns: int
    client_player: Cell
    current_player: Cell

    # row = inner[i]
    # cell = inner[i][i]
    inner: list[list[Cell]]

    def __init__(self, client_player: Cell, columns: int, rows: int) -> None:
        self.rows = rows
        self.columns = columns
        self.client_player = client_player
        self.current_player = Cell.RED_PLAYER
        self.inner = [[Cell.EMPTY for _ in range(rows)] for _ in range(columns)]


    async def wait_for_update(self, connection: WebSocketClientProtocol) -> bool:
        board_update = BoardUpdate.parse_raw(await connection.recv())
        self.inner = board_update.board
        return board_update.game_end

    async def play(self, connection: WebSocketClientProtocol):
        while True:
            clear_screen()
            print(self)
            if self.current_player == self.client_player:
                index = input(f"{self.current_player} Column to drop piece on: ")

                try:
                    index = int(index) - 1
                except ValueError:
                    continue
                
                if index >= self.columns:
                    continue

                await connection.send(ClientServerMessage(
                    c = "play_piece",
                    a = {"column": index}
                ).json())

            # Returns true on game end
            if await self.wait_for_update(connection):
                # Do one more refresh to show winning play
                clear_screen()
                print(f"{self}\n{self.current_player} You won!")

async def main():
    username = input("Enter your username: ")
    server_uri = input("Enter the URI of the server: ")
    async with connect(server_uri) as server_connection:
        await server_connection.send(ClientServerMessage(
            c = "login",
            a = {"username": username}
        ).json())
        
        current_rooms = CurrentRooms.parse_raw(await server_connection.recv())

        clear_screen()
        print("Current Open Rooms")
        for room_id, username in current_rooms.rooms.items():
            print(f"{room_id}: {username}")

        room_to_join = input("Choose the room number to join or type CREATE: ")
        if room_to_join.upper() == "CREATE":
            clear_screen()
            print("Waiting for a connection...")
            await server_connection.send(ClientServerMessage(
                c = "create",
                a = {},
            ).json())
        else:
            await server_connection.send(ClientServerMessage(
                c = "connect",
                a = {},
                t = room_to_join
            ).json())

        game_details = GameStart.parse_raw(await server_connection.recv())
        await ClientGrid(**game_details.dict()).play(server_connection)

asyncio.run(main())
