#!/usr/bin/env python3

import os
import random
from engine import Shoe, applyAction, canSplitCards, dealRound, handValue, isBlackjack
from engine import evaluateInitialBlackjack, resolveInsurance, resolveRound
from engine import evaluatePlayerTurnOutcome
from engine import playDealerTurn, playerDoubleDownStep, playerHitStep, startSplitHands

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
		print("You drew the {card} and now have {hand}.".format(card=step["card_name"], hand=step["total"]))
		handVal = step["total"]
		if step["bust"]:
			break
		elif step["blackjack"]:
			print("Sanding on 21, stop hitting me!")
			break
		#print("True Count: {}".format(shoe.count_actual))
		print("Hit(h) or Stand(s)?")
		hitAgain = input(">")
		if hitAgain == 'h':
			continue
		else:
			print("You stand on {}.".format(handVal))
			break
	return handVal

#Double Down function
def doubleDown(playerHand, handVal, shoe):
	step = playerDoubleDownStep(shoe, playerHand)
	print("You doubled down and drew the {draw} and now have {hand}. Good luck!".format(draw=step["card_name"], hand=step["total"]))
	return step["total"]

#Dealer engine
def dealer(dCard1, dCard2, dealerHand, shoe):
	dealer_result = playDealerTurn(shoe, dealerHand)
	dVal = handValue(dealerHand)
	print("Dealer has the {card1} and the {card2} for a total of {dealer}.".format(card1=dCard2, card2=dCard1, dealer=dVal))
	if dealer_result["events"]:
		for event in dealer_result["events"]:
			print("Dealer draws the {card} for a total of {hand}.".format(card=event["card_name"], hand=event["total"]))
		if 17 <= dealer_result["final_total"] <= 21:
			print("Dealer stands with {}.".format(dealer_result["final_total"]))
	else:
		print("Dealer stands on {}.".format(dVal))
	return dealer_result["final_total"]

# Split function
def split(playerHand, shoe):
	betDouble1 = betDouble2 = 0
	split_start = startSplitHands(shoe, playerHand)
	spCard1 = split_start["first_draw_card"]
	spCard2 = split_start["second_draw_card"]
	handSP1 = split_start["hand1"]
	handSP2 = split_start["hand2"]
	hand1 = split_start["total1"]
	hand2 = split_start["total2"]
	print("You split and draw the {card1} for your first hand, a total of {hand}.".format(card1=spCard1, hand=hand1))
	print("Hit, Double Down,  or stand on your first hand?")
	h1 = input(">")
	if h1 == 'h':
		while True:
			step = playerHitStep(shoe, handSP1)
			hand1 = step["total"]
			print("You drew the {card} and now have {hand}.".format(card=step["card_name"], hand=hand1))
			if hand1 >= 22:
				print("You bust on your first hand with {}!.".format(hand1))
				break
			else:
				pass
			print("Hit(h) or Stand(s)?")
			h1Again = input(">")
			if h1Again == 'h':
				continue
			else:
				print("You stand with {} on your first hand.".format(hand1))
				break
	elif h1 == 'dd':
		betDouble1 += 1
		step = playerDoubleDownStep(shoe, handSP1)
		ddHand1 = step["card_name"]
		hand1 = step["total"]
		if hand1 > 21:
			print("You drew the {card} and bust with {hand}!".format(card=ddHand1, hand=hand1))
		else:
			print("You double down on your first hand  and draw a {card} for a total of {hand}. Good luck!".format(card=ddHand1, hand=hand1))
	elif h1 == 's':
		print("You stand on your first hand with {}.".format(hand1))
	else:
		pass
	print("You drew the {card2} for your second hand and now have {hand}.".format(card2=spCard2, hand=hand2))
	print("Hit, Double Down, or stand?")
	h2 = input(">")
	if h2 == 'h':
		while True:
			step = playerHitStep(shoe, handSP2)
			hand2 = step["total"]
			print("You drew the {card} and now have {hand}.".format(card=step["card_name"], hand=hand2))
			if hand2 >= 22:
				print("You bust on your second hand with {}!.".format(hand2))
				break
			else:
				pass
			print("Hit(h) or Stand(s)?")
			h2Again = input(">")
			if h2Again == 'h':
				continue
			else:
				print("You stand with {} on your second hand.".format(hand2))
				break
	elif h2 == 'dd':
		betDouble2 += 1
		step = playerDoubleDownStep(shoe, handSP2)
		ddHand2 = step["card_name"]
		hand2 = step["total"]
		if hand2 > 21:
			print("You drew the {card} and bust with {hand}!".format(card=ddHand2, hand=hand2))
		else:
			print("You doubled down on your second hand and drew the {card} for a total of {hand}. Good luck!".format(card=ddHand2, hand=hand2))
	elif h2 == 's':
		print("You stand on your second hand with a total of {}.".format(hand2))
	else:
		pass

	return [hand1, hand2, betDouble1, betDouble2]


