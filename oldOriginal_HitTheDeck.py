import random


deck = {
'Ace of Spades': 1,
'2 of Spades': 2,
'3 of Spades': 3,
'4 of Spades': 4,
'5 of Spades': 5,
'6 of Spades': 6,
'7 of Spades': 7,
'8 of spades': 8,
'9 of Spades': 9,
'10 of Spades': 10,
'Jack of Spades': 10,
'Queen of Spades': 10,
'King of Spades': 10,
'Ace of Hearts': 1,
'2 of Hearts': 2,
'3 of Hearts': 3,
'4 of Hearts': 4,
'5 of Hearts': 5,
'6 of Hearts': 6,
'7 of Hearts': 7,
'8 of Hearts': 8,
'9 of Hearts': 9,
'10 of Hearts': 10,
'Jack of Hearts': 10,
'Queen of Hearts': 10,
'King of Hearts': 10,
'Ace of Clubs': 1,
'2 of Clubs': 2,
'3 of Clubs': 3,
'4 of Clubs': 4,
'5 of Clubs': 5,
'6 of Clubs': 6,
'7 of Clubs': 7,
'8 of Clubs': 8,
'9 of Clubs': 9,
'10 of Clubs': 10,
'Jack of Clubs': 10,
'Queen of Clubs': 10,
'King of Clubs': 10,
'Ace of Diamonds': 1,
'2 of Diamonds': 2,
'3 of Diamonds': 3,
'4 of Diamonds': 4,
'5 of Diamonds': 5,
'6 of Diamonds': 6,
'7 of Diamonds': 7,
'8 of Diamonds': 8,
'9 of Diamonds': 9,
'10 of Diamonds': 10,
'Jack of Diamonds': 10,
'Queen of Diamonds': 10,
'King of Diamonds': 10
}
win = ["Alright alright alright!", "That's what I'm talkin' about!", "Money money money!", "Schweeeet!", "Winner winner, chicken dinner!", "We have a winner!", "Quite nice, that.", "Very good!", "Most excellent!", "You punched that dealer right in the face!", "Do the thing! Score the money units!", "Hot damn!", "You're on fire!", "Bingo! Wait, wrong game...", "Yahtzee! Oh, wrong game...", "So much win!", "Way to go!", "Hooray!", "Awesome.", "Sweet!", "That's some fine card sharkin' right there, I tell you what!", "Woohoo!", "You win all the things!", "Look out, the pit boss is watching!", "Rock on!", "The win is strong with this one.", "Yeehaw!", "Full of win!", "Nice, good one.", "That's the way to do it!", "Yes! Keep it up!", "You are totally ready for Vegas!", "So amaze!", "Positive reinforcement!", "There you go!", "That'll do.", "Someone call the cops! You just committed grand larceny!"]

lose = ["What in the ass?", "You just got F'd in the A!", "Dammit, dammit, dammit!",  "Aww shucks.", "Crap!", "Total bollocks, that.", "Hey, wha' happened?", "Rat farts!", "Total balls.", "Oh biscuits!", "Oh applesauce!", "That...that was not good.", "Do or do not. There is no try!", "Ouch, not pleasant.", "Fiddlesticks!", "You were eaten by a Gru.", "Your card skills are lacking.", "Fanned on that one...", "Robbed!", "Ah shit.", "Damn, too bad.", "Frak!", "Oh no!", "You are doing it wrong!", "Oops, that's a loss.", "So much for your retirement.", "So much for college tuition.", "Hey, at least the drinks are free.", "Better luck next hand!", "Your chips are getting low.", "Aack, not good!", "That's unfortunate.", "Sorry, you lost.", "Loser!", "That's a loser!", "Who shuffled this deck?", "Who cut this round?", "This dealer is totally cheating.", "At least you get free table massages.", "That's not what I meant when I said I like big busts!", "Try again."]

