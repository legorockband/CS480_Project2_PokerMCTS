import random 
import math
from itertools import combinations

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.rank = self.card_rank(value)
    
    def card_rank(self, value):
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                 '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return ranks[value]

    def __str__(self):
        return f"{self.value} of {self.suit}"
    
    def __eq__(self, other_card):
        return self.suit == other_card.suit and self.value == other_card.value

    def __hash__(self):
        return hash((self.suit, self.value))

class Deck:
    def __init__(self):
        suits = ["Hearts", "Spades", "Clubs", "Diamonds"]
        values = ["A", "2", "3", "4", "5", "6" ,"7", "8", "9", "10", "J", "Q", "K"]
        self.cards = [Card(suit, value) for suit in suits for value in values]          ## Create Deck with all 52 cards
        
    def remove(self, cards):
        self.cards = [c for c in self.cards if c not in cards]
    
    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self, n):
        dealt = self.cards[:n]
        self.cards = self.cards[n:]
        return dealt

    def sample(self, k):
        return random.sample(self.cards, k)

class Node:
    def __init__(self, my_hand, opp_hand=[], board=[], deck=None, level=0, parent=None):
        self.my_hand = my_hand
        self.opp_hand = opp_hand
        self.board = board
        self.deck = deck or Deck()
        self.deck.remove(my_hand + opp_hand + board)
        self.level = level
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        self.sampled = set()

    # Only 5 levels in poker (You get cards, Opponent gets some cards, Flop, Turn, and River)
    def is_terminal(self):
        return self.level == 4

    def ucb1(self, child):
        if child.visits == 0:
            return float('inf')     # Encourage exploration 
        c = math.sqrt(2)    
        exploit = child.wins / child.visited    ## wi / ni
        explore = c * math.sqrt(math.log(self.visits) / child.visits)
        return exploit + explore

    def selection(self):
        return max(self.children, key=self.ucb1)

    def expand(self):
        full_deck = Deck()
        known_cards = self.my_hand + self.opp_hand + self.board
        full_deck.remove(known_cards)

        try:
            # Opponent gets 2 cards 
            if self.level == 0:
                if len(full_deck.cards) < 2:
                    return None
                new_opp = tuple(full_deck.sample(2))       
                if new_opp in self.sampled:
                    return self.expand()
                self.sampled.add(new_opp)
                return Node(self.my_hand, list(new_opp), [], None, 1, self)

            # Flop (3 cards on the table)
            elif self.level == 1:
                if len(full_deck.cards) < 3:
                    return None
                flop = tuple(full_deck.sample(3))           
                if flop in self.sampled:
                    return self.expand()
                self.sampled.add(flop)
                return Node(self.my_hand, self.opp_hand, list(flop), None, 2, self)

            # Turn (1 new card on table)
            elif self.level == 2:
                if len(full_deck.cards) < 1:
                    return None
                turn = tuple(full_deck.sample(1))
                if turn in self.sampled:
                    return self.expand()
                self.sampled.add(turn)
                return Node(self.my_hand, self.opp_hand, self.board + list(turn), None, 3, self)

            # River (1 final card on the table)
            elif self.level == 3:
                if len(full_deck.cards) < 1:
                    return None
                river = tuple(full_deck.sample(1))
                if river in self.sampled:
                    return self.expand()
                self.sampled.add(river)
                return Node(self.my_hand, self.opp_hand, self.board + list(river), None, 4, self)

        except ValueError:
            return None
    
    def rollout(self):
        # Clone deck to avoid altering the real one
        temp_deck = Deck()
        temp_deck.remove(self.my_hand + self.opp_hand + self.board)

        # Complete the board to 5 cards
        completed_board = self.board[:]
        needed = 5 - len(completed_board)
        completed_board += temp_deck.sample(needed)

        # Get the score for my hand vs opponents potential hand
        my_score = hand_eval(self.my_hand + completed_board)
        opp_score = hand_eval(self.opp_hand + completed_board)

        # Determine a clear winner at the final stage
        if my_score > opp_score:
            return 1
        elif my_score < opp_score:
            return 0
        else:
            return 0.5

    def backpropagate(self, reward):
        # Send whether the terminal value to all previous parents and root
        self.visits += 1
        self.wins += reward
        if self.parent:
            self.parent.backpropagate(reward)

