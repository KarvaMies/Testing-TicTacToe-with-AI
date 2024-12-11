import random
from easyAI import AI_Player
from transposition_table import tt


class RandomAI(AI_Player):
    def __init__(self, game):
        super().__init__(game)

    def simulate_move(self, game, move):
        """Makes simulated game to prevent updating transposition table when not intended"""
        from ticTacToe import TicTacToe

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
        """Checks if the move is already in TT and chooses randomly
        from any moves that aren't, if possible"""
        possible_moves = game.possible_moves()
        valid_moves = []

        # Checks if the move is already in tt
        if len(tt.d) < 5477:  # TT already full
            for move in possible_moves:
                entry = self.simulate_move(game, move)
                if tt.d.get(entry) is None:
                    valid_moves.append(move)

        # If not in tt, choose randomly
        if not valid_moves:
            valid_moves = possible_moves

        chosen_move = random.choice(valid_moves)
        return chosen_move
