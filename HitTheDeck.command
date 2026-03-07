#!/usr/bin/env python3

import os
from engine import applyAction, canSplitCards, dealRound, handValue, isBlackjack
from engine import applyNonSplitIntent, parsePlayerIntent
from engine import evaluateInitialBlackjack, resolveInsurance, resolveRound
from engine import evalTurnOut
from engine import playDealerTurn, playerDoubleDownStep, playerHitStep, startSplitHands
from engine import resolveSplitHandIntent
from engine import parseBankInput, parseDeckCount, startSession
from ui import pickLoseMsg, promptIns, renderInitBj, renderInsRes, renderRoundEvent, uiTxt

# Version Number
version = "5.0.0"

def quitGame():
	global bank, initBank
	if bank > initBank:
		print("\nNice work coloring up! Come back soon!\n")
	elif bank == initBank:
		print("\nWell, at least you didn't lose anything! Try again soon!\n")
	else:
		print("\nOops, tough loss today. Better luck next time!\n")
	raise SystemExit

def clearScreen():
	os.system('cls' if os.name == 'nt' else 'clear')

def readInput(promptTxt):
	while True:
		userIn = input(promptTxt)
		if userIn.lower() == "cl":
			clearScreen()
			continue
		return userIn

def runStepLoop(stepFn):
	while True:
		loopRes = stepFn()
		if loopRes["done"]:
			return loopRes

def runChoiceLoop(startChoice, stepFn):
	choice = startChoice
	while True:
		loopRes = stepFn(choice)
		if loopRes["done"]:
			return loopRes
		choice = loopRes["nextChoice"]

# Hit function
def hit(playerHand, handVal, shoe):
	def doStep():
		nonlocal handVal
		step = playerHitStep(shoe, playerHand)
		print("You drew the {card} and now have {hand}.".format(card=step["cardName"], hand=step["total"]))
		handVal = step["total"]
		if step["bust"]:
			return {"done": True}
		elif step["blackjack"]:
			print("Sanding on 21, stop hitting me!")
			return {"done": True}
		#print("True Count: {}".format(shoe.countNow))
		print(uiTxt["hitStand"])
		hitAgain = readInput(">")
		if hitAgain == 'h':
			return {"done": False}
		print("You stand on {}.".format(handVal))
		return {"done": True}
	runStepLoop(doStep)
	return handVal

#Double Down function
def doubleDown(playerHand, handVal, shoe):
	step = playerDoubleDownStep(shoe, playerHand)
	print("You doubled down and drew the {draw} and now have {hand}. Good luck!".format(draw=step["cardName"], hand=step["total"]))
	return step["total"]

#Dealer engine
def dealer(dCard1, dCard2, dealerHand, shoe):
	openTotal = handValue([11 if card == 1 else card for card in dealerHand])
	dealerRes = playDealerTurn(shoe, dealerHand)
	dVal = handValue(dealerHand)
	print("Dealer has the {card1} and the {card2} for a total of {dealer}.".format(card1=dCard2, card2=dCard1, dealer=openTotal))
	if dealerRes["events"]:
		for event in dealerRes["events"]:
			print("Dealer draws the {card} for a total of {hand}.".format(card=event["cardName"], hand=event["total"]))
		if 17 <= dealerRes["finalTotal"] <= 21:
			print("Dealer stands with {}.".format(dealerRes["finalTotal"]))
	else:
		print("Dealer stands on {}.".format(dVal))
	return dealerRes["finalTotal"]

