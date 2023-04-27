import random
from collections import abc, Counter
from dataclasses import dataclass


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
        return f'[{self.suit_symbol[self.suit]} {self.rank}]'

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

    def deal(self, param):
        if isinstance(param, int):
            return [self._cards.pop() for _ in range(param)]
        elif isinstance(param, str):
            if param == 'all':
                return self._cards
            else:
                raise ValueError
        else:
            raise TypeError


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


weights = {'royal_flush': 10,
           'straight_flush': 9,
           'four_of_a_kind': 8,
           'full_house': 7,
           'flush': 6,
           'straight': 5,
           'three_of_a_kind': 4,
           'two_pairs': 3,
           'one_pair': 2,
           'high_card': 1}


@dataclass(frozen=True)
class Hand:
    type: str
    cards: set
    feature: tuple

    def __lt__(self, other):
        return self.feature < other.feature

    def __gt__(self, other):
        return self.feature > other.feature

    def __eq__(self, other):
        return self.feature == other.feature

    def __str__(self):
        return f'{self.type} with feature: {self.feature}'


class CardsOfPlayer:
    def __init__(self, card_list):
        if len(card_list) != 7:
            raise ValueError
        self._card_list = sorted(card_list, key=lambda s: convert(s.rank), reverse=True)
        self.accepted_hands = []
        self.need_analysis = True

    def perform_hand_analysis(self):
        # check for straight
        has_straight, active_straight, straight_tail = find_highest_straight(self._card_list)
        if has_straight:
            feature = (weights['straight'], straight_tail)
            hand = Hand('straight', active_straight, feature)
            self.accepted_hands.append(hand)

        # check for flush and straight flush
        has_flush, active_flush = find_flush(self._card_list)
        if has_flush:
            has_straight_flush, active_straight_flush, straight_tail = find_highest_straight(active_flush)
            if has_straight_flush:
                if straight_tail == 14:
                    feature = (weights['royal_flush'], 0)
                    hand = Hand('royal_flush', active_straight_flush, feature)
                    self.accepted_hands.append(hand)
                else:
                    feature = (weights['straight_flush'],
                               straight_tail)
                    hand = Hand('straight_flush', active_straight_flush, feature)
                    self.accepted_hands.append(hand)
            else:
                feature = (weights['flush'],
                           *(convert(card.rank) for card in active_flush))
                hand = Hand('flush', active_flush, feature)
                self.accepted_hands.append(hand)

        # check for others
        self.accepted_hands.append(Hand(*find_others(self._card_list)))

    def analyze_hand(self):
        if self.need_analysis:
            self.perform_hand_analysis()
            self.accepted_hands.sort(reverse=True)
            self.need_analysis = False

    def best_hand(self):
        self.analyze_hand()
        return self.accepted_hands[0]

    def show_all_hands(self):
        self.analyze_hand()
        for hand in self.accepted_hands:
            print(hand)
            print('Cards: ', '  '.join([str(card) for card in hand.cards]))

    def __str__(self):
        return f'{type(self).__name__} including the following cards: ' + \
            '  '.join([str(card) for card in self._card_list])

    def __repr__(self):
        return f'{type(self).__name__}({self._card_list})'


def find_flush(card_list):
    """Find the flush in the card list."""
    suit_counter = Counter(card.suit for card in card_list)
    most_common, count = suit_counter.most_common(1)[0]
    if count >= 5:
        active_flush = [card for card in card_list if card.suit == most_common]
        active_flush.sort(key=lambda s: convert(s.rank), reverse=True)
        return True, active_flush[:5]
    else:
        return False, None


def has_ace(card_list):
    return 'A' in {card.rank for card in card_list}


