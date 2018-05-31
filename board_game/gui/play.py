
from ..api.game import Game, MoveError, Teams, PieceType
from ..api import game
import math

import tkinter as tk

class Board(tk.Frame):
    def __init__(self, parent, get_square_colors, square_clicked=None):
        '''size is the size of a square, in pixels'''
        self.square_clicked = square_clicked
        self.get_square_colors = get_square_colors
        tk.Frame.__init__(self, parent)
        self.setup_board()

    def click_callback(self, event):
        x_tile = math.floor(event.x / self.size)
        y_tile = math.floor(event.y / self.size)
        print(str(x_tile) + "_" + str(y_tile))
        self.square_clicked(x_tile, y_tile)

    def setup_board(self):
        self.size = 32
        self.board_width = 5 * self.size
        self.board_height = 5 * self.size
        self.board = tk.Canvas(self, borderwidth=0, highlightthickness=0,
                                width=self.board_width, height=self.board_height, background="bisque")
        if self.click_callback is not None:
            self.board.bind("<Button-1>", self.click_callback)
        self.board_size = min(self.board_width,  self.board_height)
        self.board.pack(side="top", fill="both", expand=True, padx=2, pady=2)

        # this binding will cause a refresh if the user interactively
        # changes the window size
        self.board.bind("<Configure>", self.refresh)

    def fake_refresh(self):
        self.refresh_board(self.width, self.height, self.get_square_colors())

    def refresh_board(self, width, height, square_colors):
        self.width = width
        self.height = height
        xsize = int((width-1) / 5)
        ysize = int((height-1) / 5)
        self.board_size = min(xsize, ysize)
        self.board.delete("square")
        for y_tile in range(5):
            for x_tile in range(5):
                x1 = (x_tile * self.board_size)
                y1 = (y_tile * self.board_size)
                x2 = x1 + self.board_size
                y2 = y1 + self.board_size
                x_center = x1 + (x2 - x1)/2
                y_center = y1 + (y2 - y1)/2
                if (x_tile, y_tile) in square_colors:
                    if square_colors[(x_tile, y_tile)]["team"] is None:
                        self.board.create_rectangle(x1, y1, x2, y2, outline="black", fill="grey", tags="square")
                    else:
                        colour = square_colors[(x_tile, y_tile)]["team"].value
                        self.board.create_rectangle(x1, y1, x2, y2, outline="black", fill=colour, tags="square")
                    piece_type = square_colors[(x_tile, y_tile)]["piece_type"]
                    if piece_type == PieceType.King:
                        self.board.create_text(x_center, y_center,fill="darkblue",font="Times 10 italic bold", text="K")
                else:
                    self.board.create_rectangle(x1, y1, x2, y2, outline="black", fill="white", tags="square")

    def refresh(self, event):
        '''Redraw the board, possibly in response to window being resized'''
        xsize = int((event.width-1) / 5)
        ysize = int((event.height-1) / 5)
        self.board_size = min(xsize, ysize)
        self.board.delete("square")
        self.refresh_board(event.width, event.height, self.get_square_colors())

class GameBoard:

    def get_selected_squares(self, start, card_moves):
        absolute_moves = set()
        for relative_move in card_moves:
            if self.game.current_team == Teams.Blue:
                absolute_move = (start[0] - relative_move[0], start[1] - relative_move[1])
            else:
                absolute_move = (start[0] + relative_move[0], start[1] + relative_move[1])
            absolute_moves.add(absolute_move)
        return absolute_moves

    def get_selected_squares_visual(self, start, card_moves):
        absolute_moves = set()
        for relative_move in card_moves:
            absolute_move = (start[0] - relative_move[0], start[1] - relative_move[1])
            absolute_moves.add(absolute_move)
        return absolute_moves

    def callback(self, x, y):
        piece = self.get_board_piece(self.game, x,  y)
        if self.game.current_team == Teams.Red:
            y = 4 - y
            x = 4 - x
        if piece is not None and piece["team"] == self.game.current_team:
            self.start = (x,y)
        if self.start is None:
            return
        end = (x, y)
        if self.whole_thing.selected_card is not None and end in self.get_selected_squares(self.start, self.whole_thing.selected_card["moves"]):
            self.whole_thing.make_move(self.start, end, self.whole_thing.selected_card["name"])
            self.start = None
        self.boardGui.fake_refresh()

    def get_board_piece(self, current_game, x, y):
        if current_game.current_team == Teams.Blue:
            return current_game.state[y][x]
        else:
            return current_game.state[4-y][4-x]

    def square_colors(self):
        square_colors = {}
        for row in range(5):
            for col in range(5):
                piece = self.get_board_piece(self.game, row,  col)
                if piece is not None:
                    square_colors[(row, col)] = {"team": piece['team'], "piece_type": piece['type']}
        if self.start is not None:
            if self.game.current_team == Teams.Red:
                visual_start = (4 - self.start[0], 4 - self.start[1])
            else:
                visual_start = self.start
            if self.whole_thing.selected_card is not None and self.start is not None:
                for possible_move in self.get_selected_squares_visual(visual_start, self.whole_thing.selected_card["moves"]):
                    square_colors[possible_move] = {"team": None, "piece_type": PieceType.Pawn}
        return square_colors

    def __init__(self, root, game, whole_thing):
        self.game = game
        self.boardGui = Board(root, self.square_colors, self.callback)
        self.whole_thing = whole_thing
        self.start = None


