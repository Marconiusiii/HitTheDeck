#!/usr/bin/env python3

import unittest

from engine import Shoe, addCard, bankrollDelta, canSplitCards, compareHandTotals
from engine import deckGenerator, drawCardToHand, handValue, isBlackjack
from engine import evaluateInitialBlackjack, resolveInsurance, settleSplitHand, startHand


class EngineTests(unittest.TestCase):
	def test_deck_generator_builds_standard_deck(self):
		deck = deckGenerator()
		self.assertEqual(len(deck), 52)
		self.assertEqual(deck["Ace of Spades"], 1)
		self.assertEqual(deck["King of Hearts"], 10)

	def test_hand_value_converts_soft_aces(self):
		self.assertEqual(handValue([11, 9]), 20)
		self.assertEqual(handValue([11, 9, 5]), 15)
		self.assertEqual(handValue([11, 11, 9]), 21)

	def test_add_card_handles_ace(self):
		hand = [10, 6]
		total = addCard(hand, 1)
		self.assertEqual(hand, [10, 6, 11])
		self.assertEqual(total, 17)

	def test_blackjack_detection(self):
		self.assertTrue(isBlackjack([1, 10]))
		self.assertTrue(isBlackjack([10, 1]))
		self.assertFalse(isBlackjack([11, 10]))
		self.assertFalse(isBlackjack([1, 9, 1]))

	def test_split_card_rank_detection(self):
		self.assertTrue(canSplitCards("8 of Spades", "8 of Hearts"))
		self.assertFalse(canSplitCards("10 of Spades", "King of Hearts"))

	def test_shoe_single_deck_draw_reduces_deck_size(self):
		shoe = Shoe(1)
		start_size = len(shoe.deck)
		card_name, card_value = shoe.draw()
		self.assertIsInstance(card_name, str)
		self.assertIn(card_value, range(1, 11))
		self.assertEqual(len(shoe.deck), start_size - 1)

	def test_shoe_counter_updates_running_and_true_count(self):
		shoe = Shoe(1)
		shoe.counter(2)
		shoe.counter(10)
		self.assertEqual(shoe.card_count, 0)
		self.assertEqual(shoe.count_actual, 0)

	def test_shoe_reset_restores_state(self):
		shoe = Shoe(2)
		shoe.draw()
		shoe.counter(10)
		shoe.reset()
		self.assertEqual(len(shoe.deck), 52)
		self.assertEqual(shoe.discard, [])
		self.assertEqual(shoe.card_count, 0)
		self.assertEqual(shoe.count_actual, 0)

	def test_compare_hand_totals(self):
		self.assertEqual(compareHandTotals(18, 22), "win")
		self.assertEqual(compareHandTotals(22, 18), "lose")
		self.assertEqual(compareHandTotals(17, 17), "push")
		self.assertEqual(compareHandTotals(19, 18), "win")
		self.assertEqual(compareHandTotals(16, 20), "lose")

	def test_bankroll_delta(self):
		self.assertEqual(bankrollDelta("lose", 10), -10)
		self.assertEqual(bankrollDelta("lose", 10, doubled=True), -20)
		self.assertEqual(bankrollDelta("push", 10), 0)
		self.assertEqual(bankrollDelta("win", 10), 10)
		self.assertEqual(bankrollDelta("win", 10, doubled=True), 20)
		self.assertEqual(bankrollDelta("win", 10, charlie_paid=True), 0)

	def test_settle_split_hand(self):
		outcome, delta = settleSplitHand(20, 18, 10, doubled=False)
		self.assertEqual(outcome, "win")
		self.assertEqual(delta, 10)
		outcome, delta = settleSplitHand(16, 20, 10, doubled=True)
		self.assertEqual(outcome, "lose")
		self.assertEqual(delta, -20)

	def test_start_hand_converts_aces(self):
		hand, total = startHand(1, 9)
		self.assertEqual(hand, [11, 9])
		self.assertEqual(total, 20)

	def test_draw_card_to_hand(self):
		shoe = Shoe(1)
		hand = [10, 6]
		card_name, card_value, total = drawCardToHand(shoe, hand)
		self.assertIsInstance(card_name, str)
		self.assertIn(card_value, range(1, 11))
		self.assertEqual(total, handValue(hand))

	def test_evaluate_initial_blackjack(self):
		self.assertEqual(evaluateInitialBlackjack(21, [1, 10]), "push")
		self.assertEqual(evaluateInitialBlackjack(21, [9, 7]), "player_blackjack")
		self.assertEqual(evaluateInitialBlackjack(20, [1, 10]), "dealer_blackjack")
		self.assertEqual(evaluateInitialBlackjack(20, [9, 7]), "none")

	def test_resolve_insurance(self):
		res = resolveInsurance(1, True, True, 20)
		self.assertEqual(res["result"], "insurance_win")
		self.assertEqual(res["bank_delta"], 0)
		self.assertTrue(res["round_over"])

		res = resolveInsurance(1, True, False, 20)
		self.assertEqual(res["result"], "insurance_lose")
		self.assertEqual(res["bank_delta"], -10)
		self.assertFalse(res["round_over"])

		res = resolveInsurance(1, False, True, 20)
		self.assertEqual(res["result"], "dealer_blackjack")
		self.assertEqual(res["bank_delta"], -20)
		self.assertTrue(res["round_over"])


if __name__ == "__main__":
	unittest.main()