# Hit function
def hit(handVal, x, y):
	while True:
		cardHit, z = random.choice(list(deck.items()))
		if z == 1 and handVal + 11 <= 21:
			z = 11
			handVal += z
		elif x == 11 and (handVal + z > 21):
			x = 1
			handVal = x + y + z
		elif y == 11 and (handVal + z > 21):
			y = 1
			handVal = x + y + z
		else:
			handVal += z
		print "You drew the %s and now have %d." %(cardHit, handVal)
		if handVal >= 22:
			break
		elif handVal == 21:
			print "Sanding on 21, stop hitting me!"
			break
		else:
			pass
		print "Hit or stand?"
		hitAgain = raw_input(">")
		if hitAgain == 'h':
			continue
		else:
			print "You stand on %d." %handVal
			break
	return handVal

#Double Down function
def doubleDown(handVal, x, y):
	ddCard, dd = random.choice(list(deck.items()))
	if dd == 1 and handVal + 11 <= 21:
		dd == 11
		handVal += dd
	elif x == 11 and handVal + dd > 21:
		x = 1
		handVal = x + y + dd
	elif y == 11 and handVal + dd > 21:
		y = 1
		HandVal = x + y + dd
	else:
		handVal += dd
	print "You doubled down and drew the %s and now have %d. Good luck!" %(ddCard, handVal)
	return handVal

#Dealer engine
def dealer(dCard1, dCard2, d1, d2):
	if d1 == 1 and d2 == 1:
		d1 = 11
		dVal = d1 + d2
	elif d1 == 1 and d2 != 1:
		d1 = 11
		dVal = d1 + d2
	elif d2 == 1 and d1 != 1:
		d2 = 11
		dVal = d1 + d2
	else:
		dVal = d1 + d2
	print "the dealer has the %s and the %s for a total of %d." %(dCard2, dCard1, dVal)
	if dVal < 17:
		while True:
			dHit, dh1 = random.choice(list(deck.items()))
			if dh1 == 1 and dVal + 11 <=21:
				dh1 = 11
				dVal += dh1
			elif d1 == 11 and dVal + dh1 >= 22:
				d1 = 1
				dVal = d1 + d2 + dh1
			elif d2 == 11 and dVal + dh1 >= 22:
				d2 = 1
				dVal = d1 + d2 + dh1
			else:
				dVal += dh1
			print "The dealer draws the %s for a total of %d." %(dHit, dVal)
			if dVal <= 16:
				continue
			elif 17 <= dVal <= 21:
				print "The dealer stands with %d." %dVal
				break
			else:
				break
	else:
		print "The dealer stands on %d." %dVal
	return dVal