class SpareCard:

    def callback(self, x, y):
        print("clicked at", x, y)

    def get_selected_squares(self, start, card_moves):
        absolute_moves = set()
        for relative_move in card_moves:
            absolute_move = (start[0] - relative_move[0], start[1] - relative_move[1])
            absolute_moves.add(absolute_move)
        return absolute_moves

    def square_colors(self):
        square_colors = {}
        for possible_move in self.get_selected_squares((2,2), self.game.spare_card["moves"]):
            square_colors[possible_move] = {"team": None, "piece_type": PieceType.Pawn}
        square_colors[(2,2)] = {"team": self.game.current_team, "piece_type": PieceType.Pawn}
        return square_colors

    def __init__(self, root, game):
        self.game = game
        self.boardGui = Board(root, self.square_colors, self.callback)

class PlayerCard:

    def callback(self, x, y):
        if self.board_side == "bottom":
            self.whole_thing.select_card(self.card)

    def square_colors(self):
        square_colors = {}
        if self.board_side == 'top':
            if self.game.current_team == Teams.Red:
                team = Teams.Blue
            else:
                team = Teams.Red
        else:
            team = self.game.current_team
        self.card = list(self.game.team_cards[team].values())[self.card_number]
        for possible_move in self.get_selected_squares((2,2), self.card["moves"]):
            square_colors[possible_move] = {"team": None, "piece_type": PieceType.Pawn}
        square_colors[(2,2)] = {"team": team, "piece_type": PieceType.Pawn}
        return square_colors

    def get_selected_squares(self, start, card_moves):
        absolute_moves = set()
        for relative_move in card_moves:
            if self.board_side == "bottom":
                absolute_move = (start[0] - relative_move[0], start[1] - relative_move[1])
            else:
                absolute_move = (start[0] + relative_move[0], start[1] + relative_move[1])
            absolute_moves.add(absolute_move)
        return absolute_moves

    def __init__(self, root, game, board_side, card_number, whole_thing):
        self.game = game
        self.board_side = board_side
        self.card_number = card_number
        self.boardGui = Board(root, self.square_colors, self.callback)
        self.whole_thing = whole_thing

class WholeThing():
    def __init__(self):
        root = tk.Tk()

        #current_game = Game(red_cards=["tiger", "crab"], blue_cards=["monkey", "crane"], spare_card="dragon")
        self.current_game = Game()
        self.selected_card = None

        self.cards = {
            "top_player_left_card": PlayerCard(root, self.current_game, 'top', 0, self),
            "top_player_right_card": PlayerCard(root, self.current_game, 'top', 1, self),
            "bottom_player_left_card": PlayerCard(root, self.current_game, 'bottom', 0, self),
            "bottom_player_right_card": PlayerCard(root, self.current_game, 'bottom', 1, self),
            "spare_card": SpareCard(root, self.current_game)
        }
        
        self.board = GameBoard(root, self.current_game, self)

        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)

        self.cards["top_player_left_card"].boardGui.grid(row=0, column=0, sticky="ew")
        self.cards["top_player_right_card"].boardGui.grid(row=0, column=1, sticky="ew")
        self.board.boardGui.grid(row=1, column=0, sticky="nsew")
        self.cards["spare_card"].boardGui.grid(row=1, column=1, sticky="nsew")
        self.cards["bottom_player_left_card"].boardGui.grid(row=2, column=0, sticky="ew")
        self.cards["bottom_player_right_card"].boardGui.grid(row=2, column=1, sticky="ew")

        root.mainloop()

    def make_move(self, start, end, selected_card_name):
        self.current_game.move(start, end, selected_card_name)
        self.selected_card = None
        self.board.boardGui.fake_refresh()
        for card in self.cards.values():
            card.boardGui.fake_refresh()
        if self.current_game.gameover:
            print("Game Over!")

    def select_card(self, card):
        self.selected_card = card
        self.board.boardGui.fake_refresh()

if __name__ == "__main__":
    thing = WholeThing()
