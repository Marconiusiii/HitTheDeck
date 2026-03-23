#!/usr/bin/env python3

import random

uiTxt = {
	"hitStand": "Hit(h) or Stand(s)?",
	"cantDo": "You can't do that!",
	"splitBlk": "You can't split those cards! Splitting wasn't even an option, you sneaky bastard!",
	"noFundsSplit": "You don't have enough chips for that!\nTry hitting instead, you silly goose!",
	"outMoney1": "You are totally out of money!",
	"outMoney2": "Add more to your bank or type q to exit the game, walking away with a sad, empty wallet.",
	"betAsk": "You have ${} in your bank. How much would you like to bet?",
	"betAskRpt": "You have ${bank} in your bank. How much would you like to bet?\nHit Enter to repeat your last bet of ${bet}.",
	"betNone": "Nice try, but you didn't bet anything, Dealer got annoyed and hits you with a shoe.",
}

winMsg = [
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

loseMsg = [
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
	"So much for your retirement.",
	"So much for college tuition.",
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

def pickWinMsg():
	return winMsg[random.randint(0, len(winMsg)-1)]

def pickLoseMsg():
	return loseMsg[random.randint(0, len(loseMsg)-1)]

def renderRoundEvent(event):
	code = event.code
	if code == "splitHandRes":
		handIdx = event.handIdx
		outcome = event.outcome
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
				print("Your second hand wins! {}".format(pickWinMsg()))
	elif code == "playerLose":
		print(pickLoseMsg())
	elif code == "playerPush":
		print("It's a push!")
	elif code == "dealerBustWin":
		print("Dealer busts with {dealer}!\n{win}".format(dealer=event.dealerTotal, win=pickWinMsg()))
	elif code == "playerWin":
		print(pickWinMsg())
	elif code == "playerSurr":
		print("You decide to Surrender, chickening out, buggering off, bravely turning your tail and fleeing!\nDealer had {}.".format(event.dealerTotal))
	elif code == "playerBust":
		print("You bust!\n{lose}\nDealer had {dealer}.".format(lose=pickLoseMsg(), dealer=event.dealerTotal))

def renderInitBj(outcome, state, card1, card2):
	if outcome == "push":
		print("Push! You and the Dealer both have Blackjack.")
		return True
	if outcome == "playerBj":
		print("Blackjack!\n{win}\nYou drew the {card1} and the {card2} and have shamed the Dealer!\n${chips} coming to you!".format(win=pickWinMsg(), card1=card1, card2=card2, chips=state.bet//2*3))
		state.bank += state.bet//2 * 3
		return True
	return False

def promptIns(readFn=input):
	print("Insurance?")
	ins = readFn("y/n?")
	tookIns = ins == "y"
	if tookIns:
		print("Dealer checks their cards...")
	else:
		print("You decline insurance and Dealer checks their cards...")
	return tookIns

def renderInsRes(result, bet):
	if result.result == "insWin":
		print("Dealer has 21. Insurance pays ${} and returns your full ${} main bet.".format(bet, bet))
	elif result.result == "insLose":
		print("Dealer does not have 21! You pay ${} to Insurance.".format(bet//2))
	elif result.result == "dealerBj":
		print("They have 21!\n{}".format(pickLoseMsg()))
	else:
		print("Dealer does not have 21! Phew, carry on.")
