#!/usr/bin/env python3

import os
from engine import ActionChoice, ActionType, dealRound, handValue, isBlackjack
from engine import RoundPhase, applyInsPhase, applySettlePhase
from engine import applyTurnPhase, evalTurnOut, evaluateInitialBlackjack, parseBankInput
from engine import parseDeckCount, parsePlayerIntent, playDealerTurn, startRound
from engine import startSession
from ui import pickLoseMsg, promptIns, renderInitBj, renderInsRes, renderRoundEvent, uiTxt

# Version Number
version = "5.0.0"

def quitGame():
	global session
	if session.bank > session.initBank:
		print("\nNice work coloring up! Come back soon!\n")
	elif session.bank == session.initBank:
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
	if dealerRes.events:
		for event in dealerRes.events:
			print("Dealer draws the {card} for a total of {hand}.".format(card=event.cardName, hand=event.total))
		if 17 <= dealerRes.total <= 21:
			print("Dealer stands with {}.".format(dealerRes.total))
	else:
		print("Dealer stands on {}.".format(dVal))
	return dealerRes.total

def playerActionPrompt(actionReq):
	acts = []
	if ActionType.hit in actionReq.actions:
		acts.append("Hit(h)")
	if ActionType.split in actionReq.actions:
		acts.append("Split(sp)")
	if ActionType.doubleDn in actionReq.actions:
		acts.append("Double Down(dd)")
	if ActionType.surrender in actionReq.actions:
		acts.append("Surrender(su)")
	if ActionType.stand in actionReq.actions:
		acts.append("Stand(s)")
	if len(acts) == 1:
		promptTxt = acts[0]
	else:
		promptTxt = ", ".join(acts[:-1]) + ", or " + acts[-1]
	print("{}?\n(q) to Quit.".format(promptTxt))
	return readInput(">  ")


def readTurnChoice(actionReq):
	if actionReq.reqType == "playerAction":
		choice = parsePlayerIntent(playerActionPrompt(actionReq), actionReq.canSplit)
		if not choice.invalid and choice.action != ActionType.quit and choice.action not in actionReq.actions:
			return ActionChoice(action=ActionType.invalid, invalid=True, rawVal=choice.rawVal)
		return choice
	if actionReq.reqType == "splitStart" and actionReq.handIdx == 1:
		print("Hit, Double Down,  or stand on your first hand?")
		return parsePlayerIntent(readInput(">"), False)
	if actionReq.reqType == "splitStart":
		print("Hit, Double Down, or stand?")
		return parsePlayerIntent(readInput(">"), False)
	print(uiTxt["hitStand"])
	rawVal = readInput(">")
	if rawVal.lower() == "h":
		return ActionChoice(action=ActionType.hit, rawVal=rawVal)
	if rawVal.lower() == "s":
		return ActionChoice(action=ActionType.stand, rawVal=rawVal)
	return ActionChoice(action=ActionType.stand, rawVal=rawVal)


def renderPlayEvent(event):
	code = event.code
	if code == "invalidChoice":
		if event.splitBlock:
			print(uiTxt["splitBlk"])
		else:
			print(uiTxt["cantDo"])
	elif code == "splitNoFunds":
		print(uiTxt["noFundsSplit"])
	elif code == "playerDraw":
		print("You drew the {card} and now have {hand}.".format(card=event.cardName, hand=event.total))
	elif code == "playerTwentyOne":
		print("Sanding on 21, stop hitting me!")
	elif code == "playerStand":
		print("You stand on {}.".format(event.total))
	elif code == "playerDd":
		print("You doubled down and drew the {draw} and now have {hand}. Good luck!".format(draw=event.cardName, hand=event.total))
	elif code == "splitStart":
		if event.handIdx == 1:
			print("You split and draw the {card1} for your first hand, a total of {hand}.".format(card1=event.cardName, hand=event.total))
		else:
			print("You drew the {card2} for your second hand and now have {hand}.".format(card2=event.cardName, hand=event.total))
	elif code == "splitDraw":
		print("You drew the {card} and now have {hand}.".format(card=event.cardName, hand=event.total))
	elif code == "splitTwentyOne":
		print("Sanding on 21, stop hitting me!")
	elif code == "splitBust":
		if event.handIdx == 1:
			print("You bust on your first hand with {}!.".format(event.total))
		else:
			print("You bust on your second hand with {}!.".format(event.total))
	elif code == "splitDd":
		if event.handIdx == 1:
			if event.bust:
				print("You drew the {card} and bust with {hand}!".format(card=event.cardName, hand=event.total))
			else:
				print("You double down on your first hand  and draw a {card} for a total of {hand}. Good luck!".format(card=event.cardName, hand=event.total))
		else:
			if event.bust:
				print("You drew the {card} and bust with {hand}!".format(card=event.cardName, hand=event.total))
			else:
				print("You doubled down on your second hand and drew the {card} for a total of {hand}. Good luck!".format(card=event.cardName, hand=event.total))
	elif code == "splitStand":
		if event.handIdx == 1:
			print("You stand on your first hand with {}.".format(event.total))
		else:
			print("You stand on your second hand with a total of {}.".format(event.total))


