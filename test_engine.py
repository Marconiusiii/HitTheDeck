#!/usr/bin/env python3

import unittest

from engine import addCard, canSplitCards, deckGenerator, handValue, isBlackjack


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


if __name__ == "__main__":
	unittest.main()
