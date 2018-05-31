import random
import os

from enum import Enum

class PieceType(Enum):
    King = "king"
    Pawn = "pawn"


class Teams(Enum):
    Red = "red"
    Blue = "blue"

redKing = {"team": Teams.Red, "type": PieceType.King}
redPawn = {"team": Teams.Red, "type": PieceType.Pawn}
blueKing = {"team": Teams.Blue, "type": PieceType.King}
bluePawn = {"team": Teams.Blue, "type": PieceType.Pawn}

class MoveError(Exception):
    def __init__(self, message):
        self.message = message

class Game:

    @staticmethod
    def state_from_string(state_string):
        state = []
        #remove blank last element from trailing comma
        lines = state_string.split('\n')[:-1]
        for line in lines:
            state.append([])
            #remove blank last element from trailing comma
            string_pieces = line.split(",")[:-1]
            for piece_string in string_pieces:
                if piece_string in ["..", "TT"]:
                    piece = None
                elif piece_string == "rp":
                    piece = redPawn
                elif piece_string == "rk":
                    piece = redKing
                elif piece_string == "bp":
                    piece = bluePawn
                elif piece_string == "bk":
                    piece = blueKing
                else:
                    raise Exception("unrecognised piece " + piece_string)
                state[-1].append(piece)
        return state


    def __init__(self, red_cards=None, blue_cards=None, spare_card=None, start_state=None):

        #default param value are global, so I don't think setting this as it in the signature might cause concurrency badness
        if start_state is None:
            # remember the "thrones" in the middle of the top and bottom rows!
            #blue is assumed to start at the bottom, red at the top
            self.state = [
                [redPawn, redPawn, redKing, redPawn, redPawn],
                [None, None, None, None, None],
                [None, None, None, None, None],
                [None, None, None, None, None],
                [bluePawn, bluePawn, blueKing, bluePawn, bluePawn]
            ]
        else:
            #should probs verify this
            self.state = start_state

        # remember move values are relative to the side the player is sitting on
        # default assumes Red moving down
        # this is inverted for Blue
        cards = {
            "tiger": {"name": "tiger", "moves": [(0, -1), (0, 2)], "starting_team": Teams.Blue},
            "crab": {"name": "crab", "moves": [(-2, 0), (0, 1), (2, 0)], "starting_team": Teams.Blue},
            "monkey": {"name": "monkey", "moves": [(-1, -1), (1, -1), (1, 1), (-1, 1)], "starting_team": Teams.Blue},
            "crane": {"name": "crane", "moves": [(-1, -1), (0, 1), (1, -1)], "starting_team": Teams.Blue},
            "dragon": {"name": "dragon", "moves": [(-2, 1), (2, 1), (-1, -1), (1, -1)], "starting_team": Teams.Red},
            "elephant": {"name": "elephant", "moves": [(-1, 1), (-1, 0), (1, 1), (1, 0)], "starting_team": Teams.Red},
            "mantis": {"name": "mantis", "moves": [(-1, 1), (1, 1), (0, -1)], "starting_team": Teams.Red},
            "boar": {"name": "boar", "moves": [(-1, 0), (0, 1), (1, 0)], "starting_team": Teams.Red},
            "frog": {"name": "frog", "moves": [(2, 0), (1, 1), (-1, -1)], "starting_team": Teams.Red},
            "goose": {"name": "goose", "moves": [(1, 1), (1, 0), (-1, 0), (-1, -1)], "starting_team": Teams.Blue},
            "horse": {"name": "horse", "moves": [(1, 0), (0, 1), (0, -1)], "starting_team": Teams.Red},
            "eel": {"name": "eel", "moves": [(1, 1), (1, -1), (-1, 0)], "starting_team": Teams.Blue},
            "rabbit": {"name": "rabbit", "moves": [(1, -1), (-1, 1), (-2, 0)], "starting_team": Teams.Blue},
            "rooster": {"name": "rooster", "moves": [(1, 0), (1, -1), (-1, 0), (-1, 1)], "starting_team": Teams.Red},
            "ox": {"name": "ox", "moves": [(0, 1), (-1, 0), (0, -1)], "starting_team": Teams.Blue},
            "cobra": {"name": "cobra", "moves": [(1, 0), (-1, 1), (-1, -1)], "starting_team": Teams.Red}
        }

        self.team_cards = {
            Teams.Red: {},
            Teams.Blue: {}
        }

        if red_cards is not None and len(red_cards) == 2:
            for card_name in red_cards:
                try:
                    self.team_cards[Teams.Red][card_name] = cards[card_name]
                except KeyError:
                    raise Exception(card_name + " isn't a valid card name")
                del cards[card_name]
        elif red_cards is not None:
            raise Exception("red_cards must have 2 cards or be None")

        if blue_cards is not None and len(blue_cards) == 2:
            for card_name in blue_cards:
                try:
                    self.team_cards[Teams.Blue][card_name] = cards[card_name]
                except KeyError:
                    raise Exception(card_name + " isn't a valid card name")
                del cards[card_name]
        elif blue_cards is not None:
            raise Exception("blue_cards must have 2 cards or be None")

        if spare_card is not None:
            try:
                self.spare_card = cards[spare_card]
            except KeyError:
                raise Exception(spare_card + " isn't a valid card")
            del cards[spare_card]

        # we have to do random draws after ALL pre-picked cards have been removed
        # to prevent accidently drawing a pre-picked card

        if red_cards is None:
            for _ in range(2):
                card_name = random.choice(list(cards.keys()))
                self.team_cards[Teams.Red][card_name] = cards[card_name]
                del cards[card_name]
        
        if blue_cards is None:
            for _ in range(2):
                card_name = random.choice(list(cards.keys()))
                self.team_cards[Teams.Blue][card_name] = cards[card_name]
                del cards[card_name]
        
        if spare_card is None:
            card_name = random.choice(list(cards.keys()))
            self.spare_card = cards[card_name]
            del cards[card_name]

        all_chosen_cards = [
            self.spare_card["name"],
            list(self.team_cards[Teams.Red].keys())[0],
            list(self.team_cards[Teams.Red].keys())[1],
            list(self.team_cards[Teams.Blue].keys())[0],
            list(self.team_cards[Teams.Blue].keys())[1]
        ]
        if len(all_chosen_cards) != len(set(all_chosen_cards)):
            raise("Duplicate cards!")

        self.current_team = self.spare_card["starting_team"]

        self.gameover = False
        self.winningMethod = None

    def __str__(self):
        representation = ""
        for y in range(0,5):
            for x in range(0,5):
                piece = self.state[y][x]
                if x == 2 and y in [0, 4] and piece is None:
                    representation += "TT"
                elif piece is None:
                    representation += ".."
                else:
                    if piece["team"] == Teams.Blue:
                        representation += "b"
                    elif piece["team"] == Teams.Red:
                        representation += "r"
                    if piece["type"] == PieceType.King:
                        representation += "k"
                    elif piece["type"] == PieceType.Pawn:
                        representation += "p"
                representation += ","
            representation += "\n"
        return representation

    def unchecked_move(self, start, end, start_piece=None):
        if start_piece is None:
            start_piece = self.state[start[1]][start[0]]
        self.state[end[1]][end[0]] = start_piece
        self.state[start[1]][start[0]] = None

    def destination(self, x, y,  move, team):
        if team == Teams.Blue:
            new_x = x - move[0]
            new_y = y - move[1]
        elif team == Teams.Red:
            new_x = x + move[0]
            new_y = y + move[1]
        return new_x, new_y

    def can_move(self, team):
        for x in range(0,5):
            for y in range(0,5):
                possible_start = self.state[x][y]
                if possible_start is not None and possible_start["team"] == team:
                    for card in self.team_cards[self.current_team].values():
                        for move in card["moves"]:
                            end_x, end_y = self.destination(x, y, move, team)
                            try:
                                end_piece = self.state[end_y][end_x]
                            except IndexError:
                                continue
                            if end_piece is None or end_piece["team"] != team:
                                return True, {"start": (x, y), "end": [end_x, end_y], "card": card["name"]}
        return False, None

    def relative_move(self, start, move, card_name):
        self.move(start, [start[0]+move[0], start[1]+move[1]], card_name)

    def current_team_cards(self):
        return self.team_cards[self.current_team]

    def move(self, start, end, card_name):
        if self.gameover:
            raise MoveError("Game is over")
        if start is None and end is None:
            (can_move, move_details) = self.can_move(self.current_team)
            if can_move:
                raise MoveError("It's possible end move " + str(move_details))
            else:
                self.end_turn(card_name)
                return
        try:
            start_piece = self.state[start[1]][start[0]]
            end_piece = self.state[end[1]][end[0]]
        except IndexError:
            raise MoveError("start or end is outside the board")
        except TypeError:
            raise MoveError("x and y must be integers")
        if start_piece is None or start_piece["team"] != self.current_team:
            raise MoveError(str(self.current_team) + " has no piece at " + str(start[0]) + "," + str(start[1]))
        if end_piece is not None and end_piece["team"] == self.current_team:
            raise MoveError(str(end_piece["team"]) + " already has a piece at " + str(end[0]) + "," + str(end[1]))
        chosen_card = self.team_cards[self.current_team].get(card_name)
        if chosen_card is None:
            raise MoveError(card_name + " is not one of the current players cards")
        legal_move = False
        for move in chosen_card["moves"]:
            possible_x, possible_y = self.destination(start[0], start[1], move, self.current_team)
            if end[0] == possible_x and end[1] == possible_y:
                legal_move = True
        if not legal_move:
            raise MoveError("piece cannot move here with chosen card")
        self.unchecked_move(start, end, start_piece=start_piece)
        self.check_for_win(end, end_piece)
        self.end_turn(card_name)

    def check_for_win(self, end, end_piece):
        # because the moves already happened at this point
        # the start piece has already taken the position of the end piece
        start_piece = self.state[end[1]][end[0]]
        if end_piece is not None and end_piece["type"] == PieceType.King:
            self.gameover = True
            self.winningMethod = "Way of the stone"
            return
        if start_piece["type"] == PieceType.King:
            if self.current_team == Teams.Blue and end[0] == 2 and end[1] == 0:
                self.gameover = True
                self.winningMethod = "Way of the stream"
            elif self.current_team == Teams.Red and end[0] == 2 and end[1] == 4:
                self.gameover = True
                self.winningMethod = "Way of the stream"

    def end_turn(self, card_name=None):
        if card_name is None:
            card_name = random.choice(list(self.team_cards[self.current_team].keys()))
        self.team_cards[self.current_team][self.spare_card["name"]] = self.spare_card
        self.spare_card = self.team_cards[self.current_team][card_name]
        del self.team_cards[self.current_team][card_name]
        if self.current_team == Teams.Red:
            self.current_team = Teams.Blue
        elif self.current_team == Teams.Blue:
            self.current_team = Teams.Red
