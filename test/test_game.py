import unittest
from board_game.api import game

class TestGameSetup(unittest.TestCase):

    def test_duplicate_cards(self):
        self.assertRaises(Exception, game.Game, red_cards=["tiger", "tiger"])
        self.assertRaises(Exception, game.Game, blue_cards=["boar", "boar"])
        self.assertRaises(Exception, game.Game, spare_card="boar", blue_cards=["boar", "mantis"])
        self.assertRaises(Exception, game.Game, spare_card="boar", red_cards=["boar", "mantis"])
        self.assertRaises(Exception, game.Game, red_cards=["tiger", "crab"], blue_cards=["monkey", "tiger"])

    def test_valid_input(self):
        game.Game()
        game.Game(red_cards=["tiger", "crab"], blue_cards=["monkey", "mantis"])
        game.Game(blue_cards=["monkey", "mantis"], spare_card="boar")
        game.Game(red_cards=["tiger", "crab"], spare_card="boar")
        game.Game(red_cards=["tiger", "crab"], blue_cards=["monkey", "mantis"], spare_card="boar")

    def test_invalid_cards(self):
        self.assertRaises(Exception, game.Game, red_cards=["tidger", "crab"])
        self.assertRaises(Exception, game.Game, blue_cards=["tidger", "crab"])
        self.assertRaises(Exception, game.Game, spare_card="tidger")       

    def test_wrong_amount(self):
        self.assertRaises(Exception, game.Game, red_cards=["tiger", "mantis", "boar"])
        self.assertRaises(Exception, game.Game, blue_cards=["tiger", "mantis", "boar"])
        self.assertRaises(Exception, game.Game, spare_card=["tiger", "mantis"])

        self.assertRaises(Exception, game.Game, red_cards=["tiger"])
        self.assertRaises(Exception, game.Game, blue_cards=["tiger"])

def does_state_match(state1, state2):
    if str(state1) != state2:
        print("Gamestate:")
        print(state1)
        print("Expected:")
        print(state2)
        return False
    return True

class TestStateString(unittest.TestCase):
    def test_to_string(self):
        expected = "\
rp,rp,rk,rp,rp,\n\
..,..,..,..,..,\n\
..,..,..,..,..,\n\
..,..,..,..,..,\n\
bp,bp,bk,bp,bp,\n"
        myGame = game.Game()
        if not does_state_match(myGame, expected):
            self.fail("game.state was wrong")

    def test_from_string(self):
        expected = "\
rp,rp,rk,rp,rp,\n\
..,..,..,..,..,\n\
..,..,..,..,..,\n\
..,..,..,..,..,\n\
bp,bp,bk,bp,bp,\n"
        state = game.Game.state_from_string(expected)
        myGame = game.Game(start_state=state)
        if not does_state_match(myGame, expected):
            self.fail("game.state was wrong")
        expected = "\
rp,rp,TT,rp,rp,\n\
..,..,..,..,..,\n\
..,..,rk,..,..,\n\
..,..,..,bk,..,\n\
bp,bp,TT,bp,bp,\n"
        state = game.Game.state_from_string(expected)
        myGame = game.Game(start_state=state)
        if not does_state_match(myGame, expected):
            self.fail("game.state was wrong")


