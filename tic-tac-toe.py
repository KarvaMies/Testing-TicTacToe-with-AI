import random, os
from easyAI import TwoPlayerGame, AI_Player, Human_Player
from easyAI.AI import TranspositionTable

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

tt = TranspositionTable()
if os.path.exists(TT_DATA_FILE):
    tt.from_file(TT_DATA_FILE)


class RandomAI(AI_Player):
    def __init__(self, game):
        super().__init__(game)

    def simulate_move(self, game, move):
        """Makes simulated game to prevent updating tt"""
        sim_game = TicTacToe(game.players)
        sim_game.board = game.board[:]
        sim_game.current_player = game.current_player
        sim_game.nmove = game.nmove

        # simulate  make_move manually
        sim_game.board[move - 1] = "X" if sim_game.current_player == 1 else "0"
        sim_game.nmove += 1
        sim_game.current_player = 2 if sim_game.current_player == 1 else 1

        # rebuilding the ttentry because it shows the previous player
        board, prev_player, winner = sim_game.ttentry()
        curr_player = 1 if prev_player == 2 else 2
        new_entry = (board, curr_player, winner)
        return new_entry

    def ask_move(self, game):
        possible_moves = game.possible_moves()
        valid_moves = []

        # Checks if the move is already in tt
        for move in possible_moves:
            entry = self.simulate_move(game, move)
            if tt.d.get(entry) is None:
                valid_moves.append(move)

        # print(f"p moves: {possible_moves}")
        # print(f"v moves: {valid_moves}")

        # If not in tt, choose randomly
        if not valid_moves:
            valid_moves = possible_moves

        chosen_move = random.choice(valid_moves)
        return chosen_move


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
    print(f"Total positions in TT: {len(tt.d)}")
