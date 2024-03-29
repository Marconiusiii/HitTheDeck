#!/usr/bin/env python3
import os
import random

# Version Number
version = "3.5"

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

deck = {}
discard = []

suits = ['Spades', 'Clubs', 'Hearts', 'Diamonds']

cardValues = {
'Ace': 1,
'2': 2,
'3': 3,
'4': 4,
'5': 5,
'6': 6,
'7': 7,
'8': 8,
'9': 9,
'10': 10,
'Jack': 10,
'Queen': 10,
'King': 10
}
# Deck Generation

def deckGenerator():
	d = {}
	for suit in suits:
		for card, val in cardValues.items():
			d ['{} of {}'.format(card, suit)] = val
	return d

# Hand Count function

def handCount(hand):
	count = 0
	for i in hand:
		count += i
	return count

# Draw function
def draw(deck, deckAmount):
	if deckAmount == 1:
		card, cardVal = random.choice(list(deck.items()))
		del deck[card]
	elif deckAmount > 1:
		while True:
			card, cardVal = random.choice(list(deck.items()))
			if discard.count(card) == deckAmount:
				del deck[card]
				continue
			else:
				discard.append(card)
				break
	return card, cardVal

cardCount = 0
countActual = 0
def counter(card):
	global cardCount, deck, countActual
	if card in range(2,7):
		cardCount += 1
	elif card >= 10:
		cardCount -= 1
	if len(deck) >= 260:
		trueCount = 6
	elif 208 <= len(deck) < 260:
		trueCount = 5
	elif 156 <= len(deck) < 208:
		trueCount = 4
	elif 104 <= len(deck) < 156:
		trueCount = 3
	elif 52 <= len(deck) < 104:
		trueCount = 2
	elif len(deck) < 52:
		trueCount = 1
	countActual = cardCount // trueCount

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
"Hooty Hoo!"
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
def hit(playerHand, handVal, discard):
	while True:
		cardHit, z = draw(deck, deckAmount)
		counter(z)
		if z == 1 and handVal + 11 <= 21:
			z = 11
			playerHand.append(z)
			handVal = handCount(playerHand)
		elif playerHand[0] == 11 and handVal + z > 21:
			playerHand[0] = 1
			playerHand.append(z)
			handVal = handCount(playerHand)
		elif playerHand[1] == 11 and handVal + z > 21:
			playerHand[1] = 1
			playerHand.append(z)
			handVal = handCount(playerHand)
		elif len(playerHand) > 2 and  playerHand[2] == 11 and handVal + z > 21:
			playerHand[2] = 1
			playerHand.append(z)
			handVal = handCount(playerHand)
		else:
			playerHand.append(z)
			handVal = handCount(playerHand)
		print("You drew the {card} and now have {hand}.".format(card=cardHit, hand=handVal))
		if handVal >= 22:
			break
		elif handVal == 21:
			print("Sanding on 21, stop hitting me!")
			break
		else:
			pass
		#print("True Count: {}".format(countActual))
		print("Hit(h) or Stand(s)?")
		hitAgain = input(">")
		if hitAgain == 'h':
			continue
		else:
			print("You stand on {}.".format(handVal))
			break
	return handVal

#Double Down function
def doubleDown(playerHand, handVal, discard):
	ddCard, dd = draw(deck, deckAmount)
	counter(dd)
	if dd == 1 and handVal + 11 <= 21:
		dd = 11
		playerHand.append(dd)
		handVal = handCount(playerHand)
	elif playerHand[0] == 11 and handVal + dd > 21:
		playerHand[0] = 1
		playerHand.append(dd)
		handVal = handCount(playerHand)
	elif playerHand[1] == 11 and handVal + dd > 21:
		playerHand[1] = 1
		playerHand.append(dd)
		HandVal = handCount(playerHand)
	else:
		playerHand.append(dd)
		handVal = handCount(playerHand)
	print("You doubled down and drew the {draw} and now have {hand}. Good luck!".format(draw=ddCard, hand=handVal))
	return handVal

