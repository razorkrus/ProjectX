import time
from collections import deque

from card import FrenchDeck


class Player:
    def __init__(self, name, password, balance):
        self.name = name
        self.password = password
        self.balance = balance

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def replenish(self, value):
        pass

    def cash_out(self, value):
        pass


class Table:
    def __init__(self, name, password, max_player=9, sb=5, chips=1000, private=False):
        self.name = name
        self.password = password
        self.max_player = max_player
        self.private = private
        self.sb = sb
        self.initial_chips = chips
        # self.player_set = set()
        self.seat_status = dict.fromkeys(range(max_player), value=False)

    def add_player(self, player, chips, position):
        self.seat_status[position] = [player, chips]
        # self.player_set.add(player)

    def remove_player(self, player, position):
        # self.player_set.remove(player)

    def game_start(self):
        """
        Should I put the player status check inside this function?
        And how do I keep a record of each players' status?
        Maybe I should implement the hash method of Player class first.

        Keep it simple. Just deal with the main routine of game please.
        :return: None
        """
        game_dq = deque()
        rounds = 'pre_flop flop turn river'.split()

        for r in rounds:
            if r == 'pre_flop':
                game_dq.rotate(2)
                self.bet_round(game_dq)
            elif r == 'flop':
                game_dq.rotate(-2)
                self.bet_round(game_dq)
            else:
                self.bet_round(game_dq)

    def bet_round(self, dq):
        pass

    def clear(self):
        pass

    def run(self, sleep_time=3, recycle_time=300):
        idle_count = 0
        while True:
            if self.player_set:
                idle_count = 0
                if len(self.player_set) > 1:
                    self.game_start()
                else:
                    time.sleep(sleep_time)
            else:
                if idle_count > recycle_time:
                    self.clear()
                else:
                    idle_count += sleep_time
                    time.sleep(sleep_time)
