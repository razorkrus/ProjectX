import random
import logging
# import argparse
from collections import namedtuple, abc, Counter
from functools import partial
from dataclasses import dataclass


# suit_symbol = {'spades': chr(0x2660),
#                'diamonds': chr(0x2662),
#                'clubs': chr(0x2663),
#                'hearts': chr(0x2661)}


class Card:
    symbol_list = [chr(0x2660 + i) for i in range(4)]
    suit_list = 'spades hearts diamonds clubs'.split()
    suit_symbol = dict(zip(suit_list, symbol_list))

    def __init__(self, rank, suit):
        self.rank: str = rank
        self.suit: str = suit

    def __str__(self):
        return f'{self.suit_symbol[self.suit]} {self.rank}'

    def __repr__(self):
        class_name = type(self).__name__
        return f'{class_name}(rank={self.rank}, suit={self.suit})'


class FrenchDeck(abc.MutableSequence):
    ranks = [str(i) for i in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits
                       for rank in self.ranks]
        self._randomizer = random.SystemRandom()

    def __getitem__(self, position):
        return self._cards[position]

    def __setitem__(self, position, value):
        self._cards[position] = value

    def __delitem__(self, position):
        del self._cards[position]

    def __len__(self):
        return len(self._cards)

    def __str__(self):
        pass

    def insert(self, index: int, value) -> None:
        self._cards.insert(index, value)

    def shuffle(self):
        self._randomizer.shuffle(self._cards)


def convert(rank, ace=True):
    match rank:
        case 'A':
            return 14 if ace else 1
        case 'K':
            return 13
        case 'Q':
            return 12
        case 'J':
            return 11
        case _:
            return int(rank)


def convert_back(value):
    match value:
        case 14:
            return 'A'
        case 13:
            return 'K'
        case 12:
            return 'Q'
        case 11:
            return 'J'
        case _:
            return str(value)


convert1 = partial(convert, ace=False)


class HandOfCards:
    hand_type = ('royal_flush straight_flush four_of_a_kind full_house '
                 'flush straight three_of_a_kind two_pairs one_pair high_card').split()

    def __init__(self, card_list):
        if len(card_list) != 7:
            raise ValueError
        self._card_list = sorted(card_list, key=lambda s: convert(s.rank), reverse=True)
        self._rank_counter = Counter(card.rank for card in self._card_list).most_common(3)
        self._suit_counter = Counter(card.suit for card in self._card_list).most_common(1)
        self.type = dict.fromkeys(self.hand_type, value=False)
        self.set_type()

    def set_type(self):
        has_straight, straight_tail = self.find_straight()
        if has_straight:
            straight_tail = convert_back(straight_tail)
            self.type['straight'] = True
        if self._suit_counter[0][1] >= 5:
            self.type['flush'] = True
        match [v for _, v in self._rank_counter]:
            case [4, _] | [4, _, _]:
                self.type['four_of_a_kind'] = True
            case [3, 3, 1] | [3, 2, _]:
                self.type['full_house'] = True
            case [3, 1, 1]:
                self.type['three_of_a_kind'] = True
            case [2, 2, _]:
                self.type['two_pairs'] = True
            case [2, 1, 1]:
                self.type['one_pair'] = True
            case _:
                self.type['high_card'] = True

    def has_ace(self):
        return 'A' in {card.rank for card in self._card_list}

    def find_straight(self):
        straight_tail = 0
        to_test = set(convert(card.rank) for card in self._card_list)
        if self.has_ace():
            to_test = to_test | {1}
        for i in range(1, 11):
            test_set = set(range(i, i + 5))
            if test_set <= to_test:
                straight_tail = i + 4
        return straight_tail != 0, straight_tail


if __name__ == '__main__':
    x = HandOfCards(
        [Card('A', 'spades'), Card('A', 'hearts'), Card('A', 'clubs'), Card('4', 'clubs'), Card('5', 'clubs'),
         Card('2', 'clubs'), Card('3', 'clubs')])
    print(x.type)
