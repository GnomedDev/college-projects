from enum import Enum, auto
from operator import add, sub
from typing import Callable, Generator, Iterable, Optional


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

def check_neighbours(iterable: Iterable[Cell]):
    """Checks for 4 consecutive Cells of the same value

    Args:
        iterable: The iterable to find consecutive cells in.
    """

    same_count = 0
    last_cell = None

    for cell in iterable:
        if cell != Cell.EMPTY and cell == last_cell:
            same_count += 1
            if same_count == 3:
                return True
        else:
            last_cell = cell
            same_count = 0

    return False

class Grid:
    rows: int
    columns: int
    
    same_count: int
    last_cell: Optional[Cell]

    # row = inner[i]
    # cell = inner[i][i]
    inner: list[list[Cell]]

    def __init__(self, columns: int = 6, rows: int = 7) -> None:
        if columns >= 10:
            print("please don't")
            quit()

        self.rows = rows
        self.columns = columns
        self.inner = [[Cell.EMPTY for _ in range(rows)] for _ in range(columns)]

    def __str__(self) -> str:
        # Start off with a line of indexes
        out = " " + "  ".join(map(str, range(1, self.columns + 2))) + "\n"

        # Loop through each column and row, concatenating each cell
        for column in self.inner:
            for cell in column:
                out += f"{cell} "

            out += "\n"

        return out


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


    def add_piece(self, column_idx: int, kind: Cell) -> bool:
        """Adds a piece to the Grid

        Args:
            column_idx: The index of the column to add the piece to.
            kind: The type of Cell to add, must not be EMPTY

        Returns:
            If piece addition was successful
        """
        assert kind != Cell.EMPTY

        for row_idx in range(self.rows - 2, -2, -1):
            if self.inner[row_idx][column_idx] == Cell.EMPTY:
                self.inner[row_idx][column_idx] = kind
                return True

        return False

    def check_win_condition(self) -> bool:
        # Check horizontal
        if any(map(check_neighbours, self.inner)):
            return True

        # Check vertical
        for column_idx in range(0, self.columns):
            if check_neighbours((row[column_idx] for row in self.inner)):
                return True

        # Check diagonal
        for (y, row) in enumerate(self.inner):
            for (x, cell) in enumerate(row):
                if cell == Cell.EMPTY:
                    continue

                if check_neighbours(self.diagnoal_iter(x, y, add)):
                    return True

                if check_neighbours(self.diagnoal_iter(x, y, sub)):
                    return True

        return False

    def play(self):
        current_player = Cell.RED_PLAYER
        while True:
            clear_screen()
            print(self)
            
            index = input(f"{current_player} Column to drop piece on: ")

            try:
                index = int(index) - 1
            except ValueError:
                continue

            self.add_piece(index, current_player)
            if self.check_win_condition():
                # Do one more refresh to show winning play
                clear_screen()
                print(f"{self}\n{current_player} You won!")
                return

            # Swap current player
            match current_player:
                case Cell.RED_PLAYER:
                    current_player = Cell.YELLOW_PLAYER
                case Cell.YELLOW_PLAYER:
                    current_player = Cell.RED_PLAYER

try:
    Grid().play()
except KeyboardInterrupt:
    pass
