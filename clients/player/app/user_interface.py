"""
Project:            mjb-battleships-2021
File:               user_interface.py
Created by:        Matt Barton V244576

Description:
Interface for user to place ships and set attack targets

"""
import logging
from battlefield_ui import BattlefieldUI
from breezypythongui import EasyCanvas, EasyFrame
logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class UserControls(EasyFrame):
    """
    User controls to place ships and fire control

    """
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
    SHIP_FLEET = {
        'A': 1,
        'B': 1,
        'S': 3,
        'C': 1,
        'D': 2,
        'P': 2,
    }
    VALID_INPUT_X = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    VALID_INPUT_Y = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def __init__(self, parent, my_ui, opponent_ui, my_battlefield, opponent_battlefield, _background="lightblue"):
        """

        """
        self._parent = parent
        self._my_ui = my_ui
        self._my_battlefield = my_battlefield
        self._op_ui = opponent_ui
        self._op_battlefield = opponent_battlefield
        self.__ships = self.SHIPS.copy()
        self._docked_fleet = self.SHIP_FLEET.copy()
        self._deployed_fleet = dict.fromkeys(self.SHIP_FLEET, 0)
        self._my_turn = False
        self._fleet_deployed = False

        EasyFrame.__init__(self, parent, background=_background)

        self.deploy_label = self.addLabel(text='Deploy', row=1, column=1, columnspan=3, sticky='NSEW', background=_background)
        self.Deploy_Carrier = self.addButton(text='Carrier', row=2, column=1, columnspan=3,
                                             command=self._deploy_carrier)
        self.Deploy_Battle_Ship = self.addButton(text='Battle Ship', row=3, column=1, columnspan=3,
                                                 command=self._deploy_battle_ship)
        self.Deploy_Submarine = self.addButton(text='Submarine', row=4, column=1, columnspan=3,
                                               command=self._deploy_submarine)
        self.Deploy_Cruiser = self.addButton(text='Cruiser', row=5, column=1, columnspan=3,
                                             command=self._deploy_cruiser)
        self.Deploy_Destroyer = self.addButton(text='Destroyer', row=6, column=1, columnspan=3,
                                               command=self._deploy_destroyer)
        self.Deploy_Patrol_Boat = self.addButton(text='Patrol Boat', row=7, column=1, columnspan=3,
                                                 command=self._deploy_patrol_boat)

        self.addLabel(text='Docked', row=1, column=0, sticky='E', background=_background)

        self.Carrier_Docked = self.addIntegerField(value=self._docked_fleet['A'], row=2, column=0, width=5, sticky="E", state='disabled')
        self.Battle_Ship_Docked = self.addIntegerField(value=self._docked_fleet['B'], row=3, column=0, width=5, sticky="E", state='disabled')
        self.Submarine_Docked = self.addIntegerField(value=self._docked_fleet['S'], row=4, column=0, width=5, sticky="E", state='disabled')
        self.Cruiser_Docked = self.addIntegerField(value=self._docked_fleet['C'], row=5, column=0, width=5, sticky="E", state='disabled')
        self.Destroyer_Docked = self.addIntegerField(value=self._docked_fleet['D'], row=6, column=0, width=5, sticky="E", state='disabled')
        self.Patrol_Boat_Docked = self.addIntegerField(value=self._docked_fleet['P'], row=7, column=0, width=5, sticky="E", state='disabled')

        self.addLabel(text='Deployed', row=1, column=4, sticky='W', background=_background)
        self.Carrier_Deployed = self.addIntegerField(value=self._deployed_fleet['A'], row=2, column=4, width=5, sticky="W", state='disabled')
        self.Battle_Ship_Deployed = self.addIntegerField(value=self._deployed_fleet['B'], row=3, column=4, width=5, sticky="W", state='disabled')
        self.Submarine_Deployed = self.addIntegerField(value=self._deployed_fleet['S'], row=4, column=4, width=5, sticky="W", state='disabled')
        self.Cruiser_Deployed = self.addIntegerField(value=self._deployed_fleet['C'], row=5, column=4, width=5, sticky="W", state='disabled')
        self.Destroyer_Deployed = self.addIntegerField(value=self._deployed_fleet['D'], row=6, column=4, width=5, sticky="W", state='disabled')
        self.Patrol_Boat_Deployed = self.addIntegerField(value=self._deployed_fleet['P'], row=7, column=4, width=5, sticky="W", state='disabled')

        self.Deploy_Label = self.addLabel(text='Deploy to', row=8, column=0, columnspan=2, sticky="E", background=_background)
        self.Place_XY = self.addTextField(text="A1", row=8, column=2, columnspan=2, sticky="E")
        self.Horizontal_Check = self.addCheckbutton(text='Horizontal', row=8, column=4)
        self.Target_Label = self.addLabel(text='Targeting', row=9, column=0, columnspan=2, sticky="E", background=_background)
        self.Target_XY = self.addTextField(text="A1", row=9, column=2, columnspan=2, sticky="E", state="disabled")

        self.Message = self.addLabel(text='Choose Co-ordinates to Deploy', row=11, column=0, rowspan=3, columnspan=5,
                                     sticky='NSEW', background=_background)
        self.Title = self.addLabel(text='Fleet Control', row=0, column=0, columnspan=5, sticky='NSEW',
                                   background=_background)

        # set button widths
        self.Deploy_Carrier['width'] = 15
        self.Deploy_Battle_Ship['width'] = 15
        self.Deploy_Submarine['width'] = 15
        self.Deploy_Cruiser['width'] = 15
        self.Deploy_Destroyer['width'] = 15
        self.Deploy_Patrol_Boat['width'] = 15
        # change colours for checkbox and fire button
        self.Horizontal_Check['background'] = 'lightblue'
        # self.Fire_Button['background'] = 'red'

    def deploy_ship(self, ship, size):

        self.Message['text'] = ''
        vector = self.Place_XY.getText()
        horizontal = self.Horizontal_Check.isChecked()
        if vector is None or type(vector) is not str:
            raise ValueError('Parameter vector must be a string!')

        x, y = parse_vector(vector)
        #  x, y = vector[0], int(vector[1])

        if not any(valid_x in x for valid_x in self.VALID_INPUT_X):
            self.Message['text'] = 'Invalid X co-ordinate - Please Try Again!'
            return False
        elif not y > 0:
            self.Message['text'] = 'Invalid Y co-ordinate - Please Try Again!'
            return False
        elif not y <= 10:
            self.Message['text'] = 'Invalid Y co-ordinate - Please Try Again!'
            return False
        else:
            result = self._my_battlefield.place_ship(ship, x, y, size, horizontal=horizontal)
            if result is not None:
                for x, y in result:
                    self._my_ui.update_at(x, y, ship)
                    logger.info(f"Deployed - {ship} at {x}, {y} ")
                return True
            else:
                return False

    def _deploy_carrier(self):
        ship = 'A'
        if self._docked_fleet[ship] > 0:
            size = self.__ships[ship]
            if self.deploy_ship(ship, size):
                self.Place_XY.setText('')
                self._docked_fleet[ship] -= 1
                self._deployed_fleet[ship] += 1
                self.Carrier_Docked.setValue(self._docked_fleet[ship])
                self.Carrier_Deployed.setValue(self._deployed_fleet[ship])
                self.Message['text'] = "Deployment Successful"
                if self.check_all_deployed():

                    self.Message['text'] = "Your Fleet is Deployed - Prepare to Fire!"
            else:
                msg = self.Message.cget('text')
                self.Message['text'] = f'{msg} Not Deployed'

        else:
            self.Message['text'] = "Already Deployed"

    def _deploy_battle_ship(self):
        ship = 'B'
        if self._docked_fleet[ship] > 0:
            size = self.__ships[ship]
            if self.deploy_ship(ship, size):
                self.Place_XY.setText('')
                self._docked_fleet[ship] -= 1
                self._deployed_fleet[ship] += 1
                self.Battle_Ship_Docked.setValue(self._docked_fleet[ship])
                self.Battle_Ship_Deployed.setValue(self._deployed_fleet[ship])
                self.Message['text'] = "Deployment Successful"
                if self.check_all_deployed():
                    self.Message['text'] = "Your Fleet is Deployed - Prepare to Fire!"
            else:
                msg = self.Message.cget('text')
                self.Message['text'] = f'{msg} Not Deployed'
        else:
            self.Message['text'] = "Already Deployed"

    def _deploy_submarine(self):
        """
        There are three submarines
        To be able to tell if they are sunk we need to have a different symbol for each
        So current deployed/docked quantities are used to choose the symbol to place
        """
        ship = 'S'
        if self._docked_fleet[ship] > 0:
            if self._docked_fleet[ship] == 2:
                _ship = 's'
            elif self._docked_fleet[ship] == 1:
                _ship = '5'
            else:
                _ship = 'S'
            size = self.__ships[ship]
            if self.deploy_ship(_ship, size):
                self.Place_XY.setText('')
                self._docked_fleet[ship] -= 1
                self._deployed_fleet[ship] += 1
                self.Submarine_Docked.setValue(self._docked_fleet[ship])
                self.Submarine_Deployed.setValue(self._deployed_fleet[ship])
                self.Message['text'] = "Deployment Successful"
                if self.check_all_deployed():
                    self.Message['text'] = "Your Fleet is Deployed - Prepare to Fire!"
            else:
                msg = self.Message.cget('text')
                self.Message['text'] = f'{msg} Not Deployed'
        else:
            self.Message['text'] = "Already Deployed"

    def _deploy_cruiser(self):
        ship = 'C'
        if self._docked_fleet[ship] > 0:
            size = self.__ships[ship]
            if self.deploy_ship(ship, size):
                self.Place_XY.setText('')
                self._docked_fleet[ship] -= 1
                self._deployed_fleet[ship] += 1
                self.Cruiser_Docked.setValue(self._docked_fleet[ship])
                self.Cruiser_Deployed.setValue(self._deployed_fleet[ship])
                self.Message['text'] = "Deployment Successful"
                if self.check_all_deployed():
                    self.Message['text'] = "Your Fleet is Deployed - Prepare to Fire!"
            else:
                msg = self.Message.cget('text')
                self.Message['text'] = f'{msg} Not Deployed'
        else:
            self.Message['text'] = "Already Deployed"

    def _deploy_destroyer(self):
        """
        There are two destroyers
        To be able to tell if they are sunk we need to have a different symbol for each
        So current deployed/docked quantities are used to choose the symbol to place
        """
        ship = 'D'
        if self._docked_fleet[ship] > 0:
            if self._docked_fleet[ship] == 1:
                _ship = 'd'
            else:
                _ship = 'D'
            size = self.__ships[ship]
            if self.deploy_ship(_ship, size):
                self.Place_XY.setText('')
                self._docked_fleet[ship] -= 1
                self._deployed_fleet[ship] += 1
                self.Destroyer_Docked.setValue(self._docked_fleet[ship])
                self.Destroyer_Deployed.setValue(self._deployed_fleet[ship])
                self.Message['text'] = "Deployment Successful"
                if self.check_all_deployed():
                    self.Message['text'] = "Your Fleet is Deployed - Prepare to Fire!"
            else:
                msg = self.Message.cget('text')
                self.Message['text'] = f'{msg} Not Deployed'
        else:
            self.Message['text'] = "Already Deployed"

    def _deploy_patrol_boat(self):
        """
        There are two patrol boats
        To be able to tell if they are sunk we need to have a different symbol for each
        So current deployed/docked quantities are used to choose the symbol to place
        """
        ship = 'P'
        if self._docked_fleet[ship] > 0:
            if self._docked_fleet[ship] == 1:
                _ship = 'p'
            else:
                _ship = 'P'
            size = self.__ships[ship]
            if self.deploy_ship(_ship, size):
                self.Place_XY.setText('')
                self._docked_fleet[ship] -= 1
                self._deployed_fleet[ship] += 1
                self.Patrol_Boat_Docked.setValue(self._docked_fleet[ship])
                self.Patrol_Boat_Deployed.setValue(self._deployed_fleet[ship])
                self.Message['text'] = "Deployment Successful"
                if self.check_all_deployed():
                    self.Message['text'] = "Your Fleet is Deployed - Prepare to Fire!"
            else:
                msg = self.Message.cget('text')
                self.Message['text'] = f'{msg} Not Deployed'
        else:
            self.Message['text'] = "Already Deployed"

    def check_all_deployed(self):
        docked_fleet = self._docked_fleet
        all_deployed = True
        for key in docked_fleet:
            if docked_fleet[key] > 0:
                all_deployed = False
                break
        if all_deployed:
            self.Place_XY['state'] = 'disabled'
            self.Target_XY['state'] = 'normal'
            self._fleet_deployed = True
            self.deploy_label['text'] = 'Fleet Deployed'
            if self._my_turn:
                self._parent.start_my_turn()

        return all_deployed

    @property
    def fleet_deployed(self):
        return self._fleet_deployed


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