class TestMoves(unittest.TestCase):

    def test_tiger(self):
        myGame = game.Game(red_cards=["tiger",  "mantis"], spare_card="dragon")
        myGame.move([0,0], [0,2], "tiger")
        expected = "\
..,rp,rk,rp,rp,\n\
..,..,..,..,..,\n\
rp,..,..,..,..,\n\
..,..,..,..,..,\n\
bp,bp,bk,bp,bp,\n"
        if not does_state_match(myGame, expected):
            self.fail("game.state was wrong")
        myGame = game.Game(red_cards=["tiger",  "mantis"], spare_card="dragon")
        myGame.unchecked_move([0,0], [0,2])
        myGame.relative_move([0,2], [0,-1], "tiger")
        expected = "\
..,rp,rk,rp,rp,\n\
rp,..,..,..,..,\n\
..,..,..,..,..,\n\
..,..,..,..,..,\n\
bp,bp,bk,bp,bp,\n"
        if not does_state_match(myGame, expected):
            self.fail("game.state was wrong")
        myGame = game.Game(blue_cards=["tiger",  "mantis"], spare_card="crane")
        myGame.relative_move([3,4], [0,-2], "tiger")
        expected = "\
rp,rp,rk,rp,rp,\n\
..,..,..,..,..,\n\
..,..,..,bp,..,\n\
..,..,..,..,..,\n\
bp,bp,bk,..,bp,\n"
        if not does_state_match(myGame, expected):
            self.fail("game.state was wrong")
        myGame = game.Game(blue_cards=["tiger",  "mantis"], spare_card="crane")
        myGame.unchecked_move([3,4], [3,2])
        myGame.relative_move([3,2], [0,1], "tiger")
        expected = "\
rp,rp,rk,rp,rp,\n\
..,..,..,..,..,\n\
..,..,..,..,..,\n\
..,..,..,bp,..,\n\
bp,bp,bk,..,bp,\n"
        if not does_state_match(myGame, expected):
            self.fail("game.state was wrong")

        myGame = game.Game(blue_cards=["tiger",  "mantis"], spare_card="crane")
        self.assertRaises(Exception, myGame.relative_move, [3,2], [0,-3], "tiger")


class TestEnd(unittest.TestCase):
    def test_way_of_stream(self):
        expected = "\
rp,rp,TT,rp,rp,\n\
..,..,..,..,..,\n\
..,bk,..,..,..,\n\
..,..,rk,..,..,\n\
bp,bp,TT,bp,bp,\n"
        state = game.Game.state_from_string(expected)
        myGame = game.Game(red_cards=["boar", "tiger"], spare_card="dragon", start_state=state)
        myGame.move([2,3], [2,4], "boar")
        if not myGame.gameover or myGame.winningMethod != "Way of the stream":
            self.fail("\n" + str(myGame) + "\nRed should of one by Way of the Stream, gameover: " + str(myGame.gameover) + ", method: " + str(myGame.winningMethod))
        expected = "\
rp,rp,TT,rp,rp,\n\
..,..,bk,..,..,\n\
..,rk,..,..,..,\n\
..,..,..,..,..,\n\
bp,bp,bp,..,bp,\n"
        state = game.Game.state_from_string(expected)
        myGame = game.Game(blue_cards=["boar", "tiger"], spare_card="goose", start_state=state)
        myGame.move([2,1], [2,0], "boar")
        if not myGame.gameover or myGame.winningMethod != "Way of the stream":
            self.fail("\n" + str(myGame) + "\nBlue should of one by Way of the Stream, gameover: " + str(myGame.gameover) + ", method: " + str(myGame.winningMethod))


    def test_way_of_stone(self):
        expected = "\
rp,rp,TT,rp,rp,\n\
..,..,rk,..,..,\n\
..,bk,..,..,..,\n\
..,..,..,..,..,\n\
bp,bp,TT,bp,bp,\n"
        state = game.Game.state_from_string(expected)
        myGame = game.Game(red_cards=["monkey", "tiger"], spare_card="dragon", start_state=state)
        myGame.move([2,1], [1,2], "monkey")
        if not myGame.gameover or myGame.winningMethod != "Way of the stone":
            self.fail("\n" + str(myGame) + "\nRed should of one by Way of the Stone, gameover: " + str(myGame.gameover) + ", method: " + str(myGame.winningMethod))
        expected = "\
rp,rp,TT,rp,rp,\n\
..,..,rk,..,..,\n\
..,bk,..,..,..,\n\
..,..,..,..,..,\n\
bp,bp,TT,bp,bp,\n"
        state = game.Game.state_from_string(expected)
        myGame = game.Game(blue_cards=["monkey", "tiger"], spare_card="goose", start_state=state)
        myGame.move([1,2], [2,1], "monkey")
        if not myGame.gameover or myGame.winningMethod != "Way of the stone":
            self.fail("\n" + str(myGame) + "\nBlue should of one by Way of the Stone, gameover: " + str(myGame.gameover) + ", method: " + str(myGame.winningMethod))

if __name__ == '__main__':
    unittest.main()