# Split function
def split(x, y):
	betDouble1 = 0
	betDouble2 = 0
	spCard1, sp1 = random.choice(list(deck.items()))
	spCard2, sp2 = random.choice(list(deck.items()))
	if x == 1 and y == 1:
		x = 11
		y = 11
	elif (sp1 == 1 and x + 11 <= 21) and (sp2 == 1 and y + 11 <= 21):
		sp1 = 11
		sp2 = 11
	elif sp1 == 1 and x + 11 <= 21:
		sp1 = 11
	elif sp2 == 1 and y + 11 <= 21:
		sp2 = 11
	else:
		pass
	hand1 = sp1 + x
	hand2 = sp2 + y
	print "You split and draw the %s for your first hand, a total of %d." %(spCard1, hand1)
	print "Hit, Double Down,  or stand on your first hand?"
	h1 = raw_input(">")
	if h1 == 'h':
		while True:
			handHit1, spH1 = random.choice(list(deck.items()))
			if spH1 == 1 and hand1 + 11 <= 21:
				spH1 = 11
				hand1 += spH1
			elif spH1 == 1 and x == 11:
				x = 1
				hand1 = x + spH1 + sp1
			elif x == 11 and hand1 + spH1 > 21:
				x = 1
				hand1 = x + sp1 + spH1
			else:
				hand1 += spH1
			print "You drew the %s and now have %d." %(handHit1, hand1)
			if hand1 >= 22:
				print "You bust on your first hand with %d!." %hand1
				break
			else:
				pass
			print "Hit or stand?"
			h1Again = raw_input(">")
			if h1Again == 'h':
				continue
			else:
				print "You stand with %d on your first hand." %hand1
				break
	elif h1 == 'dd':
		betDouble1 += 1
		ddHand1, ddH1 = random.choice(list(deck.items()))
		if ddH1 == 1 and hand1 + 11 <= 21:
			ddH1 = 11
			hand1 += ddH1
		elif sp1 == 11 and hand1 + ddH1 > 21:
			sp1 = 1
			hand1 = x + sp1 + ddH1
		elif x == 11 and hand1 + ddH1 > 21:
			x = 1
			hand1 = x + sp1 + ddH1
		else:
			hand1 += ddH1
		if hand1 > 21:
			print "You drew the %s and bust with %d!" %(ddHand1, hand1)
		else:
			print "You double down on your first hand  and draw a %s for a total of %d. Good luck!" %(ddHand1, hand1)
	elif h1 == 's':
		print "You stand on your first hand with %d." %hand1
	else:
		pass
	print "You drew the %s for your second hand and now have %d." %(spCard2, hand2)
	print "Hit, Double Down, or stand?"
	h2 = raw_input(">")
	if h2 == 'h':
		while True:
			handHit2, spH2 = random.choice(list(deck.items()))
			if spH2 == 1 and hand2 + 11 <= 21:
				spH2 = 11
				hand2 += spH2
			elif spH2 == 1 and y == 11:
				y = 1
				hand2 = y + spH2 + sp2
			elif y == 11 and hand2 + spH2 > 21:
				y = 1
				hand2 = y + sp2 + spH2
			else:
				hand2 += spH2
			print "You drew the %s and now have %d." %(handHit2, hand2)
			if hand2 >= 22:
				print "You bust on your second hand with %d!." %hand2
				break
			else:
				pass
			print "Hit or stand?"
			h2Again = raw_input(">")
			if h2Again == 'h':
				continue
			else:
				print "You stand with %d on your second hand." %hand2
				break
	elif h2 == 'dd':
		betDouble2 += 1
		ddHand2, ddH2 = random.choice(list(deck.items()))
		if ddH2 == 1 and hand2 + 11 <= 21:
			ddH2 = 11
			hand2 += ddH2
		elif sp2 == 11 and hand2 + ddH2 > 21:
			sp2 = 1
			hand2 = y + sp2 + ddH2
		elif y == 11 and hand2 + ddH2 > 21:
			y = 1
			hand2 = y + sp2 + ddH2
		else:
			hand2 += ddH2
		if hand2 > 21:
			print "You drew the %s and bust with %d!" %(ddHand2, hand2)
		else:
			print "You doubled down on your second hand and drew the %s for a total of %d. Good luck!" %(ddHand2, hand2)
	elif h2 == 's':
		print "You stand on your second hand with a total of %d." %hand2
	else:
		pass

	return [hand1, hand2, betDouble1, betDouble2]

bet = 0
bank = 0

# App starts here
print "Welcome to Blackjack v.1.5!"
print "How much would you like to cash in for your bank?"
while True:
	try:
		bank = int(raw_input("$"))
		break
	except ValueError:
		print "That wasn't a number, doofus."
		continue
print "Great, starting off with $%d. Good luck!" %bank

while True:
	if bank <= 0:
		print "You are totally out of money! Add more to your bank?"
		bank = input("$")
	else:
		pass
	if bet == 0:
		print "You have $%d left in your bank. How much would you like to bet?" %bank
	else:
		print "You have $%d left in your bank. How much would you like to bet? Hit Enter to repeat your last bet of $%d." %(bank, bet)
	try:
		bet = int(raw_input("$?"))
	except ValueError:
		if bet == 0:
			print "Nice try, but you didn't bet anything, the dealer got annoyed and hits you with a shoe."
			continue
		else:
			pass
	if bet > bank:
		print "You simply don't have the funds for a bet that size!"
		continue
	else:
		print "You bet $%d." %bet

	card1, x = random.choice(list(deck.items()))
	card2, y = random.choice(list(deck.items()))

	dCard1, d1 = random.choice(list(deck.items()))
	dCard2, d2 = random.choice(list(deck.items()))
	dVal = d1 + d2

	if x == 1 and y != 1:
		x = 11
	elif y == 1 and x != 1:
		y = 11
	else:
		pass

	handVal = x + y
	if handVal == 21:
		print "Blackjack! %s You drew the %s and the %s and have shamed the dealer!" %(win[random.randint(0, len(win)-1)], card1, card2)
		bank += bet*2
		continue
	else:
		pass

	print "You drew the %s and the %s for a total of %d. The dealer is showing the %s." %(card1, card2, handVal, dCard2)