#Dealer engine
def dealer(dCard1, dCard2, dealerHand, discard):
	if dealerHand[0] == 1 and dealerHand[1] == 1:
		dealerHand[0] = 11
		dVal = handCount(dealerHand)
	elif dealerHand[0] == 1:
		dealerHand[0] = 11
		dVal = handCount(dealerHand)
	elif dealerHand[1] == 1:
		dealerHand[1] = 11
		dVal = handCount(dealerHand)
	else:
		dVal = handCount(dealerHand)
	print("Dealer has the {card1} and the {card2} for a total of {dealer}.".format(card1=dCard2, card2=dCard1, dealer=dVal))
	if dVal < 17:
		while True:
			dHit, dh1 = draw(deck, deckAmount)
			counter(dh1)
			if dh1 == 1 and dVal + 11 <= 21:
				dh1 = 11
				dealerHand.append(dh1)
				dVal = handCount(dealerHand)
			elif dealerHand[0] == 11 and dVal + dh1 > 21:
				dealerHand[0] = 1
				dealerHand.append(dh1)
				dVal = handCount(dealerHand)
			elif dealerHand[1] == 11 and dVal + dh1 > 21:
				dealerHand[1] = 1
				dealerHand.append(dh1)
				dVal = handCount(dealerHand)
			elif len(dealerHand) > 2 and  dealerHand[2] == 11 and dVal + dh1 > 21:
				dealerHand[2] = 1
				dealerHand.append(dh1)
				dVal = handCount(dealerHand)
			else:
				dealerHand.append(dh1)
				dVal = handCount(dealerHand)
			print("Dealer draws the {card} for a total of {hand}.".format(card=dHit, hand=dVal))
			if dVal <= 16:
				continue
			elif 17 <= dVal <= 21:
				print("Dealer stands with {}.".format(dVal))
				break
			else:
				break
	else:
		print("Dealer stands on {}.".format(dVal))
	return dVal

