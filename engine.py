#!/usr/bin/env python3
from dataclasses import dataclass, field
import random

SUITS = ["Spades", "Clubs", "Hearts", "Diamonds"]

cardVals = {
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
		for card, value in cardVals.items():
			deck["{} of {}".format(card, suit)] = value
	return deck


def handCount(hand):
	count = 0
	for value in hand:
		count += value
	return count


def handValue(hand):
	total = handCount(hand)
	softAces = hand.count(11)
	while total > 21 and softAces > 0:
		total -= 10
		softAces -= 1
	return total


def addCard(hand, cardVal):
	if cardVal == 1:
		hand.append(11)
	else:
		hand.append(cardVal)
	return handValue(hand)


def isBlackjack(rawCards):
	return len(rawCards) == 2 and 1 in rawCards and 10 in rawCards


def cardRank(cardName):
	return cardName.split()[0]


def canSplitCards(card1Name, card2Name):
	return cardRank(card1Name) == cardRank(card2Name)


def compareHandTotals(playerTotal, dealerTotal):
	if playerTotal >= 22:
		return "lose"
	if dealerTotal >= 22:
		return "win"
	if playerTotal < dealerTotal:
		return "lose"
	if playerTotal == dealerTotal:
		return "push"
	return "win"


def bankrollDelta(outcome, bet, doubled=False, charliePaid=False):
	wager = bet * 2 if doubled else bet
	if outcome == "lose":
		return -wager
	if outcome == "push":
		return 0
	if charliePaid:
		return 0
	return wager


def settleSplitHand(handTotal, dealerTotal, bet, doubled=False):
	outcome = compareHandTotals(handTotal, dealerTotal)
	delta = bankrollDelta(outcome, bet, doubled=doubled)
	return outcome, delta


def startHand(cardAVal, cardBVal):
	hand = [11 if cardAVal == 1 else cardAVal, 11 if cardBVal == 1 else cardBVal]
	return hand, handValue(hand)


def drawCardToHand(shoe, hand):
	cardName, cardVal = shoe.draw()
	shoe.counter(cardVal)
	total = addCard(hand, cardVal)
	return cardName, cardVal, total


def playerHitStep(shoe, playerHand):
	cardName, cardVal, total = drawCardToHand(shoe, playerHand)
	return GameEvent(
		code="playerDraw",
		cardName=cardName,
		cardVal=cardVal,
		total=total,
		bust=(total >= 22),
	)


@dataclass
class GameEvent:
	code: str
	cardName: str = ""
	cardVal: int = 0
	total: int = 0
	handIdx: int = 0
	outcome: str = ""
	splitBlock: bool = False
	bust: bool = False
	dealerTotal: int = 0


@dataclass
class StepOut:
	total: int
	events: list = field(default_factory=list)
	handsplit: list = None
	betDbl: int = 0


@dataclass
class TurnFlow:
	state: object
	events: list = field(default_factory=list)
	quit: bool = False


@dataclass
class InsOut:
	roundOver: bool
	bankDelta: int
	result: str


def playerDoubleDownStep(shoe, playerHand):
	cardName, cardVal, total = drawCardToHand(shoe, playerHand)
	return GameEvent(
		code="playerDd",
		cardName=cardName,
		cardVal=cardVal,
		total=total,
		bust=(total >= 22),
	)


def dealerDrawStep(shoe, dealerHand):
	cardName, cardVal, total = drawCardToHand(shoe, dealerHand)
	return GameEvent(code="dealerDraw", cardName=cardName, cardVal=cardVal, total=total)


def playDealerTurn(shoe, dealerHand):
	dealerHand[:] = [11 if card == 1 else card for card in dealerHand]
	total = handValue(dealerHand)
	events = []
	if total < 17:
		while total <= 16:
			step = dealerDrawStep(shoe, dealerHand)
			total = step.total
			events.append(step)
	return StepOut(total=total, events=events)


def startSplitHands(shoe, playerHand):
	card1Name, card1Val, _ = drawCardToHand(shoe, [])
	card2Name, card2Val, _ = drawCardToHand(shoe, [])
	hand1, total1 = startHand(card1Val, playerHand[0])
	hand2, total2 = startHand(card2Val, playerHand[1])
	return {
		"firstDrawCard": card1Name,
		"secondDrawCard": card2Name,
		"hand1": hand1,
		"hand2": hand2,
		"total1": total1,
		"total2": total2,
	}


def resolveSplitHandIntent(choice, shoe, hand, curTotal):
	intent = choice.lower()
	result = {
		"intent": intent,
		"total": curTotal,
		"doubled": False,
		"drawCard": None,
		"bust": False,
		"complete": False,
		"invalid": False,
	}
	if intent == "h":
		step = playerHitStep(shoe, hand)
		result["total"] = step.total
		result["drawCard"] = step.cardName
		result["bust"] = step.bust
		result["complete"] = step.bust
		return result
	if intent == "dd":
		step = playerDoubleDownStep(shoe, hand)
		result["total"] = step.total
		result["drawCard"] = step.cardName
		result["bust"] = step.bust
		result["doubled"] = True
		result["complete"] = True
		return result
	if intent == "s":
		result["complete"] = True
		return result
	result["invalid"] = True
	return result


def recordEvent(events, event, renderEventFn=None):
	events.append(event)
	if renderEventFn is not None:
		renderEventFn(event)


def runHitFlow(shoe, playerHand, handTotal, readChoiceFn, renderEventFn=None):
	total = handTotal
	events = []
	while True:
		step = playerHitStep(shoe, playerHand)
		total = step.total
		recordEvent(events, step, renderEventFn)
		if step.bust:
			recordEvent(events, GameEvent(code="playerBustNow", total=total), renderEventFn)
			return StepOut(total=total, events=events)
		if total == 21:
			recordEvent(events, GameEvent(code="playerTwentyOne", total=total), renderEventFn)
			return StepOut(total=total, events=events)
		nextChoice = readChoiceFn("hitStand", total)
		if nextChoice.lower() == "h":
			continue
		recordEvent(events, GameEvent(code="playerStand", total=total), renderEventFn)
		return StepOut(total=total, events=events)


def runDdFlow(shoe, playerHand, renderEventFn=None):
	step = playerDoubleDownStep(shoe, playerHand)
	if renderEventFn is not None:
		renderEventFn(step)
	return StepOut(total=step.total, events=[step])


def runSplitHand(shoe, hand, handIdx, handTotal, startChoice, readChoiceFn, renderEventFn=None):
	total = handTotal
	betDbl = 0
	choice = startChoice
	events = []
	while True:
		result = resolveSplitHandIntent(choice, shoe, hand, total)
		total = result["total"]
		if result["invalid"]:
			recordEvent(events, GameEvent(code="splitInvalid", handIdx=handIdx), renderEventFn)
			return StepOut(total=total, betDbl=betDbl, events=events)
		if result["intent"] == "h":
			recordEvent(events, GameEvent(code="splitDraw", handIdx=handIdx, cardName=result["drawCard"], total=total), renderEventFn)
			if result["bust"]:
				recordEvent(events, GameEvent(code="splitBust", handIdx=handIdx, total=total), renderEventFn)
				return StepOut(total=total, betDbl=betDbl, events=events)
			choice = readChoiceFn("hitStand", total)
			continue
		if result["intent"] == "dd":
			betDbl = 1
			recordEvent(events, GameEvent(code="splitDd", handIdx=handIdx, cardName=result["drawCard"], total=total, bust=result["bust"]), renderEventFn)
			return StepOut(total=total, betDbl=betDbl, events=events)
		if result["intent"] == "s":
			recordEvent(events, GameEvent(code="splitStand", handIdx=handIdx, total=total), renderEventFn)
			return StepOut(total=total, betDbl=betDbl, events=events)


def runSplitFlow(shoe, playerHand, readChoiceFn, renderEventFn=None):
	splitStart = startSplitHands(shoe, playerHand)
	events = []
	recordEvent(events, GameEvent(code="splitStart", handIdx=1, cardName=splitStart["firstDrawCard"], total=splitStart["total1"]), renderEventFn)
	firstChoice = readChoiceFn("split1Start", splitStart["total1"])
	firstRes = runSplitHand(
		shoe,
		splitStart["hand1"],
		1,
		splitStart["total1"],
		firstChoice,
		readChoiceFn,
		renderEventFn,
	)
	events.extend(firstRes.events)
	recordEvent(events, GameEvent(code="splitStart", handIdx=2, cardName=splitStart["secondDrawCard"], total=splitStart["total2"]), renderEventFn)
	secondChoice = readChoiceFn("split2Start", splitStart["total2"])
	secondRes = runSplitHand(
		shoe,
		splitStart["hand2"],
		2,
		splitStart["total2"],
		secondChoice,
		readChoiceFn,
		renderEventFn,
	)
	events.extend(secondRes.events)
	return StepOut(
		total=0,
		handsplit=[firstRes.total, secondRes.total, firstRes.betDbl, secondRes.betDbl],
		events=events,
	)


def parsePlayerIntent(choice, canSplit):
	intent = choice.lower()
	if intent == "q":
		return {"intent": "quit", "invalid": False, "splitBlock": False}
	if intent == "sp":
		if canSplit:
			return {"intent": "split", "invalid": False, "splitBlock": False}
		return {"intent": "split", "invalid": True, "splitBlock": True}
	if intent == "h":
		return {"intent": "hit", "invalid": False, "splitBlock": False}
	if intent == "dd":
		return {"intent": "doubleDn", "invalid": False, "splitBlock": False}
	if intent == "su":
		return {"intent": "surrender", "invalid": False, "splitBlock": False}
	if intent == "s":
		return {"intent": "stand", "invalid": False, "splitBlock": False}
	return {"intent": "invalid", "invalid": True, "splitBlock": False}


def applyNonSplitIntent(state, intent, handTotal=None):
	if intent == "hit":
		applyAction(state, "h", handTotal=handTotal)
		return state
	if intent == "doubleDn":
		applyAction(state, "dd", handTotal=handTotal)
		return state
	if intent == "surrender":
		applyAction(state, "su", bankDelta=-(state.bet / 2))
		return state
	if intent == "stand":
		applyAction(state, "s")
		return state
	return state


def resolveTurnFlow(canSplit, state, shoe, readChoiceFn, renderEventFn=None):
	events = []
	while True:
		choice = readChoiceFn("playerAction", state.playerTotal, canSplit)
		intentRes = parsePlayerIntent(choice, canSplit)
		if intentRes["invalid"]:
			recordEvent(events, GameEvent(code="invalidChoice", splitBlock=intentRes["splitBlock"]), renderEventFn)
			continue
		intent = intentRes["intent"]
		if intent == "quit":
			return TurnFlow(state=state, events=events, quit=True)
		if intent == "hit":
			hitRes = runHitFlow(shoe, state.playerHand, state.playerTotal, readChoiceFn, renderEventFn)
			events.extend(hitRes.events)
			applyNonSplitIntent(state, intent, handTotal=hitRes.total)
			return TurnFlow(state=state, events=events, quit=False)
		if intent == "split":
			if state.bank - state.bet * 2 < 0:
				recordEvent(events, GameEvent(code="splitNoFunds"), renderEventFn)
				hitRes = runHitFlow(shoe, state.playerHand, state.playerTotal, readChoiceFn, renderEventFn)
				events.extend(hitRes.events)
				applyNonSplitIntent(state, "hit", handTotal=hitRes.total)
				return TurnFlow(state=state, events=events, quit=False)
			splitRes = runSplitFlow(shoe, state.playerHand, readChoiceFn, renderEventFn)
			events.extend(splitRes.events)
			applyAction(state, "sp", handsplit=splitRes.handsplit)
			return TurnFlow(state=state, events=events, quit=False)
		if intent == "doubleDn":
			ddRes = runDdFlow(shoe, state.playerHand, renderEventFn)
			events.extend(ddRes.events)
			applyNonSplitIntent(state, intent, handTotal=ddRes.total)
			return TurnFlow(state=state, events=events, quit=False)
		if intent == "surrender":
			applyNonSplitIntent(state, intent)
			return TurnFlow(state=state, events=events, quit=False)
		if intent == "stand":
			recordEvent(events, GameEvent(code="playerStand", total=state.playerTotal), renderEventFn)
			applyNonSplitIntent(state, intent)
			return TurnFlow(state=state, events=events, quit=False)


def parseBankInput(rawVal):
	try:
		value = int(rawVal)
	except ValueError:
		return {"ok": False, "value": None}
	return {"ok": True, "value": value}


def parseDeckCount(rawVal):
	try:
		value = int(rawVal)
	except ValueError:
		return {"ok": False, "value": None, "reason": "notNum"}
	if value < 1:
		return {"ok": False, "value": value, "reason": "tooLow"}
	if value > 6:
		return {"ok": False, "value": value, "reason": "tooHigh"}
	return {"ok": True, "value": value, "reason": "ok"}


def startSession(bank, deckAmt):
	return GameSession(
		bank=bank,
		initBank=bank,
		deckAmt=deckAmt,
		shoe=Shoe(deckAmt),
	)


def evaluateInitialBlackjack(playerTotal, dealerRawCards):
	playerBj = playerTotal == 21
	dealerBj = isBlackjack(dealerRawCards)
	if playerBj and dealerBj:
		return "push"
	if playerBj:
		return "playerBj"
	if dealerBj:
		return "dealerBj"
	return "none"


def resolveInsurance(upCardVal, tookIns, dealerBj, bet):
	if upCardVal != 1:
		if dealerBj:
			return InsOut(roundOver=True, bankDelta=-bet, result="dealerBj")
		return InsOut(roundOver=False, bankDelta=0, result="none")

	if tookIns:
		if dealerBj:
			return InsOut(roundOver=True, bankDelta=0, result="insWin")
		return InsOut(roundOver=False, bankDelta=-(bet // 2), result="insLose")

	if dealerBj:
		return InsOut(roundOver=True, bankDelta=-bet, result="dealerBj")

	return InsOut(roundOver=False, bankDelta=0, result="none")


@dataclass
class RoundState:
	bank: int
	bet: int
	playerHand: list = field(default_factory=list)
	dealerHand: list = field(default_factory=list)
	playerTotal: int = 0
	dealerTotal: int = 0
	playerCards: tuple = ("", "")
	dealerCards: tuple = ("", "")
	choice: str = ""
	handsplit: list = None
	charliePaid: bool = False


@dataclass
class GameSession:
	bank: int
	initBank: int
	deckAmt: int
	shoe: object
	bet: int = 0
	roundState: object = None


@dataclass
class RoundResolution:
	outcome: str
	bankDelta: int
	splitRes: list = None
	events: list = field(default_factory=list)


def dealRound(shoe, bank, bet):
	card1Name, card1Val = shoe.draw()
	card2Name, card2Val = shoe.draw()
	shoe.counter(card1Val)
	shoe.counter(card2Val)

	dCard1Name, dCard1Val = shoe.draw()
	dCard2Name, dCard2Val = shoe.draw()
	shoe.counter(dCard1Val)
	shoe.counter(dCard2Val)

	playerHand, playerTotal = startHand(card1Val, card2Val)
	dealerHand = [dCard1Val, dCard2Val]
	dealerTotal = handValue([11 if card == 1 else card for card in dealerHand])

	return RoundState(
		bank=bank,
		bet=bet,
		playerHand=playerHand,
		dealerHand=dealerHand,
		playerTotal=playerTotal,
		dealerTotal=dealerTotal,
		playerCards=(card1Name, card2Name),
		dealerCards=(dCard1Name, dCard2Name),
	)


def applyAction(state, choice, handTotal=None, handsplit=None, bankDelta=0):
	state.choice = choice
	if handTotal is not None:
		state.playerTotal = handTotal
	if handsplit is not None:
		state.handsplit = handsplit
	state.bank += bankDelta
	return state


def evalTurnOut(state, dealerTotal):
	if state.choice == "su":
		return StepOut(total=0, events=[GameEvent(code="playerSurr", dealerTotal=dealerTotal)])
	if state.playerTotal >= 22:
		return StepOut(total=0, events=[GameEvent(code="playerBust", dealerTotal=dealerTotal)])
	return StepOut(total=0, events=[])


def resolveRound(state, dealerTotal):
	if state.choice == "sp" and state.handsplit and state.bank - state.bet * 2 >= 0:
		hand1, hand2, betDbl1, betDbl2 = state.handsplit
		outcome1, delta1 = settleSplitHand(hand1, dealerTotal, state.bet, doubled=(betDbl1 == 1))
		outcome2, delta2 = settleSplitHand(hand2, dealerTotal, state.bet, doubled=(betDbl2 == 1))
		return RoundResolution(
			outcome="split",
			bankDelta=delta1 + delta2,
			splitRes=[(outcome1, delta1), (outcome2, delta2)],
			events=[
				GameEvent(code="splitHandRes", handIdx=1, outcome=outcome1),
				GameEvent(code="splitHandRes", handIdx=2, outcome=outcome2),
			],
		)

	outcome = compareHandTotals(state.playerTotal, dealerTotal)
	delta = bankrollDelta(
		outcome,
		state.bet,
		doubled=(state.choice == "dd"),
		charliePaid=state.charliePaid,
	)
	if outcome == "lose":
		events = [GameEvent(code="playerLose")]
	elif outcome == "push":
		events = [GameEvent(code="playerPush")]
	elif dealerTotal >= 22 and state.playerTotal <= 21:
		events = [GameEvent(code="dealerBustWin", dealerTotal=dealerTotal)]
	else:
		events = [GameEvent(code="playerWin")]
	return RoundResolution(outcome=outcome, bankDelta=delta, splitRes=None, events=events)


class Shoe:
	def __init__(self, deckAmt):
		self.deckAmt = deckAmt
		self.deck = deckGenerator()
		self.discard = []
		self.cardCnt = 0
		self.countNow = 0

	def draw(self):
		if self.deckAmt == 1:
			card, cardVal = random.choice(list(self.deck.items()))
			del self.deck[card]
			return card, cardVal

		while True:
			card, cardVal = random.choice(list(self.deck.items()))
			if self.discard.count(card) == self.deckAmt:
				del self.deck[card]
				continue
			self.discard.append(card)
			return card, cardVal

	def counter(self, card):
		if card in range(2, 7):
			self.cardCnt += 1
		elif card >= 10:
			self.cardCnt -= 1

		cardsLeft = len(self.deck)
		if cardsLeft >= 260:
			trueCnt = 6
		elif 208 <= cardsLeft < 260:
			trueCnt = 5
		elif 156 <= cardsLeft < 208:
			trueCnt = 4
		elif 104 <= cardsLeft < 156:
			trueCnt = 3
		elif 52 <= cardsLeft < 104:
			trueCnt = 2
		else:
			trueCnt = 1

		self.countNow = self.cardCnt // trueCnt
		return self.countNow

	def reset(self):
		self.deck = deckGenerator()
		self.discard = []
		self.cardCnt = 0
		self.countNow = 0
