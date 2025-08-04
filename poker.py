import random 
import math

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

    def deal_card(self):
        if not self.cards:
            return None  
        return self.cards.pop()

    def sample(self, k):
        return random.sample(self.cards, k)

class Poker:
    def __init__(self, my_hand:list[Card, Card], opp_hand:list[Card, Card], turn = 0, max_turns = 1):
        self.my_hand = my_hand or []
        self.opp_hand = opp_hand or []
        self.turn = turn
        self.max_turns = max_turns

    def get_legal_actions(self):
        return ['check']

    def perform_action(self,action):
        return Poker(
            self.my_hand,
            self.opp_hand,
            turn=self.turn + 1,
            max_turns=self.max_turns
        )
    
    def is_terminal(self):
        return self.turn >= self.max_turns
    
    def get_result(self):
        if self.my_hand > self.opp_hand:
            return 1
        elif self.my_hand < self.opp_hand:
            return 0
        else:
            return 0.5
    
    def clone(self):
        return Poker(self.my_hand, self.opp_hand, self.turn, self.max_turns)

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visited = 0
        self.wins = 0
        self.remain_actions = state.get_legal_actions()

    def full_expaned(self):
        return len(self.remain_actions) == 0

    def is_terminal(self):
        return self.state.is_terminal()

    def selection(self, c=math.sqrt(2)):
        def ucb1(child):
            if child.visited == 0:
                return float('inf')
            
            exploit = child.wins / child.visited    ## wi / ni
            explore = c * math.sqrt(math.log(self.visited) / child.visted)
            return exploit + explore

        return max(self.children, key=ucb1)

    def expand(self):
        action = self.remain_actions.pop()
        next_state = self.state.perform_action(action)
        child_node = Node(next_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node
    
    def rollout(self):
        current_state = self.state.clone()
        while not current_state.is_terminal():
            legal_actions = current_state.get_legal_actions()
            action = random.choice(legal_actions)
            current_state = current_state.perform_action(action)
        return current_state.get_result()

    def backpropagate(self, reward):
        self.visited += 1
        self.wins += reward
        if self.parent:
            self.parent.backpropagate(reward)

def hand_strength(cards: list[Card]):
    ranks = [card.rank for card in cards]       ## Get the ranks for your cards and the table cards
    suits = [card.suit for card in cards]       ## Get the suits for your cards and the table cards

    rank_count = {}
    for r in ranks:
        if r in rank_count:
            rank_count[r] += 1
        else:
            rank_count[r] = 1
    
    suit_count = {}
    for s in suits:
        if s in suit_count:
            suit_count[s] += 1
        else:
            suit_count[s] = 1
    
    is_royal = sorted(rank_count) == {10, 11, 12, 13, 14}   ## 10, J, Q, K, A
    is_flush = any(count >= 5 for count in suit_count.values())
    is_straight = has_straight(ranks)

    counts = list(rank_count.values())
    is_four = 4 in counts
    is_three = 3 in counts
    pair_total = counts.count(2)

    if is_flush and is_straight and is_royal:
        return 9    # Royal Flush
    elif is_flush and is_straight:
        return 8    # Straight Flush
    elif is_four:
        return 7    # Four of a Kind
    elif is_three and pair_total >= 1:
        return 6    # Full House
    elif is_flush:
        return 5    # Flush
    elif is_straight:
        return 4    # Straight
    elif is_three:
        return 3    # Three of a Kind
    elif pair_total >= 2:
        return 2    # Two Pair
    elif pair_total == 1:
        return 1    # Pair
    else:
        return 0    # High Card

def has_straight(ranks):
    ## Sort the card ranks from low to high
    ranks = sorted(set(ranks))

    ## Ace Low straight
    if {14, 2, 3, 4, 5}.issubset(ranks):
        return True
    
    for i in range(len(ranks) - 4):
        if ranks[i + 4] - ranks[i] == 4:
            return True
    return False

def mcts(my_hand, num_simulations = 1000):
    win_count = 0

    for _ in range(num_simulations):
        deck = Deck()
        # Remove cards already in my hand
        deck.cards = [c for c in deck.cards if not any(
            c.value == h.value and c.suit == h.suit for h in my_hand)]
        deck.shuffle()

        opp_hand = [deck.deal_card(), deck.deal_card()]

        root_state = Poker(my_hand, opp_hand)
        root_node = Node(root_state)

        node = root_node

        while not node.is_terminal():
            if not node.full_expaned():
                node = node.expand()
                break
            else:
                node = node.selection()
        result = node.rollout()
        node.backpropagate(result)
        win_count += result

    return win_count / num_simulations

if __name__ == "__main__":
    deck = Deck()
    deck.shuffle()
    my_hand = [deck.deal_card(), deck.deal_card()]

    print("My Hand:")
    for card in my_hand:
        print(card)

    board_card = [deck.deal_card(), deck.deal_card(), deck.deal_card(), deck.deal_card(), deck.deal_card()]
    print("Board Cards:")
    for card in board_card:
        print(card)

    my_score = hand_strength(my_hand + board_card)
    print(my_score)

    # win_prob = mcts(my_hand, num_simulations=1000)
    # print(f"\nEstimated Win Probability: {win_prob:.2%}")