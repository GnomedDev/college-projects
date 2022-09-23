from enum import Enum, auto
from operator import add, sub
from typing import Callable, Generator, Iterable


def clear_screen():
    print("\33[H\33[2J\33[3J", end="")

class Cell(Enum):
    EMPTY = auto()
    RED_PLAYER = auto()
    YELLOW_PLAYER = auto()

    def __str__(self):
        match self:
            case Cell.EMPTY:
                return "⚪"
            case Cell.RED_PLAYER:
                return "🔴"
            case Cell.YELLOW_PLAYER:
                return "🟡"

class Grid:
    __slots__ = ("rows", "columns", "current_player", "inner")

    rows: int
    columns: int
    current_player: Cell

    # row = inner[i]
    # cell = inner[i][i]
    inner: list[list[Cell]]

    def __init__(self, columns: int = 7, rows: int = 6) -> None:
        self.rows = rows
        self.columns = columns
        self.current_player = Cell.RED_PLAYER
        self.inner = [[Cell.EMPTY for _ in range(columns)] for _ in range(rows)]

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
        for column_idx in range(0, self.columns):
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

    def play(self):
        while True:
            clear_screen()
            print(self)
            
            index = input(f"{self.current_player} Column to drop piece on: ")

            try:
                index = int(index) - 1
            except ValueError:
                continue

            if not self.add_piece(index):
                continue # No space on the board

            if self.check_win_condition():
                # Do one more refresh to show winning play
                clear_screen()
                print(f"{self}\n{self.current_player} You won!")
                return

            self.swap_current_player()

try:
    Grid().play()
except KeyboardInterrupt:
    print()
