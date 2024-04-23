import random
has_colorama = True
try:
    # The Colorama module is recommended but not required
    from colorama import Fore
except ImportError:
    Fore = None
    has_colorama = False


card_desc = {1: "A", 10: "T", 11: "J", 12: "Q", 13: "K"}
for i in range(2, 10):
    card_desc[i] = str(i)

card_shape = ["♣", "♦", "♥", "♠"]
if has_colorama:
    card_color = [Fore.GREEN, Fore.YELLOW, Fore.RED, Fore.BLUE]


class Card:
    def __init__(self, value, serial):
        self.value = value
        self.serial = serial
        self.shape = card_shape[self.serial]

    def __str__(self):
        if has_colorama:
            return card_color[self.serial] + self.shape + card_desc[self.value] + Fore.RESET
        else:
            return self.shape + card_desc[self.value]


deck = [Card(i, j) for i in range(1, 14) for j in range(4)]


class Hand:
    def __init__(self, location, name="Player", control="Comp", held=None, strategy_score=17, strategy_complex=None):
        location.append(self)
        self.name = name
        self.control = control
        # For AI-controlled players, initializing the strategy to stand on 17 points:
        self.strategy_score = strategy_score
        self.strategy_complex = strategy_complex
        self.held = held
        if self.held is None:
            self.held = []
        self.total_aces = self.count_aces()
        self.total_score = self.calc_score()
        self.stands = False
        self.stood = False

    def count_aces(self):
        sleeve = 0
        for counted in self.held:
            if counted.value == 1:
                sleeve += 1
        return sleeve

    def calc_score(self):
        total = 0
        for points in self.held:
            if points.value >= 10:
                total += 10
            else:
                total += points.value
        added = self.total_aces
        while total <= 11 and added > 0:
            total += 10
            added -= 1
        return total

    def peek(self):
        return ", ".join(map(str, self.held))

    def draw(self, fresh=False):
        if fresh or not deck:  # Will generates cards randomly once the deck empties
            value = random.randint(1, 13)
            serial = random.randint(0, 3)
            generated = Card(value, serial)
        else:
            generated = random.choice(deck)
            deck.remove(generated)
        self.held.append(generated)
        self.total_aces = self.count_aces()
        self.total_score = self.calc_score()

    def evaluate(self):
        if self.stood:
            return True
        elif self.stands:
            self.stand()
            self.stood = True
        elif self.total_score == 21:
            self.stands = True
            if self.control != "Comp":
                print(self.name, "got 21!")
        elif self.total_score > 21:
            self.stands = True
            if self.control != "Comp":
                print(self.name, "busted!")
        else:
            return False

    def stand(self):
        print(self.name, "stands with", len(self.held), "cards.")

    def turn(self, fresh=False):
        if self.control != "Comp":

            if len(self.held) < 2:
                self.draw(fresh)
                seen = self.peek()
                print(self.name, "drew a card.")
                print(self.name + "'s cards:", seen)
                print(self.name + "'s score:", self.total_score)
                return

            seen = self.peek()
            print("Reminder -", self.name + "'s cards are:", seen)

            decide = input(self.name + ", would you like to draw? Y/N - ")
            hesitant = decide.upper()[0] not in ["Y", "N"]
            while hesitant:
                print("Invalid input.")
                decide = input(self.name + ", would you like to draw? Y/N - ")
                hesitant = decide.upper()[0] not in ["Y", "N"]
            if decide.upper() == "N":
                self.stand()
                self.stood = True
            else:
                self.draw(fresh)
                seen = self.peek()
                print(self.name + "'s cards:", seen)
                print(self.name + "'s score:", self.total_score)

        else:
            if self.strategy_complex is not None:
                # I could add options for more nuanced strategies in the future:
                # e.g. referring to other players' observed or known strategies,
                # their hand sizes, the remaining cards in the deck, and more.
                pass

            if self.total_score < self.strategy_score:
                self.draw(fresh)
                print(self.name, "drew a card. Current hand size:", len(self.held))
            else:
                self.stand()
                self.stood = True


num_players = 4
players_location = []
dummy = ""
for num in range(num_players):
    dummy = Hand(players_location, "Player " + str(num + 1))
    if num == 0:  # Choosing Player 1 to take input from the user
        dummy.control = "Player"

players_standing = [False] * len(players_location)

for first_turn in players_location:
    first_turn.draw()


gameplay = True
while gameplay:
    for player in range(len(players_location)):
        if players_location[player].stood:
            players_standing[player] = True
            continue
        elif players_location[player].stands:
            players_location[player].stand()
            players_location[player].stood = True
            players_standing[player] = True
            continue
        players_location[player].turn()
        players_standing[player] = players_location[player].evaluate()
    print("End of the round.")
    gameplay = not all(players_standing)


scoreboard = []
print("\nTotal scores:")
for finalist in players_location:
    scoreboard.append(finalist.total_score)
    print(finalist.name + "'s cards:", finalist.peek())
    print(finalist.name, "got:", finalist.total_score)

for busted in range(len(scoreboard)):
    if scoreboard[busted] > 21:
        scoreboard[busted] = 0

winners = [player for player in players_location if player.total_score == max(scoreboard)]
pedestal = ", ".join([player.name for player in winners])
if not len(winners):
    print("Everyone lost this game!")
elif len(winners) > 1:
    print("The winners are:", pedestal + "!")
else:
    print("The winner is:", pedestal + "!")