# Split function
def split(playerHand, discard):
	betDouble1 = 0
	betDouble2 = 0
	spCard1, sp1 = draw(deck, deckAmount)
	spCard2, sp2 = draw(deck, deckAmount)
	counter(sp1)
	counter(sp2)
	if playerHand[0] == 11:
		playerHand[0] = 11
		playerHand[1] = 11
	elif (sp1 == 1 and playerHand[0] + 11 <= 21) and (sp2 == 1 and playerHand[1] + 11 <= 21):
		sp1 = 11
		sp2 = 11
	elif sp1 == 1 and playerHand[0] + 11 <= 21:
		sp1 = 11
	elif sp2 == 1 and playerHand[1] + 11 <= 21:
		sp2 = 11
	else:
		pass
	handSP1 = [sp1, playerHand[0]]
	hand1 = handCount(handSP1)

	handSP2 = [sp2, playerHand[1]]
	hand2 = handCount(handSP2)
	print("You split and draw the {card1} for your first hand, a total of {hand}.".format(card1=spCard1, hand=hand1))
	print("Hit, Double Down,  or stand on your first hand?")
	h1 = input(">")
	if h1 == 'h':
		while True:
			handHit1, spH1 = draw(deck, deckAmount)
			counter(spH1)
			if spH1 == 1 and hand1 + 11 <= 21:
				spH1 = 11
				handSP1.append(spH1)
				hand1 = handCount(handSP1)
			elif spH1 == 1 and playerHand[0] == 11:
				playerHand[0] = 1
				handSP1.append(spH1)
				hand1 = handCount(handSP1)
			elif playerHand[0] == 11 and hand1 + spH1 > 21:
				playerHand[0] = 1
				handSP1.append(spH1)
				hand1 = handCount(handSP1)
			elif len(handSP1) > 2 and handSP1[2] == 11 and hand1 + spH1 > 21:
				handSP1[2] = 1
				handSP1.append(spH1)
				hand1 = handCount(handSP1)
			elif len(handSP1) > 2 and handSP1[0] == 11 and hand1 + spH1 > 21:
				handSP1[0] = 1
				handSP1.append(spH1)
				hand1 = handCount(handSP1)
			else:
				handSP1.append(spH1)
				hand1 = handCount(handSP1)
			print("You drew the {card} and now have {hand}.".format(card=handHit1, hand=hand1))
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
		ddHand1, ddH1 = draw(deck, deckAmount)
		counter(ddH1)
		if ddH1 == 1 and hand1 + 11 <= 21:
			ddH1 = 11
			handSP1.append(ddH1)
			hand1 = handCount(handSP1)
		elif handSP1[1] == 11 and hand1 + ddH1 > 21:
			handSP1[1] = 1
			handSP1.append(ddH1)
			hand1 = handCount(handSP1)
		elif playerHand[0] == 11 and hand1 + ddH1 > 21:
			playerHand[0] = 1
			handSP1.append(ddH1)
			hand1 = handCount(handSP1)
		else:
			handSP1.append(ddH1)
			hand1 = handCount(handSP1)
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
			handHit2, spH2 = draw(deck, deckAmount)
			counter(spH2)
			if spH2 == 1 and hand2 + 11 <= 21:
				spH2 = 11
				handSP2.append(spH2)
				hand2 = handCount(handSP2)
			elif spH2 == 1 and playerHand[1] == 11:
				playerHand[1] = 1
				handSP2.append(spH2)
				hand2 = handCount(handSP2)
			elif playerHand[1] == 11 and hand2 + spH2 > 21:
				playerHand[1] = 1
				handSP2.append(spH2)
				hand2 = handCount(handSP2)
			elif len(handSP2) > 2 and  handSP2[2] == 11 and handSP2 + spH2 > 21:
				handSP2[2] = 1
				handSP2.append(spH2)
				hand2 = handCount(handSP2)
			elif len(handSP2) > 2 and  handSP2[0] == 11 and handSP2 + spH2 > 21:
				handSP2[0] = 1
				handSP2.append(spH2)
				hand2 = handCount(handSP2)
			else:
				handSP2.append(spH2)
				hand2 = handCount(handSP2)
			print("You drew the {card} and now have {hand}.".format(card=handHit2, hand=hand2))
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
		ddHand2, ddH2 = draw(deck, deckAmount)
		counter(ddH2)
		if ddH2 == 1 and hand2 + 11 <= 21:
			ddH2 = 11
			handSP2.append(ddH2)
			hand2 = handCount(handSP2)
		elif sp2 == 11 and hand2 + ddH2 > 21:
			handSP2[0] = 1
			handSP2.append(ddH2)
			hand2 = handCounrt(handSP2)
		elif playerHand[1] == 11 and hand2 + ddH2 > 21:
			playerHand[1] = 1
			handSP2.append(ddH2)
			hand2 = handCount(handSP2)
		else:
			handSP2.append(ddH2)
			hand2 = handCount(handSP2)
		if hand2 > 21:
			print("You drew the {card} and bust with {hand}!".format(card=ddHand2, hand=hand2))
		else:
			print("You doubled down on your second hand and drew the {card} for a total of {hand}. Good luck!".format(card=ddHand2, hand=hand2))
	elif h2 == 's':
		print("You stand on your second hand with a total of {}.".format(hand2))
	else:
		pass

	return [hand1, hand2, betDouble1, betDouble2]

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
deck = deckGenerator()

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
	##print("True Count: {}".format(countActual))

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

	if len(deck) < 15:
		deck = deckGenerator()
		del discard[:]
		print("\nShuffling!\n")
		countActual = 0
	card1, x = draw(deck, deckAmount)
	card2, y = draw(deck, deckAmount)
	counter(x)
	counter(y)

	dCard1, d1 =draw(deck, deckAmount)
	dCard2, d2 = draw(deck, deckAmount)
	counter(d1)
	counter(d2)
	dealerHand = [d1, d2]
	dVal = handCount(dealerHand)

