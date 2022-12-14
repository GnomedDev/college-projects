import asyncio
import json
from typing import Awaitable

from websockets.client import WebSocketClientProtocol, connect

from shared import *


def ainput(question: str) -> Awaitable[str]:
    return asyncio.to_thread(input, question)

class ClientGrid:
    __slots__ = ("rows", "columns", "client_player", "current_player", "inner")

    rows: int
    columns: int
    client_player: Cell
    current_player: Cell

    # row = inner[i]
    # cell = inner[i][i]
    inner: list[list[Cell]]

    def __init__(self, game_start: GameStart, client_player: Cell) -> None:
        self.rows = game_start.rows
        self.columns = game_start.columns
        self.client_player = client_player
        self.current_player = Cell.RED_PLAYER
        self.inner = [[Cell.EMPTY for _ in range(self.columns)] for _ in range(self.rows)]

    def __str__(self) -> str:
        # Start off with a line of indexes
        out = " " + "  ".join(map(str, range(1, self.columns + 1))) + "\n"

        # Loop through each column and row, concatenating each cell
        for column in self.inner:
            for cell in column:
                out += f"{cell} "

            out += "\n"

        return out


    def swap_current_player(self):
        assert self.current_player != Cell.EMPTY

        match self.current_player:
            case Cell.RED_PLAYER:
                self.current_player = Cell.YELLOW_PLAYER
            case Cell.YELLOW_PLAYER:
                self.current_player = Cell.RED_PLAYER

    async def wait_for_update(self, connection: WebSocketClientProtocol) -> bool:
        board_update = BoardUpdate.parse_raw(await connection.recv())
        self.inner = board_update.board
        return board_update.game_end

    async def play(self, connection: WebSocketClientProtocol):
        while True:
            clear_screen()
            print(self)
            if self.current_player == self.client_player:
                index = await ainput(f"{self.current_player} Column to drop piece on: ")

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

                current_player = self.current_player
                player_name = current_player.player_name()

                print(f"{self}\n{current_player} {player_name} wins!")
                break

            self.swap_current_player()

async def main(username: str, server_uri: str):
    async with connect(server_uri) as server_connection:
        await server_connection.send(ClientServerMessage(
            c = "login",
            a = {"username": username}
        ).json())

        current_rooms = CurrentRooms.parse_raw(await server_connection.recv())
        while True:
            clear_screen()
            print("Current Open Rooms")
            for room_id, username in current_rooms.rooms.items():
                print(f"{room_id}: {username}")

            room_to_join = await ainput("Choose the room number to join or type CREATE: ")
            try:
                room_to_join = int(room_to_join)
            except ValueError:
                if room_to_join.upper() != "CREATE":
                    continue

                client_player = Cell.RED_PLAYER
                clear_screen()
                print("Waiting for a connection...")
                await server_connection.send(ClientServerMessage(
                    c = "create",
                    a = {},
                ).json())
            else:
                client_player = Cell.YELLOW_PLAYER
                await server_connection.send(ClientServerMessage(
                    c = "connect",
                    a = {},
                    t = room_to_join
                ).json())

            # The server may send back a CURRENT_ROOMS payload if the room we
            # are connecting to is invalid, otherwise it is a GAME_START
            response = json.loads(await server_connection.recv())
            if "rows" in response:
                game_start = GameStart.parse_obj(response)
                grid = ClientGrid(game_start, client_player)

                return await grid.play(server_connection)
            else:
                current_rooms = CurrentRooms.parse_obj(response)

with open("last_credentials.json", "r+") as last_creds_file:
    last_creds_raw = last_creds_file.read()
    if last_creds_raw == "":
        saved_username = formatted_username = ""
        saved_server_uri = formatted_server_uri = ""
    else:
        last_creds_file.seek(0)
        last_creds = json.loads(last_creds_raw)

        saved_username = last_creds["username"]
        saved_server_uri = last_creds["server_uri"]

        formatted_username = f" ({saved_username})"
        formatted_server_uri = f" ({saved_server_uri})"

    while True:
        username = input(f"Enter your username{formatted_username}: ") or saved_username
        server_uri = input(f"Enter the URI of the server{formatted_server_uri}: ") or saved_server_uri

        if username and server_uri:
            break
        else:
            print("Please enter both a username and server_uri!")

    json.dump({"username": username, "server_uri": server_uri}, last_creds_file)

asyncio.run(main(username, server_uri))
