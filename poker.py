#!/usr/local/bin/python3
from enum import IntEnum
from collections import Counter
from numpy import array, logspace, int32
from random import choice
from copy import deepcopy
class Card(IntEnum):
    """A Card. Don't overthink it."""
    nine = 1
    ten = 2
    jack = 3
    queen = 4
    king = 5
    ace = 6

class Hand:
    """A hand. It holds five Cards."""
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
        if isinstance(hand_raw, str):
            hand_raw = hand_raw.upper()
            hand_raw = ''.join(s for s in hand_raw if s in
                    Hand.string_to_card.keys())
            return Counter(Hand.string_to_card[x] for x in hand_raw)
        elif type(hand_raw[0]) == type(Card.nine):
            return Counter(hand_raw)
        elif type(hand_raw) is Counter:
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
        self.hand = Hand.convert_hand(hand) # a Counter
    def human_value(self):
        human_hands = ['High Card','One Pair', 'Two Pair', 'Three of a Kind',
                'Full House', 'Straight', 'Four of a Kind', 'Five of a Kind']
        human_hand = human_hands[int((self.value() - (self.value()%1e5)) // 1e5) - 1] 
        high_card = Hand.card_to_string[Card(int(((self.value() - self.value()%1e4) %
            1e5) // 1e4))]
        return " : {0} - High Card: {1}".format(human_hand, high_card)
    @staticmethod
    def filter_card_string(card_string):
        card_string = card_string.upper()
        def is_card(c):
            return c in ("".join(Hand.string_to_card.keys()))
        return "".join(filter(is_card, card_string))

    def value(self):
        """ Values are stored in a 6 digit integer. The most significant
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
        """
        assert type(self.hand) is Counter
        assert sum(self.hand.values()) == 5
        value = 0 

        # Determine actual hand value
        n_of_a_kind = max(self.hand.values())
        conversion_list = array([1e5,2e5,4e5,7e5,8e5])
        value += conversion_list[n_of_a_kind - 1]
        straight1 = Counter([Card.ace,Card.king,Card.queen,Card.jack,Card.ten])
        straight2 = Counter([Card.king,Card.queen,Card.jack,Card.ten,Card.nine])
        if self.hand == straight1 or self.hand == straight2:
            value = self.straight
        elif Counter(self.hand.values()) == Counter({3: 1, 2: 1}):
            value = self.full_house
        elif Counter(self.hand.values()) == Counter({2: 2, 1: 1}):
            value = self.two_pair
        
        # Encode card values
        weights = logspace(0,4,5, dtype=int32)
        hand_list = sorted([c for c in self.hand.elements()])
        for w, c in zip(weights, hand_list):
            value += w * int(c)
        return int32(value)
    def swap_cards(self, old_cards, new_cards):
        if not len(old_cards) == len(new_cards):
            raise Exception("old_cards and new_cards must be the same length")
        if not all(oc in self.hand for oc in old_cards):
            raise Exception("Cannot swap out card not in hand")
        temp_hand = deepcopy(self.hand)
        for oc, nc in zip(old_cards, new_cards):
            temp_hand[oc] -= 1
            temp_hand[nc] += 1
        self.hand = temp_hand

    def __lt__(self,other):
        """Compares Hand with other Hand based on value"""
        return self.value() < other.value()
    def __gt__(self,other):
        return self.value() > other.value()
    def __eq__(self,other):
        return self.value() == other.value()
    def __str__(self):
        return " ".join([self.card_to_string[c] for c in self.hand.elements()])[::-1]
def play_game():
    player_hand = Hand()
    ai_hand = Hand()
    print("Your hand: " + str(player_hand) + player_hand.human_value())
    print("AI hand:   " + str(ai_hand) + ai_hand.human_value())
    cards_to_hold_str = Hand.filter_card_string(input("Hold onto which cards? "))
play_game()