def find_highest_straight(card_list):
    """Find the highest straight in the card list."""
    straight_tail = 0
    to_test = set(convert(card.rank) for card in card_list)

    if has_ace(card_list):
        to_test = to_test | {1}
    for j in range(1, 11):
        test_set = set(range(j, j + 5))
        if test_set <= to_test:
            straight_tail = j + 4

    has_straight = straight_tail != 0

    active_hand = set()
    if has_straight:
        straight_value_set = set(range(straight_tail - 4, straight_tail + 1))
        if 1 in straight_value_set:
            straight_value_set = (straight_value_set - {1}) | {14}
        # active_hand = {card for card in card_list if convert(card.rank) in straight_value_set}
        for card in card_list:
            if convert(card.rank) in straight_value_set:
                active_hand.add(card)
                straight_value_set.remove(convert(card.rank))

    return has_straight, active_hand, straight_tail


def find_others(card_list):
    """
    Find other hands that are not straight or flush.
    Only works for 7 cards.
    """
    card_set = set(card_list)
    descending_cards = sorted(card_list, key=lambda s: convert(s.rank), reverse=True)
    rank_counter = Counter(card.rank for card in descending_cards)
    common_3 = rank_counter.most_common(3)

    # other hands are mainly constructed from the cards with the highest counts on rank,
    # which we will pick it first
    active_cards = {card for card in card_list if card.rank == common_3[0][0]}
    first_rank, second_rank = common_3[0][0], common_3[1][0]

    def expand_active_hand(pool=None):
        nonlocal active_cards, hand_feature
        hand_feature = [weights[hand_type]]
        hand_feature.extend([convert(first_rank)] * common_3[0][1])
        if hand_type == 'two_pairs':
            active_cards.update({card for card in card_list if card.rank == second_rank})
            hand_feature.extend([convert(second_rank)] * common_3[1][1])
        if len(active_cards) < 5:
            if pool is None:
                left_out = card_set - active_cards
            else:
                left_out = pool
            chosen = pick_cards_by_rank(left_out, 5 - len(active_cards))
            active_cards.update(chosen)
            hand_feature.extend([convert(card.rank) for card in chosen])

    match [count for rank, count in common_3]:
        case [4, _] | [4, _, _]:
            hand_type = 'four_of_a_kind'
            expand_active_hand()
        case [3, 3, 1] | [3, 2, 1]:
            hand_type = 'full_house'
            candidate_pool = {card for card in card_list if card.rank == second_rank}
            expand_active_hand(candidate_pool)
        case [3, 2, 2]:
            hand_type = 'full_house'
            expand_active_hand()
        case [3, 1, 1]:
            hand_type = 'three_of_a_kind'
            expand_active_hand()
        case [2, 2, _]:
            hand_type = 'two_pairs'
            expand_active_hand()
        case [2, 1, 1]:
            hand_type = 'one_pair'
            expand_active_hand()
        case _:
            hand_type = 'high_card'
            active_cards = set(descending_cards[:5])
            hand_feature = [weights[hand_type]]
            hand_feature.extend(convert(card.rank) for card in descending_cards[:5])

    return hand_type, active_cards, tuple(hand_feature)


def pick_cards_by_rank(card_list, n=5):
    sorted_list = sorted(card_list, key=lambda card: convert(card.rank), reverse=True)
    return sorted_list[:n]


if __name__ == '__main__':
    # test Card class
    sample_card = Card('A', 'spades')
    print(sample_card)

    # test CardsOfPlayer class
    sample_cards = [Card('A', 'spades'),
                    Card('A', 'hearts'),
                    Card('A', 'clubs'),
                    Card('4', 'clubs'),
                    Card('5', 'clubs'),
                    Card('2', 'clubs'),
                    Card('3', 'clubs')]
    x = CardsOfPlayer(sample_cards)
    print(x)
    print(x.best_hand())

    n = 100000
    type_log = []
    for i in range(n):
        deck = FrenchDeck()
        deck.shuffle()
        x = CardsOfPlayer(deck.deal(7))
        print(x)
        print(x.best_hand())
        type_log.append(x.best_hand().type)

    print(Counter(type_log))
