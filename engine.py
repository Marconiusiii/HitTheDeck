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
	returnAmt: int = 0


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


class ActionType:
	hit = "hit"
	stand = "stand"
	doubleDn = "doubleDn"
	split = "split"
	surrender = "surrender"
	quit = "quit"
	invalid = "invalid"


class RoundPhase:
	deal = "deal"
	insurance = "insurance"
	playerTurn = "playerTurn"
	dealerTurn = "dealerTurn"
	settle = "settle"
	roundOver = "roundOver"


@dataclass
class ActionChoice:
	action: str
	invalid: bool = False
	splitBlock: bool = False
	rawVal: str = ""


@dataclass
class ActionReq:
	reqType: str
	total: int = 0
	handIdx: int = 0
	canSplit: bool = False
	actions: tuple = ()


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


def splitChoiceVal(choice):
	if hasattr(choice, "action"):
		return choice.action
	if isinstance(choice, str):
		rawVal = choice.lower()
		if rawVal == "h":
			return ActionType.hit
		if rawVal == "dd":
			return ActionType.doubleDn
		if rawVal == "s":
			return ActionType.stand
		return rawVal
	return ActionType.invalid


def resolveSplitHandIntent(choice, shoe, hand, curTotal):
	intent = splitChoiceVal(choice)
	result = {
		"intent": intent,
		"total": curTotal,
		"doubled": False,
		"drawCard": None,
		"bust": False,
		"complete": False,
		"invalid": False,
	}
	if intent == ActionType.hit:
		step = playerHitStep(shoe, hand)
		result["total"] = step.total
		result["drawCard"] = step.cardName
		result["bust"] = step.bust
		result["complete"] = step.bust
		return result
	if intent == ActionType.doubleDn:
		step = playerDoubleDownStep(shoe, hand)
		result["total"] = step.total
		result["drawCard"] = step.cardName
		result["bust"] = step.bust
		result["doubled"] = True
		result["complete"] = True
		return result
	if intent == ActionType.stand:
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
		nextChoice = readChoiceFn(ActionReq(
			reqType="hitStand",
			total=total,
			actions=(ActionType.hit, ActionType.stand),
		))
		if nextChoice.action == ActionType.hit:
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
		if result["intent"] == ActionType.hit:
			recordEvent(events, GameEvent(code="splitDraw", handIdx=handIdx, cardName=result["drawCard"], total=total), renderEventFn)
			if result["bust"]:
				recordEvent(events, GameEvent(code="splitBust", handIdx=handIdx, total=total), renderEventFn)
				return StepOut(total=total, betDbl=betDbl, events=events)
			if total == 21:
				recordEvent(events, GameEvent(code="splitTwentyOne", handIdx=handIdx, total=total), renderEventFn)
				recordEvent(events, GameEvent(code="splitStand", handIdx=handIdx, total=total), renderEventFn)
				return StepOut(total=total, betDbl=betDbl, events=events)
			choice = readChoiceFn(ActionReq(
				reqType="hitStand",
				total=total,
				handIdx=handIdx,
				actions=(ActionType.hit, ActionType.stand),
			))
			continue
		if result["intent"] == ActionType.doubleDn:
			betDbl = 1
			recordEvent(events, GameEvent(code="splitDd", handIdx=handIdx, cardName=result["drawCard"], total=total, bust=result["bust"]), renderEventFn)
			return StepOut(total=total, betDbl=betDbl, events=events)
		if result["intent"] == ActionType.stand:
			recordEvent(events, GameEvent(code="splitStand", handIdx=handIdx, total=total), renderEventFn)
			return StepOut(total=total, betDbl=betDbl, events=events)


def runSplitFlow(shoe, playerHand, readChoiceFn, renderEventFn=None):
	splitStart = startSplitHands(shoe, playerHand)
	events = []
	recordEvent(events, GameEvent(code="splitStart", handIdx=1, cardName=splitStart["firstDrawCard"], total=splitStart["total1"]), renderEventFn)
	firstChoice = readChoiceFn(ActionReq(
		reqType="splitStart",
		total=splitStart["total1"],
		handIdx=1,
		actions=(ActionType.hit, ActionType.doubleDn, ActionType.stand),
	))
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
	secondChoice = readChoiceFn(ActionReq(
		reqType="splitStart",
		total=splitStart["total2"],
		handIdx=2,
		actions=(ActionType.hit, ActionType.doubleDn, ActionType.stand),
	))
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
		return ActionChoice(action=ActionType.quit, rawVal=choice)
	if intent == "sp":
		if canSplit:
			return ActionChoice(action=ActionType.split, rawVal=choice)
		return ActionChoice(action=ActionType.split, invalid=True, splitBlock=True, rawVal=choice)
	if intent == "h":
		return ActionChoice(action=ActionType.hit, rawVal=choice)
	if intent == "dd":
		return ActionChoice(action=ActionType.doubleDn, rawVal=choice)
	if intent == "su":
		return ActionChoice(action=ActionType.surrender, rawVal=choice)
	if intent == "s":
		return ActionChoice(action=ActionType.stand, rawVal=choice)
	return ActionChoice(action=ActionType.invalid, invalid=True, rawVal=choice)


