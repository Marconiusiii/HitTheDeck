#!/usr/bin/env python3
import random

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


def compareHandTotals(player_total, dealer_total):
	if player_total >= 22:
		return "lose"
	if dealer_total >= 22:
		return "win"
	if player_total < dealer_total:
		return "lose"
	if player_total == dealer_total:
		return "push"
	return "win"


def bankrollDelta(outcome, bet, doubled=False, charlie_paid=False):
	wager = bet * 2 if doubled else bet
	if outcome == "lose":
		return -wager
	if outcome == "push":
		return 0
	if charlie_paid:
		return 0
	return wager


def settleSplitHand(hand_total, dealer_total, bet, doubled=False):
	outcome = compareHandTotals(hand_total, dealer_total)
	delta = bankrollDelta(outcome, bet, doubled=doubled)
	return outcome, delta


def startHand(card_a_value, card_b_value):
	hand = [11 if card_a_value == 1 else card_a_value, 11 if card_b_value == 1 else card_b_value]
	return hand, handValue(hand)


def drawCardToHand(shoe, hand):
	card_name, card_value = shoe.draw()
	shoe.counter(card_value)
	total = addCard(hand, card_value)
	return card_name, card_value, total


class Shoe:
	def __init__(self, deck_amount):
		self.deck_amount = deck_amount
		self.deck = deckGenerator()
		self.discard = []
		self.card_count = 0
		self.count_actual = 0

	def draw(self):
		if self.deck_amount == 1:
			card, card_value = random.choice(list(self.deck.items()))
			del self.deck[card]
			return card, card_value

		while True:
			card, card_value = random.choice(list(self.deck.items()))
			if self.discard.count(card) == self.deck_amount:
				del self.deck[card]
				continue
			self.discard.append(card)
			return card, card_value

	def counter(self, card):
		if card in range(2, 7):
			self.card_count += 1
		elif card >= 10:
			self.card_count -= 1

		cards_remaining = len(self.deck)
		if cards_remaining >= 260:
			true_count = 6
		elif 208 <= cards_remaining < 260:
			true_count = 5
		elif 156 <= cards_remaining < 208:
			true_count = 4
		elif 104 <= cards_remaining < 156:
			true_count = 3
		elif 52 <= cards_remaining < 104:
			true_count = 2
		else:
			true_count = 1

		self.count_actual = self.card_count // true_count
		return self.count_actual

	def reset(self):
		self.deck = deckGenerator()
		self.discard = []
		self.card_count = 0
		self.count_actual = 0