# Checking for Aces

	if x == 1 and y != 1:
		x = 11
	elif x == 1:
		x = 11
	elif y == 1:
		y = 11
	else:
		pass

	playerHand = [x, y]
	handVal = handCount(playerHand)
	if handVal == 21:
		print("Blackjack!\n{win}\nYou drew the {card1} and the {card2} and have shamed the Dealer!\n${chips} coming to you!".format(win=win[random.randint(0, len(win)-1)], card1=card1, card2=card2, chips=bet//2*3))
		bank += bet//2 * 3
		continue
	else:
		pass

	print("You drew the {card1} and the {card2} for a total of {hand}.\nDealer is showing {dealer}.".format(card1=card1, card2=card2, hand=handVal, dealer=dCard2))

# Insurance
	if d2 == 1:
		print("Insurance?")
		ins = input("y/n?")
		if ins == 'y':
			print("Dealer checks their cards...")
			if d1 == 10:
				print("Oops, dealer has 21. You lose ${}.".format(bet//2))
				bank -= bet//2
				continue
			else:
				print("Dealer does not have 21! You pay ${} to Insurance.".format(bet//2))
				bank -= bet//2
		else:
			print("You decline insurance and Dealer checks their cards...")
			if d1 == 10:
				print("They have 21!\n{}".format(lose[random.randint(0, len(lose)-1)]))
				bank -= bet
				continue
			else:
				print("Dealer does not have 21! Phew, carry on.")
				# Split Check
	card1StrA, card1StrB, card1StrC = card1.split()
	card2StrA, card2StrB, card2strC = card2.split()

	while True:
		if card1StrA == card2StrA:
			print("Hit(h), Split(sp), Double Down(dd), Surrender(su), or Stand(s)?\n)x) to Quit.")
			choice = input(">  ")
		else:
			print("Hit(h), Double Down(dd), Surrender(su), or Stand(s)?\n(x) to Quit.")
			choice = input(">  ")
		if choice == 'h' or choice == 'H':
			handVal = hit(playerHand, handVal, discard)
			break
		elif choice.lower() == "x":
			quitGame()
		elif card1StrA == card2StrA and choice == 'sp':
			if bank - bet*2 <= 0:
				print("You don't have enough chips for that! Try hitting instead, you silly goose!")
				handVal = hit(playerHand, handVal, discard)
			else:
				handsplit = split(playerHand, discard)
			break
		elif card1StrA != card2StrA and choice == 'sp':
			print("You can't split those cards! Splitting wasn't even an option, you sneaky bastard!")
			continue

		elif choice == 'dd':
			handVal = doubleDown(playerHand, handVal, discard)
			break
		elif choice == 'su':
			print("You decide to Surrender, chickening out, buggering off, bravely turning your tail and fleeing!\nDealer had {}.".format(dVal))
			bank -= bet/2
			break
		elif choice == 's':
			print("You stand on {}.".format(handVal))
			break
		else:
			print("You can't do that!")
			continue
	if choice == 'su':
		continue

	if handVal >= 22:
		print("You bust!\n{lose}\nDealer had {dealer}.".format(lose=lose[random.randint(0, len(lose)-1)], dealer=dVal))
		bank -= bet
		continue
	else:
		pass
# 5 card Charlie

	if len(playerHand) >= 5:
		print("You just hit up to a 5 Card Charlie! Even money coming to you!")
		bank += bet
		print("You now have ${} in your bank!".format(bank))

# Dealer phase

	dVal = dealer(dCard1, dCard2, dealerHand, discard)
	if dVal >= 22 and handVal <= 21:
		print("Dealer busts with {dealer}!\n{win}".format(dealer=dVal, win=win[random.randint(0, len(win)-1)]))
		if choice == 'dd':
			bank += bet*2
		elif choice == 'sp':
			if handsplit[0] <= 21 and handsplit[1] <= 21:
				print("Both your split hands win! ${} coming to you.".format(bet*2))
				bank += bet*2
				continue
			else:
				bank += bet
				continue
		else:
			bank += bet
		continue
	else:
		pass
	if choice == 'sp' and bank - bet*2 > 0:
		hand1 = handsplit[0]
		hand2 = handsplit[1]
		betDouble1 = handsplit[2]
		betDouble2 = handsplit[3]
		if hand1 < dVal or hand1 >= 22:
			print("Your first hand loses!")
			if betDouble1 == 1:
				bank -= bet*2
			else:
				bank -= bet
		elif hand1 == dVal:
			print("Your first hand is a push!")
		else:
			print("You win with your first hand!")
			if betDouble1 == 1:
				bank += bet*2
			else:
				bank += bet
		if hand2 < dVal or hand2 >= 22:
			if betDouble2 == 1:
				bank -= bet*2
			else:
				bank -= bet
			print("Your second hand loses!")
			continue
		elif hand2 == dVal:
			print("Your second hand pushes!")
			continue
		else:
			if betDouble2 == 1:
				bank += bet*2
			else:
				bank += bet
			print("Your second hand wins! {}".format(win[random.randint(0, len(win)-1)]))
			continue
	else:
		pass
	if handVal < dVal:
		print(lose[random.randint(0, len(lose)-1)])
		if choice == 'dd':
			bank -= bet*2
		else:
			bank -= bet
	elif handVal == dVal:
		print("It's a push!")
	else:
		print(win[random.randint(0, len(win)-1)])
		if choice == 'dd':
			bank += bet*2
		else:
			bank += bet
	continue