# Split function
def split(playerHand, shoe):
	betDouble1 = betDouble2 = 0
	splitStart = startSplitHands(shoe, playerHand)
	spCard1 = splitStart["firstDrawCard"]
	spCard2 = splitStart["secondDrawCard"]
	handSP1 = splitStart["hand1"]
	handSP2 = splitStart["hand2"]
	hand1 = splitStart["total1"]
	hand2 = splitStart["total2"]
	print("You split and draw the {card1} for your first hand, a total of {hand}.".format(card1=spCard1, hand=hand1))
	print("Hit, Double Down,  or stand on your first hand?")
	h1 = readInput(">")
	def stepHand1(choice):
		nonlocal hand1, betDouble1
		result1 = resolveSplitHandIntent(choice, shoe, handSP1, hand1)
		hand1 = result1["total"]
		if result1["invalid"]:
			return {"done": True}
		if result1["intent"] == "h":
			print("You drew the {card} and now have {hand}.".format(card=result1["drawCard"], hand=hand1))
			if result1["bust"]:
				print("You bust on your first hand with {}!.".format(hand1))
				return {"done": True}
			print(uiTxt["hitStand"])
			return {"done": False, "nextChoice": readInput(">")}
		if result1["intent"] == "dd":
			betDouble1 += 1
			if result1["bust"]:
				print("You drew the {card} and bust with {hand}!".format(card=result1["drawCard"], hand=hand1))
			else:
				print("You double down on your first hand  and draw a {card} for a total of {hand}. Good luck!".format(card=result1["drawCard"], hand=hand1))
			return {"done": True}
		if result1["intent"] == "s":
			print("You stand on your first hand with {}.".format(hand1))
			return {"done": True}
		return {"done": True}
	runChoiceLoop(h1, stepHand1)
	print("You drew the {card2} for your second hand and now have {hand}.".format(card2=spCard2, hand=hand2))
	print("Hit, Double Down, or stand?")
	h2 = readInput(">")
	def stepHand2(choice):
		nonlocal hand2, betDouble2
		result2 = resolveSplitHandIntent(choice, shoe, handSP2, hand2)
		hand2 = result2["total"]
		if result2["invalid"]:
			return {"done": True}
		if result2["intent"] == "h":
			print("You drew the {card} and now have {hand}.".format(card=result2["drawCard"], hand=hand2))
			if result2["bust"]:
				print("You bust on your second hand with {}!.".format(hand2))
				return {"done": True}
			print(uiTxt["hitStand"])
			return {"done": False, "nextChoice": readInput(">")}
		if result2["intent"] == "dd":
			betDouble2 += 1
			if result2["bust"]:
				print("You drew the {card} and bust with {hand}!".format(card=result2["drawCard"], hand=hand2))
			else:
				print("You doubled down on your second hand and drew the {card} for a total of {hand}. Good luck!".format(card=result2["drawCard"], hand=hand2))
			return {"done": True}
		if result2["intent"] == "s":
			print("You stand on your second hand with a total of {}.".format(hand2))
			return {"done": True}
		return {"done": True}
	runChoiceLoop(h2, stepHand2)

	return [hand1, hand2, betDouble1, betDouble2]


def playerActionPrompt(canSplit):
	if canSplit:
		print("Hit(h), Split(sp), Double Down(dd), Surrender(su), or Stand(s)?\n(q) to Quit.")
	else:
		print("Hit(h), Double Down(dd), Surrender(su), or Stand(s)?\n(q) to Quit.")
	return readInput(">  ")


def resolvePlayerTurn(canSplit, state, dVal, shoe):
	while True:
		choice = playerActionPrompt(canSplit)
		intentRes = parsePlayerIntent(choice, canSplit)
		if intentRes["invalid"]:
			if intentRes["splitBlock"]:
				print(uiTxt["splitBlk"])
			else:
				print(uiTxt["cantDo"])
			continue
		intent = intentRes["intent"]
		if intent == "quit":
			quitGame()
		elif intent == "hit":
			handVal = hit(state.playerHand, state.playerTotal, shoe)
			applyNonSplitIntent(state, intent, handTotal=handVal)
			break
		elif intent == "split":
			if state.bank - state.bet*2 < 0:
				print(uiTxt["noFundsSplit"])
				handVal = hit(state.playerHand, state.playerTotal, shoe)
				applyNonSplitIntent(state, "hit", handTotal=handVal)
			else:
				handsplit = split(state.playerHand, shoe)
				applyAction(state, "sp", handsplit=handsplit)
			break
		elif intent == "doubleDn":
			handVal = doubleDown(state.playerHand, state.playerTotal, shoe)
			applyNonSplitIntent(state, intent, handTotal=handVal)
			break
		elif intent == "surrender":
			applyNonSplitIntent(state, intent)
			break
		elif intent == "stand":
			print("You stand on {}.".format(state.playerTotal))
			applyNonSplitIntent(state, intent)
			break
	return state


def resolveDealerPhase(state, dVal):
	resolution = resolveRound(state, dVal)
	for event in resolution.events:
		renderRoundEvent(event)
	state.bank += resolution.bankDelta
	return state

def resolveRoundEnd(state, dVal, dCard1, dCard2, dealerHand, playerHand, bet, shoe):
	turnOut = evalTurnOut(state, dVal)
	if turnOut["roundOver"]:
		renderRoundEvent(turnOut["event"])
		if turnOut["event"]["code"] == "playerBust":
			state.bank -= bet
		return state
	if len(playerHand) >= 5:
		print("You just hit up to a 5 Card Charlie! Even money coming to you!")
		state.bank += bet
		print("You now have ${} in your bank!".format(state.bank))
		state.charliePaid = True
	dVal = dealer(dCard1, dCard2, dealerHand, shoe)
	state.dealerTotal = dVal
	return resolveDealerPhase(state, dVal)

