import random
from collections import Counter, namedtuple
from enum import Enum
from operator import itemgetter
from typing import List, Iterator, Union, Optional, Dict, Tuple

Players = namedtuple("Players", "X O")
MiniMaxResult = namedtuple("MiniMaxResult", "player cell result")


class Player(Enum):
    USER = "user"
    EASY = "easy"
    MED = "medium"
    HARD = "hard"


class TicTacToe(object):
    GRID_BORDER: str = "---------"
    GRID_SIZE: int = 3

    def __init__(self, players: Players, start_grid: str = None, silent: bool = True) -> None:
        self.grid: List[str]
        self.cache: Dict[str, Tuple[str, int]] = {}

        # named tuple for players
        self.players: Players = players
        # don't print anything if played in silent mode - e.g. for simulation
        self.silent = silent

        # set the grid
        if start_grid and len(start_grid) == TicTacToe.GRID_SIZE ** 2:
            self.grid = [x for x in start_grid.upper().replace("_", " ")]
        elif start_grid is None:
            self.grid = [" " for _ in range(TicTacToe.GRID_SIZE ** 2)]
        else:
            raise ValueError("Please provide an input for {} cells.".format(TicTacToe.GRID_SIZE ** 2))

    @staticmethod
    def check_command() -> Optional:
        """
        Request user input for game setup and then initiate the instance.

        Returns:
            Returns an instance to the class or a falsy value if user wants to end program.

        """
        BAD_PARAMETER_MESSAGE: str = "Bad parameters"
        while True:
            try:
                command = input("Input command:\n").split(maxsplit=3)
            except ValueError:
                print(BAD_PARAMETER_MESSAGE)
                continue

            if command[0] == "exit":
                return None
            elif command[0] == "start" and len(command) == 3:
                try:
                    # initialise and set up a pre-populated board - for debugging
                    # return TicTacToe(players=Players(Player(command[1]), Player(command[2])),
                    #                  silent=False,
                    #                  start_grid="X__XO_OXO")

                    # initialise and set up an empty board
                    return TicTacToe(players=Players(Player(command[1]), Player(command[2])),
                                     silent=False)
                except ValueError:
                    print(BAD_PARAMETER_MESSAGE)
            else:
                print(BAD_PARAMETER_MESSAGE)

    @property
    def next_mark(self) -> str:
        """
        Figure out which player plays next.

        Returns:
            str: Mark for the next player (determined on counting marks)

        """
        count: Counter = self._count_moves()
        return "X" if count["X"] <= count["O"] else "O"

    @property
    def rows(self) -> List[List[str]]:
        """
        Yields slices along board rows

        Returns:
            List[List[str]]

        """
        yield from [self.grid[i * TicTacToe.GRID_SIZE: (i + 1) * TicTacToe.GRID_SIZE] for i in
                    range(TicTacToe.GRID_SIZE)]

    @property
    def rows_index(self) -> List[List[int]]:
        """
        Use the indices to change values in the row slices.
        Couldn't find a way to change the references and reflect back into the grid.

        Returns:
            List of indices into the original grid aligned with the rows property

        """
        yield from [[i * TicTacToe.GRID_SIZE + j
                     for j in range(TicTacToe.GRID_SIZE)]
                    for i in range(TicTacToe.GRID_SIZE)]

    @property
    def columns(self) -> List[List[str]]:
        """
        Yields slices for columns

        Returns:
            List of List of cells on the board

        """
        yield from [self.grid[i::TicTacToe.GRID_SIZE] for i in range(TicTacToe.GRID_SIZE)]

    @property
    def columns_index(self) -> List[List[int]]:
        yield from [[j + i * TicTacToe.GRID_SIZE for i in range(TicTacToe.GRID_SIZE)]
                    for j in range(TicTacToe.GRID_SIZE)]

    @property
    def diagonals(self) -> List[List[str]]:
        yield from [[self.grid[i * TicTacToe.GRID_SIZE + i] for i in range(TicTacToe.GRID_SIZE)],
                    [self.grid[(i + 1) * TicTacToe.GRID_SIZE - 1 - i] for i in range(TicTacToe.GRID_SIZE)]]

    @property
    def diagonals_index(self) -> List[List[int]]:
        yield from [[i * TicTacToe.GRID_SIZE + i for i in range(TicTacToe.GRID_SIZE)],
                    [(i + 1) * TicTacToe.GRID_SIZE - 1 - i for i in range(TicTacToe.GRID_SIZE)]]

    @property
    def all_combo(self) -> List[List[str]]:
        """
        Combine rows, columns and diagonals for testing board state

        Returns:

        """
        for i in [self.rows, self.columns, self.diagonals]:
            yield from i

    @property
    def all_combo_index(self) -> List[List[str]]:
        for i in [self.rows_index, self.columns_index, self.diagonals_index]:
            yield from i

    @property
    def empty_cells(self) -> List[int]:
        """
        List of indices to empty cells

        Returns:
            List of indices to empty cells

        """
        return [i for i, v in enumerate(self.grid) if v == " "]

    @property
    def winner(self) -> Union[str, None]:
        """
        Check if we have a final state (winner or draw)

        Returns:
            Mark of the winner, 'draw' or None if grid not terminal

        """
        # check if we have a winner
        for line in self.all_combo:
            winner = set(line).pop() if len(set(line)) == 1 else False
            if winner and winner in "XO":
                not self.silent and print(winner, "wins")
                return winner
        else:
            # check if we have a draw
            if sum(self._count_moves().values()) == TicTacToe.GRID_SIZE ** 2:
                not self.silent and print("Draw")
                return "draw"

        return None

    def print_grid(self) -> List[str]:
        """
        Return a string to print the grid.

        Returns:

        """
        return [TicTacToe.GRID_BORDER, *["| " + " ".join(row) + " |" for row in self.rows], TicTacToe.GRID_BORDER]

    def __repr__(self) -> str:
        """
        Show state of the grid as a string.

        Returns:

        """
        return "".join(self.grid).replace(" ", "_")

    def __str__(self) -> str:
        """
        Show state of the board as a list of rows.

        Returns:

        """
        return str(list(self.rows))

    def next_move(self, mark: str = None, cell: int = None) -> None:
        """
        Make the next move on the board. Logic different for human, easy, medium or hard computer player.
        - Easy will just make random moves.
        - Medium will make terminal moves (winning / blocking opponent), otherwise fall back to easy.
        - Hard will calculate MiniMax strategy.

        If called with mark and cell arguments it will execute this specific move without invoking logic.
        Used for simulation.

        Args:
            mark (): Mark (X,O) to use to mark the cell below.
            cell (): Cell to mark on the board.
        """

        coordinates_list: Iterator[Union[str, int]]

        # make a fixed move - for simulation
        if mark is not None and cell is not None:
            self.grid[cell] = mark

        # let the player make a move
        else:
            current_player = getattr(self.players, self.next_mark)

            if current_player == Player.USER:
                while True:
                    coord_input = input("Enter the coordinates: \n")
                    if not coord_input:
                        print("You should enter two numbers!")
                        continue
                    else:
                        coordinates_list = coord_input.split()

                    if len(coordinates_list) == 2 and all(i.isnumeric() for i in coordinates_list):
                        coordinates_list = list(map(lambda x: int(x) - 1, coordinates_list))
                        list_element = ((TicTacToe.GRID_SIZE - 1 - coordinates_list[1]) * TicTacToe.GRID_SIZE +
                                        coordinates_list[0])
                    else:
                        print("You should enter numbers!")
                        continue

                    if max(coordinates_list) > TicTacToe.GRID_SIZE - 1:
                        print("Coordinates should be from 1 to {}!".format(TicTacToe.GRID_SIZE))
                        continue

                    if self.grid[list_element] in ["X", "O"]:
                        print("This cell is occupied! Choose another one!")
                        continue
                    else:
                        self.grid[list_element] = self.next_mark
                        break
            else:
                # print status if not silent
                not self.silent and print('Making move level "{}"'.format(current_player.value))

                if current_player == Player.EASY:
                    self.grid[self._move_easy()] = self.next_mark
                elif current_player == Player.MED:
                    if self._move_med():
                        self.grid[self._move_med()] = self.next_mark
                    else:
                        # do easy move if no obvious move possible
                        self.grid[self._move_easy()] = self.next_mark
                elif current_player == Player.HARD:
                    self.grid[self._move_hard(repr(self))[0]] = self.next_mark

    def _move_hard(self, grid: str, depth: int = 1) -> Tuple[int, int]:
        """
        Calculate MiniMax strategy for 'hard' player. Is called recursively to simulate different outcomes.
        Uses caching to accelerate the calculation of game states

        Args:
            grid (): Grid to simulate
            depth (): Depth of recursion

        Returns:
            Tuple[int, int] which field to mark based on MiniMax strategy
        """
        results: List[List[int, int]] = []
        score: int = 0
        cache_value: Optional[Tuple[str, int]]

        simulation = TicTacToe(players=Players(Player("medium"), Player("medium")), start_grid=grid)

        for i in simulation.empty_cells:

            # set the next mark
            simulation.next_move(mark=simulation.next_mark, cell=i)

            # cache values for grid setups we've seen before
            cache_value = self.cache.get(repr(simulation), None)

            # check if we find a cache value
            if cache_value:
                # append value from cache - invert if value was calculated for the other player
                results.append([i, cache_value[1] if cache_value[0] == self.next_mark else -cache_value[1]])
            else:
                # check if the grid is in a final state (win/draw)
                if simulation.winner:
                    # player wins
                    if simulation.winner == self.next_mark:
                        score = 1
                    # player loses
                    elif simulation.winner != "draw":
                        score = -1
                # if not final state, walk down the tree until we get to a final state
                else:
                    score = self._move_hard(grid=repr(simulation), depth=depth + 1)[1]

                # store the resulting score and populate the cache
                results.append([i, score])
                self.cache[repr(simulation)] = (self.next_mark, score)

            # reset the mark for next iteration
            simulation.next_move(mark=" ", cell=i)

        # return min/max value depending on what level we are on (i.e. proponent vs. opponent move)
        return random.choice(list(
                filter(lambda item: item[1] == max(map(itemgetter(1), results)), results)
                if depth % 2 else
                filter(lambda item: item[1] == min(map(itemgetter(1), results)), results)))

    def _move_med(self) -> Optional[int]:
        """

        Returns:
            Index to make the mark in.
        """
        # see if we can finish the game
        for i, j in zip(self.all_combo, self.all_combo_index):
            count = Counter(i)
            # check for winning move
            if count[self.next_mark] == 2 and count[" "] == 1:
                return j[i.index(" ")]

        # see if we can stop the other player from finishing
        for i, j in zip(self.all_combo, self.all_combo_index):
            count = Counter(i)
            # check for blocker move - need to negate the player mark
            if count["O" if self.next_mark == "X" else "X"] == 2 and count[" "] == 1:
                return j[i.index(" ")]

    def _move_easy(self) -> int:
        """

        Returns:
            Index to make the mark in.
        """
        # do random move
        return random.choice(self.empty_cells)

    def _count_moves(self) -> Counter:
        """
        Counter for the grid status. Used to determine next player.

        Returns:
            Counter for X and O values.
        """
        return Counter(cell for cell in self.grid if cell in "XO")


if __name__ == "__main__":

    while True:
        # game = TicTacToe(start_grid=input("Enter cells:\n"))
        game = TicTacToe.check_command()

        if game:
            print(*game.print_grid(), sep="\n")
            while not game.winner:
                game.next_move()
                print(*game.print_grid(), sep="\n")
        else:
            break
