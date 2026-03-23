#!/usr/bin/env python3

import os
from engine import dealRound, handValue, isBlackjack
from engine import evaluateInitialBlackjack, resolveInsurance, resolveRound
from engine import evalTurnOut
from engine import playDealerTurn, resolveTurnFlow
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

def playerActionPrompt(canSplit):
	if canSplit:
		print("Hit(h), Split(sp), Double Down(dd), Surrender(su), or Stand(s)?\n(q) to Quit.")
	else:
		print("Hit(h), Double Down(dd), Surrender(su), or Stand(s)?\n(q) to Quit.")
	return readInput(">  ")


def readTurnChoice(promptKey, total, canSplit=False):
	if promptKey == "playerAction":
		return playerActionPrompt(canSplit)
	if promptKey == "split1Start":
		print("Hit, Double Down,  or stand on your first hand?")
		return readInput(">")
	if promptKey == "split2Start":
		print("Hit, Double Down, or stand?")
		return readInput(">")
	print(uiTxt["hitStand"])
	return readInput(">")


def renderPlayEvent(event):
	code = event["code"]
	if code == "invalidChoice":
		if event["splitBlock"]:
			print(uiTxt["splitBlk"])
		else:
			print(uiTxt["cantDo"])
	elif code == "splitNoFunds":
		print(uiTxt["noFundsSplit"])
	elif code == "playerDraw":
		print("You drew the {card} and now have {hand}.".format(card=event["cardName"], hand=event["total"]))
	elif code == "playerTwentyOne":
		print("Sanding on 21, stop hitting me!")
	elif code == "playerStand":
		print("You stand on {}.".format(event["total"]))
	elif code == "playerDd":
		print("You doubled down and drew the {draw} and now have {hand}. Good luck!".format(draw=event["cardName"], hand=event["total"]))
	elif code == "splitStart":
		if event["handIdx"] == 1:
			print("You split and draw the {card1} for your first hand, a total of {hand}.".format(card1=event["cardName"], hand=event["total"]))
		else:
			print("You drew the {card2} for your second hand and now have {hand}.".format(card2=event["cardName"], hand=event["total"]))
	elif code == "splitDraw":
		print("You drew the {card} and now have {hand}.".format(card=event["cardName"], hand=event["total"]))
	elif code == "splitBust":
		if event["handIdx"] == 1:
			print("You bust on your first hand with {}!.".format(event["total"]))
		else:
			print("You bust on your second hand with {}!.".format(event["total"]))
	elif code == "splitDd":
		if event["handIdx"] == 1:
			if event["bust"]:
				print("You drew the {card} and bust with {hand}!".format(card=event["cardName"], hand=event["total"]))
			else:
				print("You double down on your first hand  and draw a {card} for a total of {hand}. Good luck!".format(card=event["cardName"], hand=event["total"]))
		else:
			if event["bust"]:
				print("You drew the {card} and bust with {hand}!".format(card=event["cardName"], hand=event["total"]))
			else:
				print("You doubled down on your second hand and drew the {card} for a total of {hand}. Good luck!".format(card=event["cardName"], hand=event["total"]))
	elif code == "splitStand":
		if event["handIdx"] == 1:
			print("You stand on your first hand with {}.".format(event["total"]))
		else:
			print("You stand on your second hand with a total of {}.".format(event["total"]))


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
	d2 = dealerHand[1]
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
	turnRes = resolveTurnFlow(
		card1.split()[0] == card2.split()[0],
		state,
		shoe,
		readTurnChoice,
	)
	for event in turnRes["events"]:
		renderPlayEvent(event)
	if turnRes["quit"]:
		quitGame()
	state = turnRes["state"]
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
