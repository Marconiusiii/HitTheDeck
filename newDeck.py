import random

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

def deckGenerator():
	d = {}
	for suit in suits:
		for card, val in cardValues.iteritems():
			d ['{} of {}'.format(card, suit)] = val
	return d


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

def handCount(playerHand):
	count = 0
	for i in playerHand:
		count += i
	return count

print "how many decks?"
deckAmount = input("> ")


deck = deckGenerator()

while True:
	if len(deck) <= 15:
		print "Shuffling the Deck!"
		deck = deckGenerator()
	else:
		pass
	card1, x = draw(deck, deckAmount)
	card2, y = draw(deck, deckAmount)
	if x == 1 and y == 1:
		x = 11
	elif x == 1:
		x = 11
	elif y == 1:
		y = 11

	playerHand = [x, y]
	playerTotal = handCount(playerHand)
	print "You drew the %s and the %s for a total of %d. The deck now has %d cards." %(card1, card2, playerTotal, len(deck))
	while True:
		hit, h1 = draw(deck, deckAmount)
		if h1 == 1 and playerTotal + 11 <= 21:
			h1 = 11
		elif x == 11 and playerTotal + h1 > 21:
			playerHand[0] = 1
		elif y == 11 and playerTotal + h1 > 21:
			playerHand[1] = 1
		playerHand.append(h1)
		playerTotal = handCount(playerHand)
		print "You drew the %s and now have %d." %(hit, playerTotal)
		choice = raw_input("Hit? Y or N")
		if choice == 'y':
			continue
		else:
			break

	continue