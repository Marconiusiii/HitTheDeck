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
			discard.append(card)
			if discard.count(card) == deckAmount:
				del deck[card]
				continue
			else:
				break
	return card, cardVal


print "how many decks?"
deckAmount = input("> ")


deck = deckGenerator()

while True:
	if len(deck) <= 10:
		print "Shuffling the Deck!"
		deck = deckGenerator()
	else:
		pass
	card1, x = draw(deck, deckAmount)
	card2, y = draw(deck, deckAmount)
	print "You drew the %s and the %s for a total of %d. The deck now has %d cards." %(card1, card2, (x + y), len(deck))
	
	raw_input("Hit Enter to continue.")
	continue