def resolveDealerPhase(state, dVal):
	state.dealerTotal = dVal
	resolution = applySettlePhase(state)
	for event in resolution.events:
		renderRoundEvent(event)
	return state

def resolveRoundEnd(state, dVal, dCard1, dCard2, dealerHand, playerHand, bet, shoe):
	turnOut = evalTurnOut(state, dVal)
	if turnOut.events:
		renderRoundEvent(turnOut.events[0])
		if turnOut.events[0].code == "playerBust":
			state.bank -= bet
		state.phase = RoundPhase.roundOver
		return state
	if len(playerHand) >= 5:
		print("You just hit up to a 5 Card Charlie! Even money coming to you!")
		state.bank += bet
		print("You now have ${} in your bank!".format(state.bank))
		state.charliePaid = True
	if state.phase == RoundPhase.dealerTurn:
		dVal = dealer(dCard1, dCard2, dealerHand, shoe)
		state.dealerTotal = dVal
		state.phase = RoundPhase.settle
	if state.phase == RoundPhase.settle:
		return resolveDealerPhase(state, state.dealerTotal)
	return state

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
	return session

def runBetFlow(session):
	while True:
		if session.bank <= 0:
			print(uiTxt["outMoney1"])
			print(uiTxt["outMoney2"])
			while True:
				addCash = readInput("$")
				if addCash.lower() == "q":
					quitGame()
				try:
					session.bank += +int(addCash)
				except ValueError:
					print("That wasn't a number, try again.")
					continue
				if session.bank < 0:
					print("You fail at math. Try again!")
					session.bank = 0
					continue
				print("Great, starting you off again with ${}.".format(session.bank))
				break
		if session.bet == 0:
			print(uiTxt["betAsk"].format(session.bank))
		else:
			print(uiTxt["betAskRpt"].format(bank=session.bank, bet=session.bet))
		betIn = readInput("$?")
		if betIn.lower() == "q":
			quitGame()
		try:
			nextBet = int(betIn)
		except ValueError:
			if session.bet == 0:
				print(uiTxt["betNone"])
				continue
			nextBet = session.bet
		if nextBet > session.bank:
			print("You simply don't have the funds for a bet that size!")
			continue
		print("You bet ${bet}.".format(bet=nextBet))
		session.bet = nextBet
		return session

def runRoundFlow(session):
	if len(session.shoe.deck) < 15:
		session.shoe.reset()
		print("\nShuffling!\n")
		session.shoe.countNow = 0
	state, initBj = startRound(session)
	card1, card2 = state.playerCards
	dCard1, dCard2 = state.dealerCards
	playerHand = state.playerHand
	handVal = state.playerTotal
	dealerHand = state.dealerHand
	d2 = dealerHand[1]
	dVal = state.dealerTotal
	dealerBlackjack = isBlackjack(dealerHand)
	if renderInitBj(initBj, state, card1, card2):
		session.bank = state.bank
		return session
	print("You drew the {card1} and the {card2} for a total of {hand}.\nDealer is showing {dealer}.".format(card1=card1, card2=card2, hand=handVal, dealer=dCard2))
	if state.phase == RoundPhase.insurance:
		tookIns = promptIns(readInput)
		insRes = applyInsPhase(state, tookIns)
		renderInsRes(insRes, session.bet)
		if state.phase == RoundPhase.roundOver:
			session.bank = state.bank
			return session
	turnRes = applyTurnPhase(
		state,
		session.shoe,
		readTurnChoice,
		renderPlayEvent,
	)
	if turnRes.quit:
		quitGame()
	state = turnRes.state
	state = resolveRoundEnd(state, dVal, dCard1, dCard2, dealerHand, playerHand, session.bet, session.shoe)
	session.bank = state.bank
	session.roundState = state
	return session

session = None

# Game starts here
session = setupSession()
shuffle = session.deckAmt * 52 - 20

#Play Begins
while True:
	session = runBetFlow(session)
	session = runRoundFlow(session)
	continue
