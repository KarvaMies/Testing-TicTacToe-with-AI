import random, sys, os
from easyAI import TwoPlayerGame, Human_Player
from transposition_table import tt
from randomAI import RandomAI

BUGS = [False] * 10

WIN_LINES = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],  # horiz.
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],  # vertical
    [0, 4, 8],
    [2, 4, 6],  # diagonal
]

WIN_LINES_NO_TOP_RIGHT = [
    [0, 1, 2],
    [3, 4, 5],  # horiz.
    [0, 3, 6],
    [1, 4, 7],  # vertical
    [2, 4, 6],  # diagonal
]

WIN_LINES_NO_DIAG = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],  # horiz.
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],  # vertical
]

FOUR_CORNERS_PATTERN = [0, 2, 6, 8]

TT_DATA_FILE = "saved_tt.data"
if not os.path.exists(TT_DATA_FILE):
    print("TT not found. Run ticTacToe.py first")
    sys.exit()
tt.from_file(TT_DATA_FILE)

FILENAME = "placeholder.txt"


class BugEncounteredException(Exception):
    pass


class TicTacToe(TwoPlayerGame):
    """The board positions are numbered as follows:
    7 8 9
    4 5 6
    1 2 3
    """

    def __init__(self, players):
        self.players = players
        self.board = [" " for _ in range(9)]
        self.current_player = 1
        self.nmove = 0
        self.winner = None
        self.history = []
        self.swap_not_done = True

    def possible_moves(self):
        if BUGS[2]:
            return [i + 1 for i, _ in enumerate(self.board)]
        return [i + 1 for i, cell in enumerate(self.board) if cell == " "]

    def make_move(self, move):
        if BUGS[5]:
            self.board[move - 1] = "X" if random.randint(1, 2) == 1 else "0"
        else:
            self.board[move - 1] = "X" if self.current_player == 1 else "0"
        self.history.append(move)
        entry = self.ttentry()
        if not tt.d.get(entry):  # Bug found!
            with open(FILENAME, "a") as file:
                file.write(f"{self.ttentry()}, {self.history}")
            raise BugEncounteredException()

    def unmake_move(self, move):
        self.board[move - 1] = " "

    def is_winner(self):
        if BUGS[0]:
            win_lines = WIN_LINES_NO_TOP_RIGHT
        elif BUGS[3]:
            win_lines = WIN_LINES_NO_DIAG
        elif BUGS[4]:
            return None
        else:
            win_lines = WIN_LINES
        if (
            BUGS[8]
            and self.swap_not_done
            and (not any(self.board[pos] == " " for pos in FOUR_CORNERS_PATTERN))
        ):
            for i, pos in enumerate(self.board):
                symbol = "X" if self.current_player == "X" else "0"
                if pos != " ":
                    self.board[i] = symbol
                self.swap_not_done = False
        if BUGS[9]:
            for pos in range(len(self.board) - 2):
                if (
                    self.board[pos] == self.board[pos + 1] == self.board[pos + 2]
                    and self.board[pos] != " "
                ):
                    self.winner = self.board[pos]
        else:
            for line in win_lines:
                if not any(self.board[pos] == " " for pos in line) and BUGS[1]:
                    self.winner = "X" if self.current_player == 1 else "0"
                elif (
                    all(self.board[pos] == self.board[line[0]] for pos in line)
                    and self.board[line[0]] != " "
                ):
                    self.winner = self.board[line[0]]

    def is_over(self):
        if (BUGS[6]) and (self.winner != None):
            self.winner = None
            return True
        elif (BUGS[7]) and (self.winner != None):
            self.winner = "0" if self.winner == "X" else "X"
            return True
        return (self.possible_moves() == []) or (self.winner != None)

    def ttentry(self):
        self.is_winner()
        if BUGS[6]:
            winner = None
        elif BUGS[7] and self.winner != None:
            winner = "0" if self.winner == "X" else "X"
        else:
            winner = self.winner
        return tuple(["".join(self.board), self.current_player, winner])

    def show(self):
        print("\n", self.board[6], "│", self.board[7], "│", self.board[8])
        print("───┼───┼───")
        print("", self.board[3], "│", self.board[4], "│", self.board[5])
        print("───┼───┼───")
        print("", self.board[0], "│", self.board[1], "│", self.board[2])


if __name__ == "__main__":
    simulations = 100
    for i, bug in enumerate(BUGS):
        BUGS = [False] * 10
        BUGS[i] = True
        bug_counter = 0
        if not os.path.exists("logs"):
            os.makedirs("logs")
        FILENAME = f"logs/bug_id_{i}_log.txt"
        with open(FILENAME, "w") as file:
            file.write("\n")
        for _ in range(simulations):
            players = [RandomAI(game=TicTacToe), RandomAI(game=TicTacToe)]
            game = TicTacToe(players)
            verbose_mode = any(isinstance(player, Human_Player) for player in players)
            try:
                game.play(verbose=verbose_mode)
                if (game.winner != None) and (verbose_mode):
                    print(f"\n{game.winner} won!")
                elif (game.winner == None) and (verbose_mode):
                    print("\nIt's a draw!")
            except BugEncounteredException as e:
                if verbose_mode:
                    print("Bug encountered and logged - Game terminated.")
                bug_counter += 1

        # Edit the file to add the first line containing the results
        percentage = (bug_counter / simulations) * 100 if simulations > 0 else 0
        line = f"Bugs detectd: {bug_counter}/{simulations} or {percentage:.0f}%\n"
        content = "placeholder text"
        with open(FILENAME, "r") as file:
            content = file.readlines()
        content[0] = line
        with open(FILENAME, "w") as file:
            file.writelines(content)
