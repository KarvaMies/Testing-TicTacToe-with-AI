import os
from easyAI import TwoPlayerGame, Human_Player
from transposition_table import tt
from randomAI import RandomAI

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

TT_DATA_FILE = "saved_tt.data"

if os.path.exists(TT_DATA_FILE):
    tt.from_file(TT_DATA_FILE)


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
        self.history = []

    def possible_moves(self):
        return [i + 1 for i, cell in enumerate(self.board) if cell == " "]

    def make_move(self, move):
        self.board[move - 1] = "X" if self.current_player == 1 else "0"
        self.history.append(move)
        tt.store(game=self, moves_made=self.nmove)

    def unmake_move(self, move):
        self.board[move - 1] = " "

    def winner(self):
        for line in WIN_LINES:
            if (
                all(self.board[pos] == self.board[line[0]] for pos in line)
                and self.board[line[0]] != " "
            ):
                return self.board[line[0]]
        return None

    def show(self):
        print("\n", self.board[6], "│", self.board[7], "│", self.board[8])
        print("───┼───┼───")
        print("", self.board[3], "│", self.board[4], "│", self.board[5])
        print("───┼───┼───")
        print("", self.board[0], "│", self.board[1], "│", self.board[2])

    def is_over(self):
        return (self.possible_moves() == []) or (self.winner() != None)

    def ttentry(self):
        return tuple(["".join(self.board), self.current_player, self.winner()])


if __name__ == "__main__":
    n = 0
    total_games = 0
    while n < 100:  # there are 5478 legal boards including empty board
        players = [RandomAI(game=TicTacToe), RandomAI(game=TicTacToe)]
        game = TicTacToe(players)
        verbose_mode = any(isinstance(player, Human_Player) for player in players)
        game.play(verbose=verbose_mode)
        if (game.winner() != None) and (verbose_mode == True):
            print(f"\n{game.winner()} won!")
        elif (game.winner() == None) and (verbose_mode == True):
            print("\nIt's a draw!")
        tt.to_file(TT_DATA_FILE)
        if (len(tt.d) % 100 == 0) or ((len(tt.d) >= 5449) and len(tt.d) % 10 == 0):
            print(f"Positions in Transposition Table: {len(tt.d)}")
        if len(tt.d) >= 5477:
            n += 1
        if n == 1:
            print(f"All legal states reached (hopefully): {len(tt.d)}")
        total_games += 1
        if verbose_mode == True:
            n = 100
    print(f"Total positions in TT: {len(tt.d)}\nGames played: {total_games}")