def hand_eval(cards):
    assert len(cards) >= 5
    best = max((hand_strength(list(combo)) for combo in combinations(cards, 5)  ))
    return best

def hand_strength(cards: list[Card]):
    ranks = sorted([card.rank for card in cards], reverse=True)             # Get the ranks for your cards and the table cards
    suits = [card.suit for card in cards]                                   # Get the suits for your cards and the table cards

    rank_count = {r: ranks.count(r) for r in set(ranks)}                    # Input: {A, A, 3, 4, 4} -> {14: 2, 4: 2, 3: 1}
    rank_groups = sorted(rank_count.items(), key=lambda x: (-x[1], -x[0]))  # Input: {14: 2, 4: 2, 3: 1} -> [(14, 2), (4, 2), (3, 1)]
    counts = [count for rank, count in rank_groups]                         # Get Frequency of values Input: [(14, 2), (4, 2), (3, 1)] -> [2, 2, 1] (Two Pairs and Another card)
    unique_ranks = [rank for rank, count in rank_groups]                    # Used to break ties for better hands (Ace pair > 4 pair)
    
    is_royal = set([10, 11, 12, 13, 14]).issubset(set(ranks))               # Are the royal ranks on the table and in your hand  
    is_flush = len(set(suits)) == 1
    is_straight, straight_strength = has_straight(ranks)

    if is_flush and is_straight and is_royal:
        return 9                                                            # Royal Flush
    if is_flush and is_straight:
        return (8, straight_strength)                                       # Straight Flush
    if counts == [4, 1]:
        return (7, unique_ranks[0], unique_ranks[1])                        # Four of a Kind
    if counts == [3, 2]:
        return (6, unique_ranks[0], unique_ranks[1])                        # Full House
    if is_flush:
        return (5, *ranks)                                                  # Flush
    if is_straight:
        return (4, straight_strength)                                       # Straight
    if counts == [3, 1, 1]:
        return (3, unique_ranks[0], unique_ranks[1], unique_ranks[2])       # Three of a kind
    if counts == [2, 2, 1]:
        return (2, unique_ranks[0], unique_ranks[1], unique_ranks[2])       # Two Pair
    if counts == [2, 1, 1, 1]:
        return (1, unique_ranks[0], unique_ranks[1], unique_ranks[2], unique_ranks[3])  # Pair
    
    return (0, *ranks)                                                      # High Card

def has_straight(ranks):
    # Sort the card ranks from low to high
    ranks = sorted(set(ranks))

    # Ace Low straight
    if {14, 2, 3, 4, 5}.issubset(ranks):
        return True, 5
    
    for i in range(len(ranks) - 4):
        if ranks[i + 4] - ranks[i] == 4:    # Is the difference between the 5 cards 4? 
            return True, ranks[i]
    return False, None

def mcts(my_hand, num_simulations = 1000):
    root = Node(my_hand)

    for _ in range(num_simulations):
        node = root
        
        while not node.is_terminal():
            if len(node.sampled) < 1000:
                child = node.expand()
                if child is None:
                    break
                node.children.append(child)
                result = child.rollout()
                child.backpropagate(result)
                break
            else:
                node = node.select()
    return root.wins / root.visits if root.visits > 0 else 0

if __name__ == "__main__":
    deck = Deck()
    deck.shuffle()
    my_hand = [deck.deal_card(1)[0], deck.deal_card(1)[0]]
    print("My Hand:", my_hand[0], "and", my_hand[1])

    est_prob = mcts(my_hand, num_simulations=1000)
    print(f"Estimated win probability: {est_prob:.2%}")