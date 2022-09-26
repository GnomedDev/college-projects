from enum import Enum
from typing import Any, Optional

import pydantic
from typing_extensions import Self

def clear_screen():
    print("\33[H\33[2J\33[3J", end="")


class Cell(Enum):
    EMPTY = 0
    RED_PLAYER = 1
    YELLOW_PLAYER = 2

    def __str__(self):
        match self:
            case Cell.EMPTY:
                return "⚪"
            case Cell.RED_PLAYER:
                return "🔴"
            case Cell.YELLOW_PLAYER:
                return "🟡"

    def swap(self) -> Self:
        assert self != self.EMPTY

        match self:
            case Cell.RED_PLAYER:
                return Cell.YELLOW_PLAYER
            case Cell.YELLOW_PLAYER:
                return Cell.RED_PLAYER

class ClientServerMessage(pydantic.BaseModel):
    c: str
    a: dict[str, Any]
    t: Optional[str] = None

class CurrentRooms(pydantic.BaseModel):
    rooms: dict[int, str]

class GameStart(pydantic.BaseModel):
    rows: int
    columns: int
    client_player: Cell

class BoardUpdate(pydantic.BaseModel):
    board: list[list[Cell]]
    game_end: bool
