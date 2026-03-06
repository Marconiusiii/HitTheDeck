#!/usr/bin/env python3

import os
import random
from engine import applyAction, canSplitCards, dealRound, handValue, isBlackjack
from engine import applyNonSplitIntent, parsePlayerIntent
from engine import evaluateInitialBlackjack, resolveInsurance, resolveRound
from engine import evalTurnOut
from engine import playDealerTurn, playerDoubleDownStep, playerHitStep, startSplitHands
from engine import resolveSplitHandIntent
from engine import parseBankInput, parseDeckCount, startSession

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

# Winning Calls

win = [
"Alright alright alright!",
"That's what I'm talkin' about!",
"Money money money!",
"Schweeeet!",
"Winner winner, chicken dinner!",
"We have a winner!",
"Quite nice, that.",
"Very good!",
"Most excellent!",
"You punched that dealer right in the face!",
"Do the thing! Score the money units!",
"Hot damn!",
"You're on fire!",
"Bingo! Wait, wrong game...",
"Yahtzee! Oh, wrong game...",
"So much win!",
"Way to go!",
"Hooray!",
"Awesome.",
"Sweet!",
"That's some fine card sharkin' right there, I tell you what!",
"Woohoo!",
"You win all the things!",
"Look out, the pit boss is watching!",
"Rock on!",
"The win is strong with this one.",
"Yeehaw!",
"Full of win!",
"Nice, good one.",
"That's the way to do it!",
"Yes! Keep it up!",
"You are totally ready for Vegas!",
"So amaze!",
"Positive reinforcement!",
"There you go!",
"That'll do.",
"Someone call the cops! You just committed grand larceny!",
"Awwww Yiss!",
"Awesomesauce!",
"Someone get some salsa for all these chips you have!",
"Hooty Hoo!",
"Loud! Noises!"
]

lose = [
"What in the ass?",
"You just got F'd in the A!",
"Dammit, dammit, dammit!",
"Aww shucks.",
"Crap!",
"Total bollocks, that.",
"Hey, wha' happened?",
"Rat farts!",
"Total balls.",
"Oh biscuits!",
"Oh applesauce!",
"That...that was not good.",
"Do or do not. There is no try!",
"Ouch, not pleasant.",
"Fiddlesticks!",
"You were eaten by a Gru.",
"Your card skills are lacking.",
"Fanned on that one...",
"Robbed!",
"Ah shit.",
"Damn, too bad.",
"Frak!",
"Oh no!",
"You are doing it wrong!",
"Oops, that's a loss.",
"So much for your retirement.","So much for college tuition.",
"Hey, at least the drinks are free.",
"Better luck next hand!",
"Your chips are getting low.",
"Aack, not good!",
"That's unfortunate.",
"Sorry, you lost.",
"Loser!",
"That's a loser!",
"Who shuffled this deck?",
"Who cut this round?",
"This dealer is totally cheating.",
"At least you get free table massages.",
"That's not what I meant when I said I like big busts!",
"Try again.",
"Noooooooooo!",
"All your chips are belong to us!",
"You should probably go play Craps now."
]

