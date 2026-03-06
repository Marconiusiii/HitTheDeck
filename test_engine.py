#!/usr/bin/env python3

import unittest

from engine import RoundState, Shoe, addCard, applyAction, bankrollDelta
from engine import canSplitCards, compareHandTotals, dealRound
from engine import deckGenerator, drawCardToHand, handValue, isBlackjack
from engine import evaluateInitialBlackjack, evaluatePlayerTurnOutcome, resolveInsurance, resolveRound
from engine import playDealerTurn, playerDoubleDownStep, playerHitStep, settleSplitHand
from engine import resolveSplitHandIntent, startHand, startSplitHands


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

	def test_deal_round(self):
		shoe = Shoe(1)
		state = dealRound(shoe, bank=100, bet=10)
		self.assertIsInstance(state, RoundState)
		self.assertEqual(state.bank, 100)
		self.assertEqual(state.bet, 10)
		self.assertEqual(len(state.player_hand), 2)
		self.assertEqual(len(state.dealer_hand), 2)
		self.assertEqual(len(state.player_cards), 2)
		self.assertEqual(len(state.dealer_cards), 2)
		self.assertEqual(len(shoe.deck), 48)

	def test_apply_action(self):
		state = RoundState(bank=100, bet=10)
		updated = applyAction(state, "dd", hand_total=18, handsplit=[18, 17, 0, 0], bank_delta=-10)
		self.assertEqual(updated.choice, "dd")
		self.assertEqual(updated.player_total, 18)
		self.assertEqual(updated.handsplit, [18, 17, 0, 0])
		self.assertEqual(updated.bank, 90)

	def test_resolve_round(self):
		state = RoundState(bank=100, bet=10, player_total=19, choice="s", charlie_paid=False)
		resolution = resolveRound(state, dealer_total=18)
		self.assertEqual(resolution.outcome, "win")
		self.assertEqual(resolution.bank_delta, 10)
		self.assertEqual(resolution.events[0]["code"], "player_win")

		split_state = RoundState(
			bank=100,
			bet=10,
			choice="sp",
			handsplit=[20, 18, 0, 1],
		)
		split_resolution = resolveRound(split_state, dealer_total=19)
		self.assertEqual(split_resolution.outcome, "split")
		self.assertEqual(split_resolution.split_results[0][0], "win")
		self.assertEqual(split_resolution.split_results[1][0], "lose")
		self.assertEqual(split_resolution.events[0]["code"], "split_hand_result")
		self.assertEqual(split_resolution.events[1]["code"], "split_hand_result")

	def test_evaluate_player_turn_outcome(self):
		state = RoundState(bank=100, bet=10, choice="su")
		outcome = evaluatePlayerTurnOutcome(state, dealer_total=18)
		self.assertTrue(outcome["round_over"])
		self.assertEqual(outcome["event"]["code"], "player_surrender")

		state = RoundState(bank=100, bet=10, choice="h", player_total=23)
		outcome = evaluatePlayerTurnOutcome(state, dealer_total=18)
		self.assertTrue(outcome["round_over"])
		self.assertEqual(outcome["event"]["code"], "player_bust")

	def test_player_hit_and_double_steps(self):
		shoe = Shoe(1)
		hand = [10, 5]
		step = playerHitStep(shoe, hand)
		self.assertIn("card_name", step)
		self.assertIn("total", step)
		self.assertEqual(step["total"], handValue(hand))

		hand2 = [9, 2]
		step2 = playerDoubleDownStep(shoe, hand2)
		self.assertIn("card_name", step2)
		self.assertIn("total", step2)
		self.assertEqual(step2["total"], handValue(hand2))

	def test_play_dealer_turn(self):
		shoe = Shoe(1)
		dealer_hand = [10, 6]
		result = playDealerTurn(shoe, dealer_hand)
		self.assertIn("final_total", result)
		self.assertIn("events", result)
		if result["events"]:
			self.assertGreaterEqual(result["final_total"], 17)

	def test_start_split_hands(self):
		shoe = Shoe(1)
		player_hand = [8, 8]
		result = startSplitHands(shoe, player_hand)
		self.assertIn("first_draw_card", result)
		self.assertIn("second_draw_card", result)
		self.assertEqual(len(result["hand1"]), 2)
		self.assertEqual(len(result["hand2"]), 2)

	def test_resolve_split_hand_intent(self):
		shoe = Shoe(1)
		hand = [8, 8]
		current_total = 16
		result = resolveSplitHandIntent("h", shoe, hand, current_total)
		self.assertEqual(result["intent"], "h")
		self.assertIn("total", result)
		self.assertFalse(result["invalid"])

		result = resolveSplitHandIntent("dd", shoe, hand, result["total"])
		self.assertEqual(result["intent"], "dd")
		self.assertTrue(result["doubled"])
		self.assertTrue(result["complete"])

		result = resolveSplitHandIntent("s", shoe, hand, result["total"])
		self.assertEqual(result["intent"], "s")
		self.assertTrue(result["complete"])

		result = resolveSplitHandIntent("bad", shoe, hand, result["total"])
		self.assertTrue(result["invalid"])


if __name__ == "__main__":
	unittest.main()
