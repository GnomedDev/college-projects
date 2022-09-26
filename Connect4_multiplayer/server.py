import asyncio
import contextlib
from operator import add, sub
from typing import Awaitable, Callable, Generator, Iterable

from websockets.server import WebSocketServerProtocol, serve

from shared import *


class ServerGrid:
    red_player: WebSocketServerProtocol
    yellow_player: WebSocketServerProtocol

    inner: list[list[Cell]]

    rows: int
    columns: int
    current_player: Cell
    has_finished: asyncio.Event

    def __init__(self, yellow_player: WebSocketServerProtocol):
        self.rows = 6
        self.columns = 7
        self.yellow_player = yellow_player
        self.has_finished = asyncio.Event()
        self.current_player = Cell.RED_PLAYER
        self.inner = [[Cell.EMPTY for _ in range(self.columns)] for _ in range(self.rows)]


    def get_connection(self, cell: Cell) -> WebSocketServerProtocol:
        assert cell != Cell.EMPTY
        match cell:
            case Cell.RED_PLAYER:
                return self.red_player
            case Cell.YELLOW_PLAYER:
                return self.yellow_player

    def swap_current_player(self):
        assert self.current_player != Cell.EMPTY

        match self.current_player:
            case Cell.RED_PLAYER:
                self.current_player = Cell.YELLOW_PLAYER
            case Cell.YELLOW_PLAYER:
                self.current_player = Cell.RED_PLAYER

    def check_neighbours(self, iterable: Iterable[Cell]):
        """Checks for 4 consecutive Cells of self.current_player

        Args:
            iterable: The iterable to find consecutive cells in.
        """

        same_count = 0
        for cell in iterable:
            if cell != Cell.EMPTY and cell == self.current_player:
                same_count += 1
                if same_count == 4:
                    return True
            else:
                same_count = 0

        return False

    def diagnoal_iter(self, x: int, y: int, y_op: Callable[[int, int], int]) -> Generator[Cell, None, None]:
        """A generator to loop over `self.inner` diagonally

        This is performed by taking `x` and `y` from the current position on the board
        and allows me to continue using check_neighbours for the actual checking of
        "are there 4 matching cells".

        Args:
            x: The x position of the starting Cell.
            y: The y position of the starting Cell.
            y_op: The operation to perform on `y`, either `add` or `sub` for up right or down right matches.
        """

        i = 0
        while True:
            try:
                yield self.inner[y_op(y, i)][x + i]
            except IndexError:
                # Went off the board, no more Cells
                return

            i += 1


    def add_piece(self, column_idx: int) -> bool:
        """Adds a piece to the Grid

        Args:
            column_idx: The index of the column to add the piece to.
            kind: The type of Cell to add, must not be EMPTY

        Returns:
            If piece addition was successful
        """
        assert self.current_player != Cell.EMPTY

        for row_idx in range(self.rows - 1, -1, -1):
            if self.inner[row_idx][column_idx] == Cell.EMPTY:
                self.inner[row_idx][column_idx] = self.current_player
                return True

        return False

    def check_win_condition(self) -> bool:
        assert self.current_player != Cell.EMPTY

        # Check horizontal
        if any(map(self.check_neighbours, self.inner)):
            return True

        # Check vertical
        for column_idx in range(self.columns):
            if self.check_neighbours((row[column_idx] for row in self.inner)):
                return True

        # Check diagonal
        for (y, row) in enumerate(self.inner):
            for (x, cell) in enumerate(row):
                if cell == Cell.EMPTY:
                    continue

                if self.check_neighbours(self.diagnoal_iter(x, y, add)):
                    return True

                if self.check_neighbours(self.diagnoal_iter(x, y, sub)):
                    return True

        return False


    def broadcast(self, message: str) -> Awaitable[list[Any]]:
        return asyncio.gather(*(
            c.send(message) for c in (self.yellow_player, self.red_player)
        ))

    async def play(self, red_player: WebSocketServerProtocol):
        self.red_player = red_player

        await self.broadcast(GameStart(rows=self.rows, columns=self.columns).json())

        while True:
            connection = self.get_connection(self.current_player)
            play_piece = ClientServerMessage.parse_raw(await connection.recv())

            assert play_piece.c == "play_piece"
            column: int = play_piece.a["column"]
            self.add_piece(column)
        
            
            game_end = self.check_win_condition()
            self.swap_current_player()

            await self.broadcast(BoardUpdate(board=self.inner, game_end=game_end).json())
            if game_end:
                break

        self.has_finished.set()

class Server:
    room_waiters: dict[int, asyncio.Event]
    current_games: dict[int, ServerGrid]
    waiting_rooms: dict[int, str]

    def __init__(self):
        self.room_waiters = {}
        self.waiting_rooms = {}
        self.current_games = {}

    def next_id(self):
        """Finds the next free ID to use for waiting_rooms"""
        return next((
            index
            for index, id in enumerate(self.waiting_rooms.keys())
            if index != id
        ), 0)

    async def new_client(self, connection: WebSocketServerProtocol):
        login_message = ClientServerMessage.parse_raw(await connection.recv())
        username = login_message.a["username"]
        assert login_message.c == "login"

        while True:
            await connection.send(CurrentRooms(rooms=self.waiting_rooms).json())
            create_or_connect = ClientServerMessage.parse_raw(await connection.recv())

            if create_or_connect.c == "create":
                room_id = self.next_id()
                self.waiting_rooms[room_id] = username
                self.room_waiters[room_id] = asyncio.Event()

                # Wait for a different user to connect and setup a game
                await self.room_waiters[room_id].wait()
                await self.current_games[room_id].play(connection)
            else: # "connect"
                room_id = create_or_connect.t
                assert room_id is not None

                if (waiter := self.room_waiters.pop(room_id, None)) is None:
                    continue

                del self.waiting_rooms[room_id]
                self.current_games[room_id] = ServerGrid(yellow_player=connection)

                # Wake up the "create" task and wait until the game finishes
                waiter.set()
                await self.current_games[room_id].has_finished.wait()

            break

    async def serve(self):
        async with serve(self.new_client, port=4000):
            with contextlib.suppress(KeyboardInterrupt):
                await asyncio.Future()

server = Server()

asyncio.run(Server().serve())