def playerActionPrompt(can_split):
	if can_split:
		print("Hit(h), Split(sp), Double Down(dd), Surrender(su), or Stand(s)?\n)x) to Quit.")
	else:
		print("Hit(h), Double Down(dd), Surrender(su), or Stand(s)?\n(x) to Quit.")
	return input(">  ")


def resolvePlayerTurn(can_split, state, dVal, shoe):
	while True:
		choice = playerActionPrompt(can_split)
		if choice == 'h' or choice == 'H':
			handVal = hit(state.player_hand, state.player_total, shoe)
			applyAction(state, choice, hand_total=handVal)
			break
		elif choice.lower() == "x":
			quitGame()
		elif can_split and choice == 'sp':
			if state.bank - state.bet*2 < 0:
				print("You don't have enough chips for that!\nTry hitting instead, you silly goose!")
				handVal = hit(state.player_hand, state.player_total, shoe)
				applyAction(state, choice, hand_total=handVal)
			else:
				handsplit = split(state.player_hand, shoe)
				applyAction(state, choice, handsplit=handsplit)
			break
		elif (not can_split) and choice == 'sp':
			print("You can't split those cards! Splitting wasn't even an option, you sneaky bastard!")
			continue
		elif choice == 'dd':
			handVal = doubleDown(state.player_hand, state.player_total, shoe)
			applyAction(state, choice, hand_total=handVal)
			break
		elif choice == 'su':
			applyAction(state, choice, bank_delta=-(state.bet / 2))
			break
		elif choice == 's':
			print("You stand on {}.".format(state.player_total))
			applyAction(state, choice)
			break
		else:
			print("You can't do that!")
			continue
	return state


def renderRoundEvent(event):
	code = event["code"]
	if code == "split_hand_result":
		hand_index = event["hand_index"]
		outcome = event["outcome"]
		if hand_index == 1:
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
	elif code == "player_lose":
		print(lose[random.randint(0, len(lose)-1)])
	elif code == "player_push":
		print("It's a push!")
	elif code == "dealer_bust_win":
		print("Dealer busts with {dealer}!\n{win}".format(dealer=event["dealer_total"], win=win[random.randint(0, len(win)-1)]))
	elif code == "player_win":
		print(win[random.randint(0, len(win)-1)])
	elif code == "player_surrender":
		print("You decide to Surrender, chickening out, buggering off, bravely turning your tail and fleeing!\nDealer had {}.".format(event["dealer_total"]))
	elif code == "player_bust":
		print("You bust!\n{lose}\nDealer had {dealer}.".format(lose=lose[random.randint(0, len(lose)-1)], dealer=event["dealer_total"]))


def resolveDealerPhase(state, dVal):
	resolution = resolveRound(state, dVal)
	for event in resolution.events:
		renderRoundEvent(event)
	state.bank += resolution.bank_delta
	return state

bet = 0
bank = initBank = 0

# Game starts here
print("Hit the Deck! v.{}\n\t\tBy: Marco Salsiccia".format(version))
print("How much would you like to cash in for your bank?")
while True:
	try:
		bank = int(input("$"))
		break
	except ValueError:
		print("That wasn't a number, doofus.")
		continue
print("Great, starting off with ${bank}. And how many decks?".format(bank=bank))
gameLoops = 0
initBank = bank

#Decks and Shuffle
while True:
	try:
		deckAmount = int(input("Please choose 1-6 Decks >"))
	except ValueError:
		print("That wasn't a number between 1-6! That wasn't even a number! Try again you silly goose.")
		continue
	if deckAmount == 1:
		print("Starting a single deck game. Good luck!")
		break
	elif 2 <= deckAmount <= 6:
		print("Starting a game with {} decks. Good luck!".format(deckAmount))
		break
	elif deckAmount > 6:
		print("Too many decks! The card shoe explodes and you are felled by playing card papercuts. Good job! Try again.")
		continue
	elif deckAmount < 1:
		print("What are you trying to do? Not play Blackjack? Add some cards, you dork!")
		continue
	else:
		print("That wasn't a number between 1 and 6! It wasn't even a number! Try again, you silly goose.")
		continue

