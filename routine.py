import time
from collections import deque

from card import FrenchDeck


class Player:
    """
    Player's name should be unique across platform.
    And Player do not need to deal with account verification details.
    It should be left to the verification system.
    Player's instance should be created only after verification, and could be recycled after player quits.
    """
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        # FIXME: make player's balance non-negative

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def replenish(self, value):
        self.balance_change(value)

    def cash_out(self, value):
        self.balance_change(-value)

    def balance_change(self, value):
        try:
            self.balance += value
        except ValueError:
            raise ValueError


class Seat:
    def __init__(self, table, number):
        self.table = table
        self.number = number

        self.player = None
        self.chips = 0
        self.active = False
        # TODO: violating the DRY rule, still trying to find a way to circumvent the warning

    def clear_seat(self):
        self.player = None
        self.chips = 0
        self.active = False

    def add_player(self, player, chips, active=True):
        self.player = player
        self.chips = chips
        self.active = active

    def rm_player(self):
        if self.player is None:
            raise ValueError
        self.player.balance_change(self.chips)
        self.clear_seat()

    def bet(self, amount):
        pass


class Table:
    def __init__(self, name, password, max_player=9, sb=5, chips=1000, private=False):
        self.name = name
        self.password = password
        self.max_player = max_player
        self.private = private
        self.sb = sb
        self.initial_chips = chips
        self.seats = [Seat(self, i) for i in range(self.max_player)]

    def add_player(self, player, chips, position):
        self.seats[position].add_player(player, chips)

    def rm_player(self, player, position):
        self.seats[position].rm_player()

    def make_deque(self, sb_position):
        return 1

    def game_start(self):
        """
        Should I put the player status check inside this function?
        And how do I keep a record of each players' status?
        Maybe I should implement the hash method of Player class first.

        Keep it simple. Just deal with the main routine of game please.
        :return: None
        """
        # game_dq = deque()
        game_dq = self.make_deque()
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

    def clear_table(self):
        pass

    def run(self, sleep_time=3, recycle_time=300):
        idle_count = 0
        while True:
            seat_not_empty = [seat.player is not None for seat in self.seats]
            if any(seat_not_empty):
                idle_count = 0
                if sum(seat_not_empty) > 1:
                    self.game_start()
                else:
                    time.sleep(sleep_time)
            else:
                if idle_count > recycle_time:
                    self.clear_table()
                else:
                    idle_count += sleep_time
                    time.sleep(sleep_time)
