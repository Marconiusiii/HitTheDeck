#!/usr/bin/env python3
from dataclasses import dataclass, field
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


def evaluateInitialBlackjack(player_total, dealer_raw_cards):
	player_blackjack = player_total == 21
	dealer_blackjack = isBlackjack(dealer_raw_cards)
	if player_blackjack and dealer_blackjack:
		return "push"
	if player_blackjack:
		return "player_blackjack"
	if dealer_blackjack:
		return "dealer_blackjack"
	return "none"


def resolveInsurance(upcard_value, took_insurance, dealer_blackjack, bet):
	if upcard_value != 1:
		if dealer_blackjack:
			return {"round_over": True, "bank_delta": -bet, "result": "dealer_blackjack"}
		return {"round_over": False, "bank_delta": 0, "result": "none"}

	if took_insurance:
		if dealer_blackjack:
			return {"round_over": True, "bank_delta": 0, "result": "insurance_win"}
		return {"round_over": False, "bank_delta": -(bet // 2), "result": "insurance_lose"}

	if dealer_blackjack:
		return {"round_over": True, "bank_delta": -bet, "result": "dealer_blackjack"}

	return {"round_over": False, "bank_delta": 0, "result": "none"}


@dataclass
class RoundState:
	bank: int
	bet: int
	player_hand: list = field(default_factory=list)
	dealer_hand: list = field(default_factory=list)
	player_total: int = 0
	dealer_total: int = 0
	player_cards: tuple = ("", "")
	dealer_cards: tuple = ("", "")
	choice: str = ""
	handsplit: list = None
	charlie_paid: bool = False


@dataclass
class RoundResolution:
	outcome: str
	bank_delta: int
	split_results: list = None
	events: list = field(default_factory=list)


def dealRound(shoe, bank, bet):
	card1_name, card1_value = shoe.draw()
	card2_name, card2_value = shoe.draw()
	shoe.counter(card1_value)
	shoe.counter(card2_value)

	dcard1_name, dcard1_value = shoe.draw()
	dcard2_name, dcard2_value = shoe.draw()
	shoe.counter(dcard1_value)
	shoe.counter(dcard2_value)

	player_hand, player_total = startHand(card1_value, card2_value)
	dealer_hand = [dcard1_value, dcard2_value]
	dealer_total = handValue([11 if card == 1 else card for card in dealer_hand])

	return RoundState(
		bank=bank,
		bet=bet,
		player_hand=player_hand,
		dealer_hand=dealer_hand,
		player_total=player_total,
		dealer_total=dealer_total,
		player_cards=(card1_name, card2_name),
		dealer_cards=(dcard1_name, dcard2_name),
	)


def applyAction(state, choice, hand_total=None, handsplit=None, bank_delta=0):
	state.choice = choice
	if hand_total is not None:
		state.player_total = hand_total
	if handsplit is not None:
		state.handsplit = handsplit
	state.bank += bank_delta
	return state


def evaluatePlayerTurnOutcome(state, dealer_total):
	if state.choice == "su":
		return {"round_over": True, "event": {"code": "player_surrender", "dealer_total": dealer_total}}
	if state.player_total >= 22:
		return {"round_over": True, "event": {"code": "player_bust", "dealer_total": dealer_total}}
	return {"round_over": False, "event": None}


def resolveRound(state, dealer_total):
	if state.choice == "sp" and state.handsplit and state.bank - state.bet * 2 >= 0:
		hand1, hand2, bet_double1, bet_double2 = state.handsplit
		outcome1, delta1 = settleSplitHand(hand1, dealer_total, state.bet, doubled=(bet_double1 == 1))
		outcome2, delta2 = settleSplitHand(hand2, dealer_total, state.bet, doubled=(bet_double2 == 1))
		return RoundResolution(
			outcome="split",
			bank_delta=delta1 + delta2,
			split_results=[(outcome1, delta1), (outcome2, delta2)],
			events=[
				{"code": "split_hand_result", "hand_index": 1, "outcome": outcome1},
				{"code": "split_hand_result", "hand_index": 2, "outcome": outcome2},
			],
		)

	outcome = compareHandTotals(state.player_total, dealer_total)
	delta = bankrollDelta(
		outcome,
		state.bet,
		doubled=(state.choice == "dd"),
		charlie_paid=state.charlie_paid,
	)
	if outcome == "lose":
		events = [{"code": "player_lose"}]
	elif outcome == "push":
		events = [{"code": "player_push"}]
	elif dealer_total >= 22 and state.player_total <= 21:
		events = [{"code": "dealer_bust_win", "dealer_total": dealer_total}]
	else:
		events = [{"code": "player_win"}]
	return RoundResolution(outcome=outcome, bank_delta=delta, split_results=None, events=events)


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
