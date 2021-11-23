"""
Project:            mjb-battleships-2021
File:               sunk_ships.py
Created by:        Matt Barton V244576

Description:
user view to show a list of the sunk ships
Using array to make referencing simpler
"""
from breezypythongui import EasyCanvas, EasyFrame


class SunkShips(EasyFrame):

    def __init__(self, parent, _label, _background="lightblue"):

        # initialise list
        self.sunk_ship = []

        self.this_background = _background

        EasyFrame.__init__(self, parent, background=_background)
        self.sunk_ship_label = self.addLabel(text=_label, row=0, column=0, sticky='NSEW', background=self.this_background)
        # Prepare labels to hold ships as they are sunk
        self.sunk_ship.append(self.addLabel(text='', row=1, column=0, background=self.this_background))
        self.sunk_ship.append(self.addLabel(text='', row=2, column=0, background=self.this_background))
        self.sunk_ship.append(self.addLabel(text='', row=3, column=0, background=self.this_background))
        self.sunk_ship.append(self.addLabel(text='', row=5, column=0, background=self.this_background))
        self.sunk_ship.append(self.addLabel(text='', row=6, column=0, background=self.this_background))
        self.sunk_ship.append(self.addLabel(text='', row=7, column=0, background=self.this_background))
        self.sunk_ship.append(self.addLabel(text='', row=8, column=0, background=self.this_background))
        self.sunk_ship.append(self.addLabel(text='', row=9, column=0, background=self.this_background))
        self.sunk_ship.append(self.addLabel(text='', row=10, column=0, background=self.this_background))
