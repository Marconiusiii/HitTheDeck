#!/usr/bin/env python3

import unittest

from engine import RoundState, Shoe, addCard, applyAction, bankrollDelta
from engine import applyNonSplitIntent, parsePlayerIntent
from engine import canSplitCards, compareHandTotals, dealRound, parseBankInput
from engine import parseDeckCount, startSession
from engine import deckGenerator, drawCardToHand, handValue, isBlackjack
from engine import evaluateInitialBlackjack, evalTurnOut, resolveInsurance, resolveRound
from engine import playDealerTurn, playerDoubleDownStep, playerHitStep, settleSplitHand
from engine import resolveSplitHandIntent, resolveTurnFlow, runDdFlow, runHitFlow
from engine import runSplitFlow, startHand, startSplitHands


class FakeShoe:
	def __init__(self, draws):
		self.draws = list(draws)
		self.cardCnt = 0
		self.countNow = 0

	def draw(self):
		return self.draws.pop(0)

	def counter(self, card):
		return card


class EngineTests(unittest.TestCase):
	def testDeckGenStd(self):
		deck = deckGenerator()
		self.assertEqual(len(deck), 52)
		self.assertEqual(deck["Ace of Spades"], 1)
		self.assertEqual(deck["King of Hearts"], 10)

	def testHandValAces(self):
		self.assertEqual(handValue([11, 9]), 20)
		self.assertEqual(handValue([11, 9, 5]), 15)
		self.assertEqual(handValue([11, 11, 9]), 21)

	def testAddCardAce(self):
		hand = [10, 6]
		total = addCard(hand, 1)
		self.assertEqual(hand, [10, 6, 11])
		self.assertEqual(total, 17)

	def testBlackjack(self):
		self.assertTrue(isBlackjack([1, 10]))
		self.assertTrue(isBlackjack([10, 1]))
		self.assertFalse(isBlackjack([11, 10]))
		self.assertFalse(isBlackjack([1, 9, 1]))

	def testSplitRank(self):
		self.assertTrue(canSplitCards("8 of Spades", "8 of Hearts"))
		self.assertFalse(canSplitCards("10 of Spades", "King of Hearts"))

	def testShoeDrawSize(self):
		shoe = Shoe(1)
		startSize = len(shoe.deck)
		cardName, cardVal = shoe.draw()
		self.assertIsInstance(cardName, str)
		self.assertIn(cardVal, range(1, 11))
		self.assertEqual(len(shoe.deck), startSize - 1)

	def testShoeCount(self):
		shoe = Shoe(1)
		shoe.counter(2)
		shoe.counter(10)
		self.assertEqual(shoe.cardCnt, 0)
		self.assertEqual(shoe.countNow, 0)

	def testShoeReset(self):
		shoe = Shoe(2)
		shoe.draw()
		shoe.counter(10)
		shoe.reset()
		self.assertEqual(len(shoe.deck), 52)
		self.assertEqual(shoe.discard, [])
		self.assertEqual(shoe.cardCnt, 0)
		self.assertEqual(shoe.countNow, 0)

	def testCmpTotals(self):
		self.assertEqual(compareHandTotals(18, 22), "win")
		self.assertEqual(compareHandTotals(22, 18), "lose")
		self.assertEqual(compareHandTotals(17, 17), "push")
		self.assertEqual(compareHandTotals(19, 18), "win")
		self.assertEqual(compareHandTotals(16, 20), "lose")

	def testBankDelta(self):
		self.assertEqual(bankrollDelta("lose", 10), -10)
		self.assertEqual(bankrollDelta("lose", 10, doubled=True), -20)
		self.assertEqual(bankrollDelta("push", 10), 0)
		self.assertEqual(bankrollDelta("win", 10), 10)
		self.assertEqual(bankrollDelta("win", 10, doubled=True), 20)
		self.assertEqual(bankrollDelta("win", 10, charliePaid=True), 0)

	def testSettleSplit(self):
		outcome, delta = settleSplitHand(20, 18, 10, doubled=False)
		self.assertEqual(outcome, "win")
		self.assertEqual(delta, 10)
		outcome, delta = settleSplitHand(16, 20, 10, doubled=True)
		self.assertEqual(outcome, "lose")
		self.assertEqual(delta, -20)

	def testStartHandAce(self):
		hand, total = startHand(1, 9)
		self.assertEqual(hand, [11, 9])
		self.assertEqual(total, 20)

	def testDrawToHand(self):
		shoe = Shoe(1)
		hand = [10, 6]
		cardName, cardVal, total = drawCardToHand(shoe, hand)
		self.assertIsInstance(cardName, str)
		self.assertIn(cardVal, range(1, 11))
		self.assertEqual(total, handValue(hand))

	def testInitBj(self):
		self.assertEqual(evaluateInitialBlackjack(21, [1, 10]), "push")
		self.assertEqual(evaluateInitialBlackjack(21, [9, 7]), "playerBj")
		self.assertEqual(evaluateInitialBlackjack(20, [1, 10]), "dealerBj")
		self.assertEqual(evaluateInitialBlackjack(20, [9, 7]), "none")

	def testInsResolve(self):
		res = resolveInsurance(1, True, True, 20)
		self.assertEqual(res["result"], "insWin")
		self.assertEqual(res["bankDelta"], 0)
		self.assertTrue(res["roundOver"])

		res = resolveInsurance(1, True, False, 20)
		self.assertEqual(res["result"], "insLose")
		self.assertEqual(res["bankDelta"], -10)
		self.assertFalse(res["roundOver"])

		res = resolveInsurance(1, False, True, 20)
		self.assertEqual(res["result"], "dealerBj")
		self.assertEqual(res["bankDelta"], -20)
		self.assertTrue(res["roundOver"])

	def testDealRound(self):
		shoe = Shoe(1)
		state = dealRound(shoe, bank=100, bet=10)
		self.assertIsInstance(state, RoundState)
		self.assertEqual(state.bank, 100)
		self.assertEqual(state.bet, 10)
		self.assertEqual(len(state.playerHand), 2)
		self.assertEqual(len(state.dealerHand), 2)
		self.assertEqual(len(state.playerCards), 2)
		self.assertEqual(len(state.dealerCards), 2)
		self.assertEqual(len(shoe.deck), 48)

	def testApplyAction(self):
		state = RoundState(bank=100, bet=10)
		updated = applyAction(state, "dd", handTotal=18, handsplit=[18, 17, 0, 0], bankDelta=-10)
		self.assertEqual(updated.choice, "dd")
		self.assertEqual(updated.playerTotal, 18)
		self.assertEqual(updated.handsplit, [18, 17, 0, 0])
		self.assertEqual(updated.bank, 90)

	def testResolveRound(self):
		state = RoundState(bank=100, bet=10, playerTotal=19, choice="s", charliePaid=False)
		resolution = resolveRound(state, dealerTotal=18)
		self.assertEqual(resolution.outcome, "win")
		self.assertEqual(resolution.bankDelta, 10)
		self.assertEqual(resolution.events[0]["code"], "playerWin")

		splitState = RoundState(
			bank=100,
			bet=10,
			choice="sp",
			handsplit=[20, 18, 0, 1],
		)
		splitRes = resolveRound(splitState, dealerTotal=19)
		self.assertEqual(splitRes.outcome, "split")
		self.assertEqual(splitRes.splitRes[0][0], "win")
		self.assertEqual(splitRes.splitRes[1][0], "lose")
		self.assertEqual(splitRes.events[0]["code"], "splitHandRes")
		self.assertEqual(splitRes.events[1]["code"], "splitHandRes")

	def testTurnOutcome(self):
		state = RoundState(bank=100, bet=10, choice="su")
		outcome = evalTurnOut(state, dealerTotal=18)
		self.assertTrue(outcome["roundOver"])
		self.assertEqual(outcome["event"]["code"], "playerSurr")

		state = RoundState(bank=100, bet=10, choice="h", playerTotal=23)
		outcome = evalTurnOut(state, dealerTotal=18)
		self.assertTrue(outcome["roundOver"])
		self.assertEqual(outcome["event"]["code"], "playerBust")

	def testHitDdSteps(self):
		shoe = Shoe(1)
		hand = [10, 5]
		step = playerHitStep(shoe, hand)
		self.assertIn("cardName", step)
		self.assertIn("total", step)
		self.assertEqual(step["total"], handValue(hand))

		hand2 = [9, 2]
		step2 = playerDoubleDownStep(shoe, hand2)
		self.assertIn("cardName", step2)
		self.assertIn("total", step2)
		self.assertEqual(step2["total"], handValue(hand2))

	def testDealerTurn(self):
		shoe = Shoe(1)
		dealerHand = [10, 6]
		result = playDealerTurn(shoe, dealerHand)
		self.assertIn("finalTotal", result)
		self.assertIn("events", result)
		if result["events"]:
			self.assertGreaterEqual(result["finalTotal"], 17)

	def testStartSplit(self):
		shoe = Shoe(1)
		playerHand = [8, 8]
		result = startSplitHands(shoe, playerHand)
		self.assertIn("firstDrawCard", result)
		self.assertIn("secondDrawCard", result)
		self.assertEqual(len(result["hand1"]), 2)
		self.assertEqual(len(result["hand2"]), 2)

	def testSplitIntent(self):
		shoe = Shoe(1)
		hand = [8, 8]
		curTotal = 16
		result = resolveSplitHandIntent("h", shoe, hand, curTotal)
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

	def testRunHitFlow(self):
		shoe = FakeShoe([
			("4 of Hearts", 4),
			("2 of Clubs", 2),
		])
		hand = [10, 2]
		choices = iter(["h", "s"])
		def readChoice(promptKey, total, canSplit=False):
			self.assertEqual(promptKey, "hitStand")
			return next(choices)
		result = runHitFlow(shoe, hand, 12, readChoice)
		self.assertEqual(result["total"], 18)
		self.assertEqual(result["events"][0]["code"], "playerDraw")
		self.assertEqual(result["events"][1]["code"], "playerDraw")
		self.assertEqual(result["events"][-1]["code"], "playerStand")

	def testRunDdFlow(self):
		shoe = FakeShoe([("9 of Clubs", 9)])
		hand = [5, 6]
		result = runDdFlow(shoe, hand)
		self.assertEqual(result["total"], 20)
		self.assertEqual(result["events"][0]["code"], "playerDd")
		self.assertFalse(result["events"][0]["bust"])

	def testRunSplitFlow(self):
		shoe = FakeShoe([
			("3 of Hearts", 3),
			("4 of Clubs", 4),
			("5 of Spades", 5),
			("9 of Diamonds", 9),
		])
		playerHand = [8, 8]
		choices = iter(["h", "s", "dd"])
		def readChoice(promptKey, total, canSplit=False):
			return next(choices)
		result = runSplitFlow(shoe, playerHand, readChoice)
		self.assertEqual(result["handsplit"], [16, 21, 0, 1])
		self.assertEqual(result["events"][0]["code"], "splitStart")
		self.assertEqual(result["events"][1]["code"], "splitDraw")
		self.assertEqual(result["events"][2]["code"], "splitStand")
		self.assertEqual(result["events"][-1]["code"], "splitDd")

	def testResolveTurnFlow(self):
		shoe = FakeShoe([("4 of Hearts", 4)])
		state = RoundState(bank=100, bet=10, playerHand=[10, 2], playerTotal=12)
		choices = iter(["h", "s"])
		def readChoice(promptKey, total, canSplit=False):
			return next(choices)
		result = resolveTurnFlow(False, state, shoe, readChoice)
		self.assertFalse(result["quit"])
		self.assertEqual(result["state"].choice, "h")
		self.assertEqual(result["state"].playerTotal, 16)
		self.assertEqual(result["events"][0]["code"], "playerDraw")
		self.assertEqual(result["events"][-1]["code"], "playerStand")

	def testResolveTurnFlowSplitNoFunds(self):
		shoe = FakeShoe([("5 of Hearts", 5)])
		state = RoundState(bank=15, bet=10, playerHand=[8, 8], playerTotal=16)
		choices = iter(["sp", "s"])
		def readChoice(promptKey, total, canSplit=False):
			return next(choices)
		result = resolveTurnFlow(True, state, shoe, readChoice)
		self.assertEqual(result["events"][0]["code"], "splitNoFunds")
		self.assertEqual(result["state"].choice, "h")
		self.assertEqual(result["state"].playerTotal, 21)

	def testParseIntent(self):
		self.assertEqual(parsePlayerIntent("h", False)["intent"], "hit")
		self.assertEqual(parsePlayerIntent("H", False)["intent"], "hit")
		self.assertEqual(parsePlayerIntent("dd", False)["intent"], "doubleDn")
		self.assertEqual(parsePlayerIntent("su", False)["intent"], "surrender")
		self.assertEqual(parsePlayerIntent("s", False)["intent"], "stand")
		self.assertEqual(parsePlayerIntent("q", False)["intent"], "quit")
		self.assertFalse(parsePlayerIntent("sp", True)["invalid"])
		spBlocked = parsePlayerIntent("sp", False)
		self.assertTrue(spBlocked["invalid"])
		self.assertTrue(spBlocked["splitBlock"])
		self.assertTrue(parsePlayerIntent("x", False)["invalid"])
		self.assertTrue(parsePlayerIntent("bad", False)["invalid"])

	def testApplyIntent(self):
		state = RoundState(bank=100, bet=10, playerTotal=15)
		applyNonSplitIntent(state, "hit", handTotal=18)
		self.assertEqual(state.choice, "h")
		self.assertEqual(state.playerTotal, 18)

		applyNonSplitIntent(state, "doubleDn", handTotal=20)
		self.assertEqual(state.choice, "dd")
		self.assertEqual(state.playerTotal, 20)

		applyNonSplitIntent(state, "surrender")
		self.assertEqual(state.choice, "su")
		self.assertEqual(state.bank, 95)

		applyNonSplitIntent(state, "stand")
		self.assertEqual(state.choice, "s")

	def testParseBank(self):
		self.assertTrue(parseBankInput("100")["ok"])
		self.assertEqual(parseBankInput("100")["value"], 100)
		self.assertFalse(parseBankInput("abc")["ok"])

	def testParseDeck(self):
		ok = parseDeckCount("6")
		self.assertTrue(ok["ok"])
		self.assertEqual(ok["value"], 6)
		tooLow = parseDeckCount("0")
		self.assertFalse(tooLow["ok"])
		self.assertEqual(tooLow["reason"], "tooLow")
		tooHigh = parseDeckCount("7")
		self.assertFalse(tooHigh["ok"])
		self.assertEqual(tooHigh["reason"], "tooHigh")
		notNum = parseDeckCount("abc")
		self.assertFalse(notNum["ok"])
		self.assertEqual(notNum["reason"], "notNum")

	def testStartSession(self):
		session = startSession(250, 3)
		self.assertEqual(session["bank"], 250)
		self.assertEqual(session["initBank"], 250)
		self.assertEqual(session["deckAmt"], 3)
		self.assertIn("shoe", session)


if __name__ == "__main__":
	unittest.main()
