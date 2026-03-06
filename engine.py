#!/usr/bin/env python3

SUITS = ["Spades", "Clubs", "Hearts", "Diamonds"]

CARD_VALUES = {
	"Ace": 1,
	"2": 2,
	"3": 3,
	"4": 4,
	"5": 5,
	"6": 6,
	"7": 7,
	"8": 8,
	"9": 9,
	"10": 10,
	"Jack": 10,
	"Queen": 10,
	"King": 10,
}


def deckGenerator():
	deck = {}
	for suit in SUITS:
		for card, value in CARD_VALUES.items():
			deck["{} of {}".format(card, suit)] = value
	return deck


def handCount(hand):
	count = 0
	for value in hand:
		count += value
	return count


def handValue(hand):
	total = handCount(hand)
	soft_aces = hand.count(11)
	while total > 21 and soft_aces > 0:
		total -= 10
		soft_aces -= 1
	return total


def addCard(hand, card_value):
	if card_value == 1:
		hand.append(11)
	else:
		hand.append(card_value)
	return handValue(hand)


def isBlackjack(raw_cards):
	return len(raw_cards) == 2 and 1 in raw_cards and 10 in raw_cards


def cardRank(card_name):
	return card_name.split()[0]


def canSplitCards(card1_name, card2_name):
	return cardRank(card1_name) == cardRank(card2_name)
