import random
from collections import abc, Counter


class Card:
    # unicode symbols for suits
    suit_symbol = {'spades': chr(0x2660),
                   'diamonds': chr(0x2662),
                   'clubs': chr(0x2663),
                   'hearts': chr(0x2661)}

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


# convert rank to value
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


# convert value to rank
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


class HandOfCards:
    # hand_type = ('royal_flush',
    #              'straight_flush',
    #              'four_of_a_kind',
    #              'full_house',
    #              'flush',
    #              'straight',
    #              'three_of_a_kind',
    #              'two_pairs',
    #              'one_pair',
    #              'high_card')

    def __init__(self, card_list):
        if len(card_list) != 7:
            raise ValueError
        self._card_list = sorted(card_list, key=lambda s: convert(s.rank), reverse=True)
        self._rank_counter = Counter(card.rank for card in self._card_list)
        self.accepted_hands = []
        self.need_analysis = True

    def hand_analysis(self):
        # check for straight
        has_straight, active_straight = find_straight(self._card_list)
        if has_straight:
            self.accepted_hands.append(('straight', active_straight))

        # check for flush
        has_flush, active_flush = find_flush(self._card_list)
        if has_flush:
            self.accepted_hands.append(('flush', active_flush))

        # check for others
        self.accepted_hands.append(find_others(self._card_list))

        # check for straight flush
        if has_straight and has_flush:
            common_set = set(active_straight) & set(active_flush)
            if len(common_set) >= 5:
                best_hand = pick_cards_by_rank(common_set)
                self.accepted_hands.append(('straight_flush', common_set))
                # TODO: maybe separate royal straight flush out later.

    def best_hand(self):
        if self.need_analysis:
            self.hand_analysis()
            self.accepted_hands.sort()
            # TODO: need to adjust the sort parameters
            self.need_analysis = False
        return self.accepted_hands[0]

    def __str__(self):
        # TODO: figure the f-string out
        return f'{type(self).__name__} including the following cards: ({self._card_list})'

    def __repr__(self):
        return f'{type(self).__name__}({self._card_list})'


def find_flush(card_list):
    suit_counter = Counter(card.suit for card in card_list)
    most_common, count = suit_counter.most_common(1)[0]
    if count >= 5:
        active_flush = {card for card in card_list if card.suit == most_common}
        return True, active_flush
    return False, None


def has_ace(card_list):
    return 'A' in {card.rank for card in card_list}


def find_straight(card_list):
    straight_tail = 0
    to_test = set(convert(card.rank) for card in card_list)

    if has_ace(card_list):
        to_test = to_test | {1}
    for i in range(1, 11):
        test_set = set(range(i, i + 5))
        if test_set <= to_test:
            straight_tail = i + 4
    has_straight = straight_tail != 0

    if has_straight:
        straight_value_set = set(range(straight_tail - 4, straight_tail + 1))
        if 1 in straight_value_set:
            straight_value_set = straight_value_set | {14}
        active_hand = {card for card in card_list if convert(card.rank) in straight_value_set}
    else:
        active_hand = ()

    return has_straight, active_hand


def find_others(card_list):
    card_set = set(card_list)
    rank_counter = Counter(card.rank for card in card_list)
    common_3 = rank_counter.most_common(3)
    active_hand = {card for card in card_list if card.rank == common_3[0][0]}

    match [count for rank, count in common_3]:
        case [4, _] | [4, _, _]:
            hand_type = 'four_of_a_kind'
            left_out = card_set - active_hand
            active_hand |= set(pick_cards_by_rank(left_out, 1))
        case [3, 3, 1]:
            hand_type = 'full_house'
            active_hand |= {card for card in card_list if card.rank == common_3[1][0]}
            active_hand = set(pick_cards_by_rank(active_hand))
        case [3, 2, _]:
            hand_type = 'full_house'
            active_hand |= {card for card in card_list if card.rank == common_3[1][0]}
        case [3, 1, 1]:
            hand_type = 'three_of_a_kind'
            left_out = card_set - active_hand
            active_hand |= set(pick_cards_by_rank(left_out, 2))
        case [2, 2, 2]:
            hand_type = 'two_pairs'
            active_hand |= {card for card in card_list if card.rank == common_3[1][0]}
            active_hand |= {card for card in card_list if card.rank == common_3[2][0]}
            active_hand = set(pick_cards_by_rank(active_hand))
            # FIXME: there is bug here. May not get the right answer in some cases.
        case [2, 2, 1]:
            hand_type = 'two_pairs'
            active_hand |= {card for card in card_list if card.rank == common_3[1][0]}
            left_out = card_set - active_hand
            active_hand |= set(pick_cards_by_rank(left_out, 1))
        case [2, 1, 1]:
            hand_type = 'one_pair'
            left_out = card_set - active_hand
            active_hand |= set(pick_cards_by_rank(left_out, 3))
        case _:
            hand_type = 'high_card'
            active_hand = set(pick_cards_by_rank(card_list))

    return hand_type, active_hand


def pick_cards_by_rank(card_list, n=5):
    sorted_list = sorted(card_list, key=lambda card: convert(card.rank))
    return sorted_list[:n]


if __name__ == '__main__':
    # test Card class
    sample_card = Card('A', 'spades')
    print(sample_card)

    # test FrenchDeck class
    deck = FrenchDeck()
    # print(deck)

    # test HandOfCards class
    sample_cards = [Card('A', 'spades'),
                    Card('A', 'hearts'),
                    Card('A', 'clubs'),
                    Card('4', 'clubs'),
                    Card('5', 'clubs'),
                    Card('2', 'clubs'),
                    Card('3', 'clubs')]
    x = HandOfCards(sample_cards)
    print(x.best_hand())