shuffle = deckAmount * 52 - 20

# Initial deck creation
shoe = Shoe(deckAmount)

#Play Begins
while True:
	gameLoops += 1
	if gameLoops == 18:
		clearScreen()
		gameLoops = 0

	if bank <= 0:
		print("You are totally out of money!")
		print("Add more to your bank or hit Ctrl-C to exit the game, walking away with a sad, empty wallet.")
		while True:
			try:
				bank += +int(input("$"))
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
	##print("True Count: {}".format(shoe.count_actual))

	if bet == 0:
		print("You have ${} in your bank. How much would you like to bet?".format(bank))
	else:
		print("You have ${bank} in your bank. How much would you like to bet?\nHit Enter to repeat your last bet of ${bet}.".format(bank=bank, bet=bet))
	try:
		bet = int(input("$?"))
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
		shoe.count_actual = 0
	state = dealRound(shoe, bank, bet)
	state.charlie_paid = False
	card1, card2 = state.player_cards
	dCard1, dCard2 = state.dealer_cards
	playerHand = state.player_hand
	handVal = state.player_total
	dealerHand = state.dealer_hand
	d1, d2 = dealerHand
	dVal = state.dealer_total
	dealerBlackjack = isBlackjack(dealerHand)
	initial_blackjack = evaluateInitialBlackjack(state.player_total, dealerHand)
	if initial_blackjack == "push":
		print("Push! You and the Dealer both have Blackjack.")
		continue
	elif initial_blackjack == "player_blackjack":
		print("Blackjack!\n{win}\nYou drew the {card1} and the {card2} and have shamed the Dealer!\n${chips} coming to you!".format(win=win[random.randint(0, len(win)-1)], card1=card1, card2=card2, chips=bet//2*3))
		state.bank += bet//2 * 3
		bank = state.bank
		continue

	print("You drew the {card1} and the {card2} for a total of {hand}.\nDealer is showing {dealer}.".format(card1=card1, card2=card2, hand=handVal, dealer=dCard2))

	# Insurance
	if d2 == 1:
		print("Insurance?")
		ins = input("y/n?")
		took_insurance = ins == 'y'
		if took_insurance:
			print("Dealer checks their cards...")
		else:
			print("You decline insurance and Dealer checks their cards...")
		insurance_resolution = resolveInsurance(d2, took_insurance, dealerBlackjack, bet)
		state.bank += insurance_resolution["bank_delta"]
		if insurance_resolution["result"] == "insurance_win":
			bank = state.bank
			print("Dealer has 21. Insurance wins and offsets your main bet.")
			continue
		elif insurance_resolution["result"] == "insurance_lose":
			print("Dealer does not have 21! You pay ${} to Insurance.".format(bet//2))
		elif insurance_resolution["result"] == "dealer_blackjack":
			print("They have 21!\n{}".format(lose[random.randint(0, len(lose)-1)]))
			bank = state.bank
			continue
		else:
			print("Dealer does not have 21! Phew, carry on.")
	else:
		dealer_resolution = resolveInsurance(d2, False, dealerBlackjack, bet)
		if dealer_resolution["round_over"]:
			print("Dealer has Blackjack.\n{}".format(lose[random.randint(0, len(lose)-1)]))
			state.bank += dealer_resolution["bank_delta"]
			bank = state.bank
			continue

	# Split Check
	can_split = canSplitCards(card1, card2)
	state = resolvePlayerTurn(can_split, state, dVal, shoe)
	turn_outcome = evaluatePlayerTurnOutcome(state, dVal)
	if turn_outcome["round_over"]:
		renderRoundEvent(turn_outcome["event"])
		if turn_outcome["event"]["code"] == "player_bust":
			state.bank -= bet
		bank = state.bank
		continue

	# 5 card Charlie
	if len(playerHand) >= 5:
		print("You just hit up to a 5 Card Charlie! Even money coming to you!")
		state.bank += bet
		print("You now have ${} in your bank!".format(state.bank))
		state.charlie_paid = True

	# Dealer phase

	dVal = dealer(dCard1, dCard2, dealerHand, shoe)
	state.dealer_total = dVal
	state = resolveDealerPhase(state, dVal)
	bank = state.bank
	continue