# Hit function
def hit(playerHand, handVal, shoe):
	while True:
		step = playerHitStep(shoe, playerHand)
		print("You drew the {card} and now have {hand}.".format(card=step["cardName"], hand=step["total"]))
		handVal = step["total"]
		if step["bust"]:
			break
		elif step["blackjack"]:
			print("Sanding on 21, stop hitting me!")
			break
		#print("True Count: {}".format(shoe.countNow))
		print("Hit(h) or Stand(s)?")
		hitAgain = readInput(">")
		if hitAgain == 'h':
			continue
		else:
			print("You stand on {}.".format(handVal))
			break
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
	while True:
		result1 = resolveSplitHandIntent(h1, shoe, handSP1, hand1)
		hand1 = result1["total"]
		if result1["invalid"]:
			break
		if result1["intent"] == "h":
			print("You drew the {card} and now have {hand}.".format(card=result1["drawCard"], hand=hand1))
			if result1["bust"]:
				print("You bust on your first hand with {}!.".format(hand1))
				break
			print("Hit(h) or Stand(s)?")
			h1 = readInput(">")
			continue
		if result1["intent"] == "dd":
			betDouble1 += 1
			if result1["bust"]:
				print("You drew the {card} and bust with {hand}!".format(card=result1["drawCard"], hand=hand1))
			else:
				print("You double down on your first hand  and draw a {card} for a total of {hand}. Good luck!".format(card=result1["drawCard"], hand=hand1))
			break
		if result1["intent"] == "s":
			print("You stand on your first hand with {}.".format(hand1))
			break
		break
	print("You drew the {card2} for your second hand and now have {hand}.".format(card2=spCard2, hand=hand2))
	print("Hit, Double Down, or stand?")
	h2 = readInput(">")
	while True:
		result2 = resolveSplitHandIntent(h2, shoe, handSP2, hand2)
		hand2 = result2["total"]
		if result2["invalid"]:
			break
		if result2["intent"] == "h":
			print("You drew the {card} and now have {hand}.".format(card=result2["drawCard"], hand=hand2))
			if result2["bust"]:
				print("You bust on your second hand with {}!.".format(hand2))
				break
			print("Hit(h) or Stand(s)?")
			h2 = readInput(">")
			continue
		if result2["intent"] == "dd":
			betDouble2 += 1
			if result2["bust"]:
				print("You drew the {card} and bust with {hand}!".format(card=result2["drawCard"], hand=hand2))
			else:
				print("You doubled down on your second hand and drew the {card} for a total of {hand}. Good luck!".format(card=result2["drawCard"], hand=hand2))
			break
		if result2["intent"] == "s":
			print("You stand on your second hand with a total of {}.".format(hand2))
			break
		break

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
				print("You can't split those cards! Splitting wasn't even an option, you sneaky bastard!")
			else:
				print("You can't do that!")
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
				print("You don't have enough chips for that!\nTry hitting instead, you silly goose!")
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


def renderRoundEvent(event):
	code = event["code"]
	if code == "splitHandRes":
		handIdx = event["handIdx"]
		outcome = event["outcome"]
		if handIdx == 1:
			if outcome == "lose":
				print("Your first hand loses!")
			elif outcome == "push":
				print("Your first hand is a push!")
			else:
				print("You win with your first hand!")
		else:
			if outcome == "lose":
				print("Your second hand loses!")
			elif outcome == "push":
				print("Your second hand pushes!")
			else:
				print("Your second hand wins! {}".format(win[random.randint(0, len(win)-1)]))
	elif code == "playerLose":
		print(lose[random.randint(0, len(lose)-1)])
	elif code == "playerPush":
		print("It's a push!")
	elif code == "dealerBustWin":
		print("Dealer busts with {dealer}!\n{win}".format(dealer=event["dealerTotal"], win=win[random.randint(0, len(win)-1)]))
	elif code == "playerWin":
		print(win[random.randint(0, len(win)-1)])
	elif code == "playerSurr":
		print("You decide to Surrender, chickening out, buggering off, bravely turning your tail and fleeing!\nDealer had {}.".format(event["dealerTotal"]))
	elif code == "playerBust":
		print("You bust!\n{lose}\nDealer had {dealer}.".format(lose=lose[random.randint(0, len(lose)-1)], dealer=event["dealerTotal"]))