def applyNonSplitIntent(state, intent, handTotal=None):
	if intent == ActionType.hit:
		applyAction(state, "h", handTotal=handTotal)
		return state
	if intent == ActionType.doubleDn:
		applyAction(state, "dd", handTotal=handTotal)
		return state
	if intent == ActionType.surrender:
		applyAction(state, "su", bankDelta=-(state.bet // 2))
		return state
	if intent == ActionType.stand:
		applyAction(state, "s")
		return state
	return state


def resolveTurnFlow(canSplit, state, shoe, readChoiceFn, renderEventFn=None):
	events = []
	turnActs = [ActionType.hit, ActionType.doubleDn, ActionType.stand]
	if state.deckAmt == 6:
		turnActs.insert(2, ActionType.surrender)
	if canSplit:
		turnActs.append(ActionType.split)
	while True:
		choice = readChoiceFn(ActionReq(
			reqType="playerAction",
			total=state.playerTotal,
			canSplit=canSplit,
			actions=tuple(turnActs),
		))
		if choice.invalid:
			recordEvent(events, GameEvent(code="invalidChoice", splitBlock=choice.splitBlock), renderEventFn)
			continue
		intent = choice.action
		if intent == ActionType.quit:
			return TurnFlow(state=state, events=events, quit=True)
		if intent == ActionType.hit:
			hitRes = runHitFlow(shoe, state.playerHand, state.playerTotal, readChoiceFn, renderEventFn)
			events.extend(hitRes.events)
			applyNonSplitIntent(state, intent, handTotal=hitRes.total)
			return TurnFlow(state=state, events=events, quit=False)
		if intent == ActionType.split:
			if state.bank - state.bet * 2 < 0:
				recordEvent(events, GameEvent(code="splitNoFunds"), renderEventFn)
				hitRes = runHitFlow(shoe, state.playerHand, state.playerTotal, readChoiceFn, renderEventFn)
				events.extend(hitRes.events)
				applyNonSplitIntent(state, ActionType.hit, handTotal=hitRes.total)
				return TurnFlow(state=state, events=events, quit=False)
			splitRes = runSplitFlow(shoe, state.playerHand, readChoiceFn, renderEventFn)
			events.extend(splitRes.events)
			applyAction(state, "sp", handsplit=splitRes.handsplit)
			return TurnFlow(state=state, events=events, quit=False)
		if intent == ActionType.doubleDn:
			ddRes = runDdFlow(shoe, state.playerHand, renderEventFn)
			events.extend(ddRes.events)
			applyNonSplitIntent(state, intent, handTotal=ddRes.total)
			return TurnFlow(state=state, events=events, quit=False)
		if intent == ActionType.surrender:
			applyNonSplitIntent(state, intent)
			return TurnFlow(state=state, events=events, quit=False)
		if intent == ActionType.stand:
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
	deckAmt: int = 1
	playerHand: list = field(default_factory=list)
	dealerHand: list = field(default_factory=list)
	playerTotal: int = 0
	dealerTotal: int = 0
	playerCards: tuple = ("", "")
	dealerCards: tuple = ("", "")
	choice: str = ""
	handsplit: list = None
	charliePaid: bool = False
	phase: str = RoundPhase.deal


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


def dealRound(shoe, bank, bet, deckAmt=1):
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
		deckAmt=deckAmt,
		playerHand=playerHand,
		dealerHand=dealerHand,
		playerTotal=playerTotal,
		dealerTotal=dealerTotal,
		playerCards=(card1Name, card2Name),
		dealerCards=(dCard1Name, dCard2Name),
		phase=RoundPhase.deal,
	)


def applyAction(state, choice, handTotal=None, handsplit=None, bankDelta=0):
	state.choice = choice
	if handTotal is not None:
		state.playerTotal = handTotal
	if handsplit is not None:
		state.handsplit = handsplit
	state.bank += bankDelta
	return state


def setPhase(state, phase):
	state.phase = phase
	return state


def startRound(session):
	state = dealRound(session.shoe, session.bank, session.bet, session.deckAmt)
	state.charliePaid = False
	initBj = evaluateInitialBlackjack(state.playerTotal, state.dealerHand)
	if initBj != "none":
		state.phase = RoundPhase.roundOver
	elif state.dealerHand[1] == 1:
		state.phase = RoundPhase.insurance
	else:
		state.phase = RoundPhase.playerTurn
	session.roundState = state
	return state, initBj


def applyInsPhase(state, tookIns):
	dealerBj = isBlackjack(state.dealerHand)
	insRes = resolveInsurance(state.dealerHand[1], tookIns, dealerBj, state.bet)
	state.bank += insRes.bankDelta
	if insRes.roundOver:
		state.phase = RoundPhase.roundOver
	else:
		state.phase = RoundPhase.playerTurn
	return insRes


def applyTurnPhase(state, shoe, readChoiceFn, renderEventFn=None):
	turnRes = resolveTurnFlow(
		cardRank(state.playerCards[0]) == cardRank(state.playerCards[1]),
		state,
		shoe,
		readChoiceFn,
		renderEventFn,
	)
	if not turnRes.quit:
		turnOut = evalTurnOut(turnRes.state, turnRes.state.dealerTotal)
		if turnOut.events:
			turnRes.state.phase = RoundPhase.roundOver
		else:
			turnRes.state.phase = RoundPhase.dealerTurn
	return turnRes


def applyDealerPhase(state, shoe):
	dealerRes = playDealerTurn(shoe, state.dealerHand)
	state.dealerTotal = dealerRes.total
	state.phase = RoundPhase.settle
	return dealerRes


def applySettlePhase(state):
	resolution = resolveRound(state, state.dealerTotal)
	state.bank += resolution.bankDelta
	state.phase = RoundPhase.roundOver
	return resolution


def evalTurnOut(state, dealerTotal):
	if state.choice == "su":
		return StepOut(total=0, events=[GameEvent(code="playerSurr", dealerTotal=dealerTotal, returnAmt=state.bet // 2)])
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
