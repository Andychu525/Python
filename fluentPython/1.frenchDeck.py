import collections
from random import choice

Card = collections.namedtuple('Card', ['rank', 'suit'])


class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self._cards = [Card(rank, suit) for rank in self.ranks
                       for suit in self.suits]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]


def spades_high(card):
    suit_values = dict(spades=3, hearts=2, diamonds=1, clubs=0)
    rand_value = FrenchDeck.ranks.index(card.rank)
    return rand_value * len(suit_values) + suit_values[card.suit]


def main():
    deck = FrenchDeck()
    for card in sorted(deck, key=spades_high, reverse=True):
        print(card)


if __name__ == '__main__':
    main()