# Insurance
	if d2 == 1:
		print "Insurance?"
		ins = raw_input("y/n?")
		if ins == 'y':
			print "The dealer checks their cards..."
			if d1 == 10:
				print "Oops, dealer has 21."
				bank -= bet/2
				continue
			else:
				print "The dealer does not have 21!"
				bank -= bet/2
		else:
			print "You decline insurance and the dealer checks their cards..."
			if d1 == 10:
				print "They have 21! ", lose[random.randint(0, len(lose)-1)]
				bank -= bet
				continue
			else:
				print "The dealer does not have 21! Phew, carry on."
	if x == y:
		print "Hit(h), Split(sp), Double Down(dd), Surrender(su), or Stand(s)?"
		choice = raw_input("h, sp, dd, su,  s >")
	else:
		print "Hit(h), Double Down(dd), Surrender(su), or Stand(s)?"
		choice = raw_input("h, dd, su,  s >")
	if choice == 'h' or choice == 'H':
		handVal = hit(handVal, x, y)
	elif x == y and choice == 'sp':
		if bank - bet*2 <= 0:
			print "You don't have enough chips for that! Try hitting instead, you silly goose!"
			handVal = hit(handVal, x, y)
		else:
			handsplit = split(x, y)
	elif choice == 'dd':
		handVal = doubleDown(handVal, x, y)
	elif choice == 'su':
		print "You decide to Surrender, chickening out, buggering off, bravely turning your tail and fleeing! The dealer had %d." %dVal
		bank -= bet/2
		continue
	elif choice == 's':
		print "You stand on %d." %handVal

	if handVal >= 22:
		print "You bust! %s The dealer had %d." %(lose[random.randint(0, len(lose)-1)], dVal)
		bank -= bet
		continue
	else:
		pass


	dVal = dealer(dCard1, dCard2, d1, d2)
	if dVal >= 22 and handVal <= 21:
		print "The dealer busts with %d! %s" %(dVal, win[random.randint(0, len(win)-1)])
		if choice == 'dd':
			bank += bet*2
		elif choice == 'sp':
			if handsplit[0] <= 21 and handsplit[1] <= 21:
				print "Both your split hands win!"
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
			print "Your first hand loses!"
			if betDouble1 == 1:
				bank -= bet*2
			else:
				bank -= bet
		elif hand1 == dVal:
			print "Your first hand is a push!"
		else:
			print "You win with your first hand!"
			if betDouble1 == 1:
				bank += bet*2
			else:
				bank += bet
		if hand2 < dVal or hand2 >= 22:
			if betDouble2 == 1:
				bank -= bet*2
			else:
				bank -= bet
			print "Your second hand loses!"
			continue
		elif hand2 == dVal:
			print "Your second hand pushes!"
			continue
		else:
			if betDouble2 == 1:
				bank += bet*2
			else:
				bank += bet
			print "Your second hand wins! %s" %win[random.randint(0, len(win)-1)]
			continue
	else:
		pass
	if handVal < dVal:
		print lose[random.randint(0, len(lose)-1)]
		if choice == 'dd':
			bank -= bet*2
		else:
			bank -= bet
	elif handVal == dVal:
		print "It's a push!"
	else:
		print win[random.randint(0, len(win)-1)]
		if choice == 'dd':
			bank += bet*2
		else:
			bank += bet
	continue