def setupSession():
	print("Hit the Deck! v.{}\n\t\tBy: Marco Salsiccia".format(version))
	print("How much would you like to cash in for your bank?")
	while True:
		bankRes = parseBankInput(readInput("$"))
		if bankRes["ok"]:
			bank = bankRes["value"]
			break
		print("That wasn't a number, doofus.")
	print("Great, starting off with ${bank}. And how many decks?".format(bank=bank))
	while True:
		deckRes = parseDeckCount(readInput("Please choose 1-6 Decks >"))
		if not deckRes["ok"] and deckRes["reason"] == "notNum":
			print("That wasn't a number between 1-6! That wasn't even a number! Try again you silly goose.")
			continue
		deckCnt = deckRes["value"]
		if deckCnt == 1:
			print("Starting a single deck game. Good luck!")
			break
		elif 2 <= deckCnt <= 6:
			print("Starting a game with {} decks. Good luck!".format(deckCnt))
			break
		elif not deckRes["ok"] and deckRes["reason"] == "tooHigh":
			print("Too many decks! The card shoe explodes and you are felled by playing card papercuts. Good job! Try again.")
			continue
		elif not deckRes["ok"] and deckRes["reason"] == "tooLow":
			print("What are you trying to do? Not play Blackjack? Add some cards, you dork!")
			continue
		else:
			print("That wasn't a number between 1 and 6! It wasn't even a number! Try again, you silly goose.")
			continue
	session = startSession(bank, deckCnt)
	return session, deckCnt

def runBetFlow(bank, bet):
	while True:
		if bank <= 0:
			print(uiTxt["outMoney1"])
			print(uiTxt["outMoney2"])
			while True:
				addCash = readInput("$")
				if addCash.lower() == "q":
					quitGame()
				try:
					bank += +int(addCash)
				except ValueError:
					print("That wasn't a number, try again.")
					continue
				if bank < 0:
					print("You fail at math. Try again!")
					bank = 0
					continue
				print("Great, starting you off again with ${}.".format(bank))
				break
		if bet == 0:
			print(uiTxt["betAsk"].format(bank))
		else:
			print(uiTxt["betAskRpt"].format(bank=bank, bet=bet))
		betIn = readInput("$?")
		if betIn.lower() == "q":
			quitGame()
		try:
			nextBet = int(betIn)
		except ValueError:
			if bet == 0:
				print(uiTxt["betNone"])
				continue
			nextBet = bet
		if nextBet > bank:
			print("You simply don't have the funds for a bet that size!")
			continue
		print("You bet ${bet}.".format(bet=nextBet))
		return bank, nextBet

def runRoundFlow(shoe, bank, bet):
	if len(shoe.deck) < 15:
		shoe.reset()
		print("\nShuffling!\n")
		shoe.countNow = 0
	state = dealRound(shoe, bank, bet)
	state.charliePaid = False
	card1, card2 = state.playerCards
	dCard1, dCard2 = state.dealerCards
	playerHand = state.playerHand
	handVal = state.playerTotal
	dealerHand = state.dealerHand
	d1, d2 = dealerHand
	dVal = state.dealerTotal
	dealerBlackjack = isBlackjack(dealerHand)
	initBj = evaluateInitialBlackjack(state.playerTotal, dealerHand)
	if renderInitBj(initBj, state, card1, card2):
		return state.bank
	print("You drew the {card1} and the {card2} for a total of {hand}.\nDealer is showing {dealer}.".format(card1=card1, card2=card2, hand=handVal, dealer=dCard2))
	if d2 == 1:
		tookIns = promptIns(readInput)
		insRes = resolveInsurance(d2, tookIns, dealerBlackjack, bet)
		state.bank += insRes["bankDelta"]
		renderInsRes(insRes, bet)
		if insRes["roundOver"]:
			return state.bank
	else:
		dealerRes = resolveInsurance(d2, False, dealerBlackjack, bet)
		if dealerRes["roundOver"]:
			print("Dealer has Blackjack.\n{}".format(pickLoseMsg()))
			state.bank += dealerRes["bankDelta"]
			return state.bank
	canSplit = canSplitCards(card1, card2)
	state = resolvePlayerTurn(canSplit, state, dVal, shoe)
	state = resolveRoundEnd(state, dVal, dCard1, dCard2, dealerHand, playerHand, bet, shoe)
	return state.bank

bet = 0
bank = initBank = 0

# Game starts here
session, deckAmount = setupSession()
shuffle = deckAmount * 52 - 20
shoe = session["shoe"]
bank = session["bank"]
initBank = session["initBank"]

#Play Begins
while True:
	bank, bet = runBetFlow(bank, bet)
	bank = runRoundFlow(shoe, bank, bet)
	continue
