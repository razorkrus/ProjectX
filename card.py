import random
import logging
# import argparse
from collections import namedtuple, abc, Counter
from dataclasses import dataclass


# suit_symbol = {'spades': chr(0x2660),
#                'diamonds': chr(0x2662),
#                'clubs': chr(0x2663),
#                'hearts': chr(0x2661)}


class Card:
    symbol_list = [chr(0x2660+i) for i in range(4)]
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


class HandOfCards:
    def __init__(self, card_list):
        if len(card_list) < 5:
            raise ValueError
        self._card_list = list(card_list)
        self._rank_list = [card.rank for card in self._card_list]
        self._suit_list = [card.suit for card in self._card_list]
        self._rank_counter = Counter(self._rank_list)
        self._suit_counter = Counter(self._suit_list)
