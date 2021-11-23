"""
Project:            mjb-battleships-2021
File:               client_interface.py
Modified by:        Matt Barton V244576

Description:
Interface for communications to server
need to send if ship is sunk and if so which ship type
"""
from abc import abstractmethod


class ClientInterface:
    @abstractmethod
    def add_event_listener(self, event=None, handler=None):
        pass

    @abstractmethod
    def join(self):
        pass

    @abstractmethod
    def attack(self, vector):
        pass

    @abstractmethod
    def hit(self):
        pass

    @abstractmethod
    def miss(self):
        pass

    @abstractmethod
    def defeat(self):
        pass

    @abstractmethod
    def sunk(self, ship):
        pass
