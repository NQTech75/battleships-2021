import logging
import os
import random
import time
from breezypythongui import EasyFrame
from battlefield import Battlefield
from battlefield_ui import BattlefieldUI
from battleship_client import BattleshipClient
from user_interface import UserControls
from sunk_ships import SunkShips
from playsound import playsound

# Without this, nothing shows up...
logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

grpc_host = os.getenv('GRPC_HOST', 'localhost')
grpc_port = os.getenv('GRPC_PORT', '50051')


class Game(EasyFrame):
    SIZE = 10
    SHIPS = {
        'A': 5, 'B': 4, 'S': 3, 's': 3, '5': 3,
        'C': 3, 'D': 2, 'd': 2, 'P': 1, 'p': 1,
    }

    SHIP_NAMES = {
        'A': 'Aircraft Carrier',
        'B': 'Battleship',
        'S': 'Submarine', 's': 'Submarine', '5': 'Submarine',
        'C': 'Cruiser',
        'D': 'Destroyer', 'd': 'Destroyer',
        'P': 'Patrol Boat', 'p': 'Patrol Boat',
    }
    VALID_INPUT_X = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']

    def __init__(self, timeout=1.0, mirrored=False, vertical=False, smart_ai=False):
        EasyFrame.__init__(self, background='lightgrey')

        self.__smart_ai = smart_ai

        # Get a copy of the ships
        self.__ships = self.SHIPS.copy()
        self.__fleet_deployed = False
        self.__my_turn = False
        self.__mine = Battlefield(colour=193)
        self.__opponent = Battlefield(colour=208)

        self.__mine_ui = BattlefieldUI(self, width=350, height=350, size=self.SIZE)
        self.__opponent_ui = BattlefieldUI(self, width=350, height=350, size=self.SIZE,
                                           colour='lightgreen')
        self.__user_controls = UserControls(self, self.__mine_ui, self.__opponent_ui, self.__mine, self.__opponent)

        # number of sunk ships to use for array
        self.__mine_sunk_count = 0
        self.__opponent_sunk_count = 0
        # user view to show sunk ships
        self.__mine_sunk = SunkShips(self, 'Our Grave Yard')
        self.__opponent_sunk = SunkShips(self, 'Our Victory Board', 'lightgreen')

        # add to overlay
        self.addCanvas(self.__opponent_ui, row=0, column=0)
        self.addCanvas(self.__mine_ui, row=0, column=1)
        self.addCanvas(self.__user_controls, row=0, column=1, columnspan=2)

        # add sunk ships overviews
        self.addCanvas(self.__opponent_sunk, row=0, column=3)
        self.addCanvas(self.__mine_sunk, row=0, column=4)

        # set fire button
        self.__fire_button = self.addButton(text='    ', row=0, column=2, command=self.__attack_cell, state='disabled')
        self.__fire_button['background'] = 'lightblue'
        font = ('Helvetica', 28, 'bold')
        self.__fire_button['font'] = font

        self.__timeout = abs(timeout)
        self.__attack_vector = None, None

        self.__client = self.__create_grpc_client()
        self.__client.join()

    def __create_grpc_client(self):
        """
        Create BattleshipClient that communicates with Game Server.
        """
        client = BattleshipClient(grpc_host=grpc_host, grpc_port=grpc_port)

        # Assign event handlers
        client.add_event_listener('begin', self.begin)
        client.add_event_listener('start_turn', self.start_my_turn)
        client.add_event_listener('end_turn', self.end_my_turn)
        client.add_event_listener('hit', self.hit)
        client.add_event_listener('miss', self.miss)
        client.add_event_listener('win', self.won)
        client.add_event_listener('lose', self.lost)
        client.add_event_listener('attack', self.attacked)
        client.add_event_listener('sunk', self.sunk)
        return client

    def clear(self):
        """
        Clear all data related to the game so we can start a new game.
        """
        self.__mine.clear()
        self.__mine_ui.clear()

        self.__opponent.clear()
        self.__opponent_ui.clear()

    def start(self):
        self.mainloop()

    def begin(self):
        logger.info("The game has started!")

    def start_my_turn(self):
        self.__my_turn = True
        self.__user_controls._my_turn = True
        if not self.__user_controls.fleet_deployed:
            self.__user_controls.Message['text'] = 'Deploy your fleet - you fire first!'
        else:
            logger.info("Okay, it's my turn now.")
            time.sleep(self.__timeout)
            self.__user_controls.Message['text'] = 'Your Turn to Fire-------!'
            self.__fire_button['state'] = 'normal'
            self.__fire_button['background'] = 'red'
            self.__fire_button['text'] = 'Fire'

    def __attack_cell(self):
        """
        Attack the opponent at location ({col}, {row}).
        """
        vector = self.__user_controls.Target_XY.getText()
        if vector is None or type(vector) is not str:
            raise ValueError('Parameter vector must be a string!')
        x, y = parse_vector(vector)
        # x, y = vector[0], int(vector[1])

        if not any(valid_x in x for valid_x in self.VALID_INPUT_X):
            self.__user_controls.Message['text'] = 'Invalid X co-ordinate - Please Try Again!'
        elif not y > 0:
            self.__user_controls.Message['text'] = 'Invalid Y co-ordinate - Please Try Again!'
        elif not y < 10:
            self.__user_controls.Message['text'] = 'Invalid Y co-ordinate - Please Try Again!'
        else:
            col, row = self.__mine.from_coords(x, y)
            self.__attack_vector = col, row
            vector = f'{x}{y}'
            logger.info(f'Attacking on {vector}.')
            self.__client.attack(vector)
            self.__user_controls.Target_XY.setText('')

    def end_my_turn(self):
        self.__my_turn = False
        logger.info("Okay, my turn has ended.")
        self.__fire_button['state'] = 'disabled'
        self.__fire_button['background'] = 'lightblue'
        self.__fire_button['text'] = ''
        self.__user_controls.Message['text'] = 'Prepare for Incoming - Opponents Turn!'

    def hit(self):
        logger.info("Success!")
        self.__opponent.set_by_col_row(*self.__attack_vector, 'X')
        self.__opponent_ui.update_at(*self.__attack_vector, '\u2716', colour='red')
        self.__user_controls.Message['text'] = 'You Got a Hit!'
        # playsound(os.path.abspath('./sounds/hit.mp3'))

    def miss(self):
        logger.info("No luck.")
        dot = '\u25CB'
        self.__opponent.set_by_col_row(*self.__attack_vector, dot)
        self.__opponent_ui.update_at(*self.__attack_vector, dot, colour='blue')
        self.__user_controls.Message['text'] = 'You Missed!'
        # playsound(os.path.abspath('./sounds/miss.mp3'))

    def won(self):
        logger.info("I won!!!")
        self.__user_controls.Message['text'] = 'You Won!'

    def lost(self):
        logger.info("Meh. I lost.")
        self.__user_controls.Message['text'] = 'You Lost - Game Over'
        # playsound(os.path.abspath('./sounds/defeat.mp3'))

    def attacked(self, vector):
        # Get rid of any whitespace
        vector = vector.strip()

        logger.info(f"Oi! Getting attacked on {vector}")
        
        x, y = vector[0], int(vector[1:])
        cell = self.__mine.get(x, y)
        col, row = self.__mine.from_coords(x, y)
        if cell is None:
            self.__client.miss()
            self.__mine.set(x, y, 'O')
            self.__mine_ui.update_at(col, row, '\u25CB', colour='blue')
        elif cell == '@':
            logger.info('THIS SHOULD NOT HAPPEN!')  # Voiceover: "it happened."
            self.__client.miss()
        elif cell == 'X':
            self.__client.miss()
        elif cell == 'O':
            self.__client.miss()
        else:
            logger.info("I'm hit!")
            self.__mine.set(x, y, 'X')
            # col, row = self.__mine.from_coords(x, y)
            self.__mine_ui.update_at(col, row, '\u2716', colour='red')
            self.__ships[cell] -= 1
            if self.__ships[cell] == 0:
                if cell in self.SHIP_NAMES:
                    sunk_ship = self.SHIP_NAMES[cell]
                    logger.info(f'Sunk {sunk_ship}!')
                    self.__user_controls.Message['text'] = f'They Sunk Our {sunk_ship}!'
                    self.__client.sunk(sunk_ship)
                    self.__mine_sunk.sunk_ship[self.__mine_sunk_count]['text'] = sunk_ship
                    self.__mine_sunk_count += 1
                del self.__ships[cell]

            if not self.__ships:
                self.__client.defeat()
            else:
                self.__client.hit()

    def sunk(self, ship):
        sunk_ship = self.SHIP_NAMES[ship]
        logger.info(f'We Sunk their {sunk_ship}')
        self.__opponent.set_by_col_row(*self.__attack_vector, 'X')
        self.__opponent_ui.update_at(*self.__attack_vector, '\u2716', colour='red')
        self.__user_controls.Message['text'] = f'We Sunk their {sunk_ship}'
        self.__opponent_sunk.sunk_ship[self.__opponent_sunk_count]['text'] = sunk_ship
        self.__opponent_sunk_count += 1


def parse_vector(vector):
    """
    Parses vector to X = ( A - J)
                    Y = 1 or greater
    """
    # x is str so easy
    x = vector[0]
    # initialise y
    y = 0
    # get rest of vector input - remove first character
    y_str = vector[1::]
    # use try as it might not be an integer
    try:
        y = int(y_str)
    except ValueError as verr:
        logger.info(f'Value Error occurred trying to convert ot int- {verr}')

    except Exception as exerr:
        logger.info(f'Exception occurred trying to convert to int {exerr}')

    return x, y


def main():
    mirrored = os.getenv('MIRRORED', False)
    vertical = os.getenv('VERTICAL', False)
    smart_ai = os.getenv('SMART_AI', False)

    game = Game(timeout=0.25, mirrored=mirrored, vertical=vertical, smart_ai=smart_ai)
    # game.setup()
    game.start()


if __name__ == '__main__':
    main()


