#!/usr/local/bin/python3
from enum import IntEnum
from collections import Counter
from numpy import array, logspace, int32
from random import choice
from copy import deepcopy


class Card(IntEnum):
    '''A Card. Don't overthink it.'''
    nine = 1
    ten = 2
    jack = 3
    queen = 4
    king = 5
    ace = 6


class Hand:
    '''A hand. It holds five Cards.'''
    card_count = 5
    five_of_a_kind = 8e5
    four_of_a_kind = 7e5
    straight = 6e5
    full_house = 5e5
    three_of_a_kind = 4e5
    two_pair = 3e5
    one_pair = 2e5
    high_card = 1e5

    string_to_card = {
        "N": Card.nine,
        "T": Card.ten,
        "J": Card.jack,
        "Q": Card.queen,
        "K": Card.king,
        "A": Card.ace
    }
    card_to_string = {c: s for s, c in
                      string_to_card.items()}

    @staticmethod
    def convert_hand(hand_raw):
        '''Converts a string of card chars or list of Cards into a Counter'''
        if isinstance(hand_raw, str):
            hand_raw = hand_raw.upper()
            hand_raw = (
                ''.join(
                    s for s in hand_raw if s in Hand.string_to_card.keys()))
            return Counter(Hand.string_to_card[x] for x in hand_raw)
        elif isinstance(hand_raw[0], Card):
            return Counter(hand_raw)
        elif isinstance(hand_raw, Counter):
            return hand_raw
        else:
            raise Exception("convert_hand requires a string or a list of"
                            " Cards")

    @staticmethod
    def random_hand(size=5):
        hand = []
        for i in range(size):
            hand.append(choice(list(Card)))
        return Counter(hand)

    def __init__(self, hand=None):
        if hand is None:
            hand = Hand.random_hand()
        self.hand = Hand.convert_hand(hand)  # a Counter

    def human_value(self):
        '''Gives the human-readable value of the current value of Hand.hand
        e.g. AAKQJ --> A A K Q J : One Pair - High Card: A'''
        human_hands = [
            'High Card',
            'One Pair',
            'Two Pair',
            'Three of a Kind',
            'Full House',
            'Straight',
            'Four of a Kind',
            'Five of a Kind']
        human_hand = human_hands[int((self.value() - (self.value() % 1e5)) //
                                     1e5) - 1]
        high_card = Hand.card_to_string[Card(int(((self.value() - self.value()
                                                   % 1e4) % 1e5) // 1e4))]
        return " : {0} - High Card: {1}".format(human_hand, high_card)

    @staticmethod
    def filter_card_string(card_string):
        '''Removes all non-card related characters and converts them to
        uppercase.'''
        card_string = card_string.upper()

        def is_card(c):
            return c in ("".join(Hand.string_to_card.keys()))
        string = "".join(filter(is_card, card_string))
        return string

    def value(self):
        ''' Values are stored in a 6 digit integer. The most significant
            digit corresponds to the actual hand (two pair, full house, etc.)
            while the rest encode the rest of the hand values in descending
            order of value.

            Ex: A A J J N --> 366331

            Order of hand values:
            Five of a Kind
            Four of a Kind
            Straight
            Full House
            Three of a Kind
            Two Pair
            One Pair
            High Card
        '''
        assert isinstance(self.hand, Counter)
        assert sum(self.hand.values()) == 5
        value = 0

        # Remove empty counters
        self.hand = Counter({key: value for key, value in self.hand.items() if
                             value > 0})
        # Determine actual hand value
        n_of_a_kind = max(self.hand.values())
        conversion_list = array([1e5, 2e5, 4e5, 7e5, 8e5])
        value += conversion_list[n_of_a_kind - 1]
        straight1 = Counter(
            [Card.ace, Card.king, Card.queen, Card.jack, Card.ten])
        straight2 = Counter(
            [Card.king, Card.queen, Card.jack, Card.ten, Card.nine])
        if self.hand == straight1 or self.hand == straight2:
            value = self.straight
        elif Counter(self.hand.values()) == Counter({3: 1, 2: 1}):
            value = self.full_house
        elif Counter(self.hand.values()) == Counter({2: 2, 1: 1}):
            value = self.two_pair

        # Encode card values
        weights = logspace(0, 4, 5, dtype=int32)
        hand_list = sorted([c for c in self.hand.elements()])
        for w, c in zip(weights, hand_list):
            value += w * int(c)
        return int32(value)

    @staticmethod
    def hand_subtract(b_hand, small_hand):
        big_hand = deepcopy(b_hand)
        big_hand.subtract(small_hand)
        if any([value < 0 for (key, value) in big_hand.items()]):
            raise ValueError(
                "Can't subtract small_hand from b_hand if small_hand is not a "
                "subset of b_hand")
        big_hand = Counter({key: value for key, value in big_hand.items() if
                            value > 0})
        return big_hand

    def swap_cards(self, old_cards, new_cards):
        if not Hand.hand_size(old_cards) == Hand.hand_size(new_cards):
            print("old_cards: " + str(old_cards))
            print("new_cards: " + str(new_cards))
            raise Exception("old_cards and new_cards must be the same length")
        if not all(oc in self.hand for oc in old_cards):
            raise Exception("Cannot swap out card not in hand")
        temp_hand = deepcopy(self.hand)
        for oc, nc in zip(old_cards, new_cards):
            temp_hand[oc] -= 1
            temp_hand[nc] += 1
        self.hand = temp_hand

    @staticmethod
    def hand_size(hand):

        return len([c for c in hand.elements()])

    def __lt__(self, other):
        '''Compares Hand with other Hand based on value'''
        return self.value() < other.value()

    def __gt__(self, other):
        return self.value() > other.value()

    def __eq__(self, other):
        return self.value() == other.value()

    def __str__(self):
        return " ".join([self.card_to_string[c]
                         for c in self.hand.elements()])[::-1]


def play_game():
    player_hand = Hand()
    ai_hand = Hand()
    rounds = 2
    for i in range(rounds):
        print("Round {0}:".format(i + 1))
        print(
            "Your hand: " + str(player_hand) + player_hand.human_value() + " "
            + str(player_hand.value()),
            str(Counter(player_hand.hand.values())))
        print("AI hand:   " + str(ai_hand) + ai_hand.human_value() +
              " " + str(ai_hand.value()), str(Counter(ai_hand.hand.values())))
        while True:
            try:
                cards_to_hold_str = Hand.filter_card_string(
                    input("Hold onto which cards? "))
                cards_to_hold = Hand.convert_hand(cards_to_hold_str)
                new_cards = Hand.random_hand(
                    Hand.card_count - Hand.hand_size(cards_to_hold))
                player_hand.swap_cards(Hand.hand_subtract(
                    player_hand.hand, cards_to_hold), new_cards)
                break
            except ValueError:
                print("You can only hold onto cards currently in your hand.")
        # TODO: Implement AI for deciding which cards to hold onto for ai_hand
    print("Final:")
    print("Your hand: " + str(player_hand) + player_hand.human_value() +
          " " + str(player_hand.value()),
          str(Counter(player_hand.hand.values())))
    print("AI hand:   " + str(ai_hand) + ai_hand.human_value() + " " +
          str(ai_hand.value()), str(Counter(ai_hand.hand.values())))
    if ai_hand > player_hand:
        print("YOU LOSE! HOW COULD YOU?")
    elif ai_hand < player_hand:
        print("YOU WIN! HOW DID THAT HAPPEN?")

play_game()
