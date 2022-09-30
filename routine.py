import time
from collections import deque

from card import FrenchDeck


class Table:
    def __init__(self, name, password, max_player=9, private=False):
        self.name = name
        self.password = password
        self.max_player = max_player
        self.private = False
        self.player_set = set()

    def add_player(self, player):
        self.player_set.add(player)

    def remove_player(self, player):
        self.player_set.remove(player)

    def game_start(self):
        pass

    def clear(self):
        pass

    def run(self, probe_time=3, recycle_time=300):
        idle_count = 0
        while True:
            if self.player_set:
                idle_count = 0
                if len(self.player_set) > 1:
                    self.game_start()
                else:
                    time.sleep(probe_time)
            else:
                if idle_count > recycle_time:
                    self.clear()
                else:
                    idle_count += probe_time
                    time.sleep(probe_time)