def renderInitBj(outcome, state, card1, card2):
	if outcome == "push":
		print("Push! You and the Dealer both have Blackjack.")
		return True
	if outcome == "playerBj":
		print("Blackjack!\n{win}\nYou drew the {card1} and the {card2} and have shamed the Dealer!\n${chips} coming to you!".format(win=win[random.randint(0, len(win)-1)], card1=card1, card2=card2, chips=state.bet//2*3))
		state.bank += state.bet//2 * 3
		return True
	return False


def promptInsuranceDecision():
	print("Insurance?")
	ins = readInput("y/n?")
	tookIns = ins == 'y'
	if tookIns:
		print("Dealer checks their cards...")
	else:
		print("You decline insurance and Dealer checks their cards...")
	return tookIns


def renderInsRes(result, bet):
	if result["result"] == "insWin":
		print("Dealer has 21. Insurance wins and offsets your main bet.")
	elif result["result"] == "insLose":
		print("Dealer does not have 21! You pay ${} to Insurance.".format(bet//2))
	elif result["result"] == "dealerBj":
		print("They have 21!\n{}".format(lose[random.randint(0, len(lose)-1)]))
	else:
		print("Dealer does not have 21! Phew, carry on.")


def resolveDealerPhase(state, dVal):
	resolution = resolveRound(state, dVal)
	for event in resolution.events:
		renderRoundEvent(event)
	state.bank += resolution.bankDelta
	return state

bet = 0
bank = initBank = 0

# Game starts here
print("Hit the Deck! v.{}\n\t\tBy: Marco Salsiccia".format(version))
print("How much would you like to cash in for your bank?")
while True:
	bankRes = parseBankInput(readInput("$"))
	if bankRes["ok"]:
		bank = bankRes["value"]
		break
	print("That wasn't a number, doofus.")
	continue
print("Great, starting off with ${bank}. And how many decks?".format(bank=bank))
initBank = bank

#Decks and Shuffle
while True:
	deckRes = parseDeckCount(readInput("Please choose 1-6 Decks >"))
	if not deckRes["ok"] and deckRes["reason"] == "notNum":
		print("That wasn't a number between 1-6! That wasn't even a number! Try again you silly goose.")
		continue
	deckAmount = deckRes["value"]
	if deckAmount == 1:
		print("Starting a single deck game. Good luck!")
		break
	elif 2 <= deckAmount <= 6:
		print("Starting a game with {} decks. Good luck!".format(deckAmount))
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

shuffle = deckAmount * 52 - 20

# Initial deck creation
session = startSession(bank, deckAmount)
shoe = session["shoe"]
bank = session["bank"]
initBank = session["initBank"]

#Play Begins
while True:
	if bank <= 0:
		print("You are totally out of money!")
		print("Add more to your bank or type q to exit the game, walking away with a sad, empty wallet.")
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
			else:
				print("Great, starting you off again with ${}.".format(bank))
				break
	else:
		pass

# Betting
	##print("True Count: {}".format(shoe.countNow))

	if bet == 0:
		print("You have ${} in your bank. How much would you like to bet?".format(bank))
	else:
		print("You have ${bank} in your bank. How much would you like to bet?\nHit Enter to repeat your last bet of ${bet}.".format(bank=bank, bet=bet))
	betIn = readInput("$?")
	if betIn.lower() == "q":
		quitGame()
	try:
		bet = int(betIn)
	except ValueError:
		if bet == 0:
			print("Nice try, but you didn't bet anything, Dealer got annoyed and hits you with a shoe.")
			continue
		else:
			pass
	if bet > bank:
		print("You simply don't have the funds for a bet that size!")
		continue
	else:
		print("You bet ${bet}.".format(bet=bet))
	# Initial Draw

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
		bank = state.bank
		continue

	print("You drew the {card1} and the {card2} for a total of {hand}.\nDealer is showing {dealer}.".format(card1=card1, card2=card2, hand=handVal, dealer=dCard2))

	# Insurance
	if d2 == 1:
		tookIns = promptInsuranceDecision()
		insRes = resolveInsurance(d2, tookIns, dealerBlackjack, bet)
		state.bank += insRes["bankDelta"]
		renderInsRes(insRes, bet)
		if insRes["roundOver"]:
			bank = state.bank
			continue
	else:
		dealerRes = resolveInsurance(d2, False, dealerBlackjack, bet)
		if dealerRes["roundOver"]:
			print("Dealer has Blackjack.\n{}".format(lose[random.randint(0, len(lose)-1)]))
			state.bank += dealerRes["bankDelta"]
			bank = state.bank
			continue

	# Split Check
	canSplit = canSplitCards(card1, card2)
	state = resolvePlayerTurn(canSplit, state, dVal, shoe)
	turnOut = evalTurnOut(state, dVal)
	if turnOut["roundOver"]:
		renderRoundEvent(turnOut["event"])
		if turnOut["event"]["code"] == "playerBust":
			state.bank -= bet
		bank = state.bank
		continue

	# 5 card Charlie
	if len(playerHand) >= 5:
		print("You just hit up to a 5 Card Charlie! Even money coming to you!")
		state.bank += bet
		print("You now have ${} in your bank!".format(state.bank))
		state.charliePaid = True

	# Dealer phase

	dVal = dealer(dCard1, dCard2, dealerHand, shoe)
	state.dealerTotal = dVal
	state = resolveDealerPhase(state, dVal)
	bank = state.bank
	continue
