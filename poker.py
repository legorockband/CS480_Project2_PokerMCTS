import random 
import math

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
    
    def __str__(self):
        return f"{self.value} of {self.suit}"

class Deck:
    def __init__(self):
        suits = ["Hearts", "Spades", "Clubs", "Diamonds"]
        values = ["A", "2", "3", "4", "5", "6" ,"7", "8", "9", "10", "J", "Q", "K"]
        self.cards = [Card(suit, value) for suit in suits for value in values]          ## Create Deck with all 52 cards
        
    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        if not self.cards:
            return None  
        return self.cards.pop()

    def __len__(self):
        return len(self.cards)



class Nodes:
    def __init__(self, ):
        pass

class Player:
    def __init__(self, card1: Card, card2: Card):
        self.card1 = card1
        self.card2 = card2

    def hand_properties(self):
        if self.card1.suit == self.card1.suit:
            return "Same Suit!!!"
        if self.card1.value == self.card2.value:
            return "You have a pair"


def poker():
    deck = Deck()
    deck.shuffle()       ## Create a new shuffled deck

    player1_hand = []
    player2_hand = []

    ## Deal 2 cards to each player
    for _ in range(2):
        player1_hand.append(deck.deal_card())
        player2_hand.append(deck.deal_card())

    print("Player1's Hand:")
    for card in player1_hand:
        print(card)

    print("\nPlayer2's Hand:")
    for card in player2_hand:
        print(card)


def mcts():

    return 0

def ucb1(wins, num_sim_child, num_sim_parents, c=math.sqrt(2)):
    return wins/num_sim_child + c * math.sqrt(math.log(num_sim_parents) / num_sim_child)




if __name__ == "__main__":
    poker()    