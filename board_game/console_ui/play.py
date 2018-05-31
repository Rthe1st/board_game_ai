from ..api.game import Game, MoveError
from ..api import game
import os

def pretty_str(game, reverse=False):
    string = "  0  1  2  3  4\n"
    rows = str(game).split("\n")
    if reverse:
        rows = list(reversed(rows))
    for index, row in enumerate(rows[:-1]):
        if reverse:
            row = "".join(list(reversed(row)))
        string += str(index) + "|" + row + "\n"
    string += "  0  1  2  3  4"
    return string

def pretty_card(card,reverse=False):
    grid = [
        ["..","..","..","..",".."],
        ["..","..","..","..",".."],
        ["..","..","..","..",".."],
        ["..","..","..","..",".."],
        ["..","..","..","..",".."],
    ]
    grid[2][2] = "XX"
    for [x,y] in card["moves"]:
        grid[y+2][x+2] = "xx"
    string = ""
    if reverse:
        for row in list(reversed(grid)):
            string += ",".join(list(reversed(row))) + "\n"
    else:
        for row in grid:
            string += ",".join(row) + "\n"

    return string

def play():
    current_game = Game()
    try:
        while True:
            if current_game.current_team == game.Teams.Red:
                reverse = False
            else:
                reverse = True
            print(pretty_str(current_game, reverse))
            print('Current player: ' + current_game.current_team.value)
            #print('Current cards: ' + str(current_game.current_team_cards()))
            for name, card in current_game.current_team_cards().items():
                print("Card: " + name + "\n")
                print(pretty_card(card, reverse))
            start, card, end = get_move()
            try:
                current_game.move(start, end,  card)
            except MoveError as e:
                print(e.message)
            if current_game.gameover:
                print("Winner: " + current_game.current_team.value)
                break
    except KeyboardInterrupt:
        exit()

def get_move():
    while True:
        move = input("Move:").split(",")
        if len(move) != 5:
            print("Move must be in form 'from_x, from_y, card, to_x, to_y'")
            continue
        try:
            start = (int(move[0]), int(move[1]))
            end = (int(move[3]), int(move[4]))
        except ValueError:
            continue
        card = move[2]
        return start, card, end

if __name__ == "__main__":
    play()