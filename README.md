# Hit The Deck!

A blind coder's first attempt at making a Python-based Blackjack game.


## Welcome to my game!

This Blackjack game runs in Terminal, iTerm, or whatever shell program you have  to work and run with Python. Double-clicking the file should launch the game in your Terminal app, otherwise from your favorite shell, navigate to the HitTheDeck directory and type:

$ python HitTheDeck_2.command

This is a fully featured Blackjack game, containing the ability to Surrender, Split, Double Down, plus has a multi- or single-deck option for play.

### Starting the Game
Start off the game by cashing in money for your bank. You will then be prompted to choose how many decks you'd like to play with. Once chosen, the game starts and will ask you for a bet. You have the option to hit Enter to repeat the last bet you made after a round completes.

### Playing the Game
YOU will be dealt two cards and shown the top facing card of the dealer. From here you will have the option to Hit, Stand, Double Down, or Surrender. These are activated using shortcodes that appear next to their names and hitting Enter.

* Type *h to Hit.
* Type *s to Stand.
* Type *dd to Double Down.
* Type *sp to Split if you are dealt two cards of the same value.
* Type *su to Surrender and get half of your bet back.

### How to Blackjack
The point of the game is to get your hand as close to 21 as possible without Busting, or going over 21. You face off against the Dealer who will flip over their hole card and hit until they hit a Soft 17 or higher or Bust.

### Double Down
Doubling Down doubles your bet and you only get 1 card.

### Splitting your Hand
Splitting allows you to play two separate hands at once off of two cards of the same rank. In this game, you are allowed to split Aces and hit more than once on each hand.

### 5 Card Charlie
This game has the 5 Card Charlie feature enabled, where you will win even money when you hit 3 or more times without busting. This gets paid out before the Dealer phase.

### Winning the Game
You win your bet if the Dealer busts or your hand(s) defeat the Dealer's hand. That will get added to your bank and the round will restart asking you for your bet.
 
### Losing the Game
You lose if you hit and your hand goes over 21 or if the Dealer's hand defeats yours. Your bet will be deducted from your bank and the round will restart asking you for your new bet.

### Running out of money and Quitting the Game
If you run out of money, you have the option to add more to your bank or hit Ctrl-C to exit the game. You can exit the game at any time by hitting Ctrl-C or closing your Terminal session.

## Thanks for playing and enjoy!