import random
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union

from chatarena.environments import Environment, register_env
from chatarena.environments.base import TimeStep
from chatarena.message import Message, MessagePool
from src.environments.base import Parser

ENDINGS = [
    "And so, they lived happily ever after, free from the sorrows of the past.",
    "With the curse finally broken, peace and joy returned to the kingdom.",
    "As the sun set, they realized that true love had conquered all.",
    "With the dragon defeated, the village flourished like never before.",
    "The mysterious enchantment was lifted, revealing the truth hidden for ages.",
    "They found the hidden treasure, which brought prosperity to their land.",
    "With a single act of kindness, the spell was broken, and harmony restored.",
    "The hero's bravery saved the kingdom, and they were hailed forevermore.",
    "As the clock struck midnight, everything magically returned to normal.",
    "The lost prince was found, and the kingdom rejoiced in his return.",
    "With the wicked witch gone, the forest bloomed anew.",
    "Their journey ended where it began, but they were no longer the same.",
    "And with the final word of the prophecy fulfilled, peace reigned.",
    "The secret door was closed, sealing away the ancient fears.",
    "They returned victorious, with stories that would be told for generations.",
    "In the end, the truth was revealed, and justice was served.",
    "The spell was broken, and the beast returned to his true form.",
    "As the magical land healed, its inhabitants celebrated their newfound freedom.",
    "The once silent kingdom erupted in song and dance, free at last.",
    "And so, with the villain vanquished, the land prospered once again.",
    "The hero's quest was complete, and they returned home a changed person.",
]

class CardType(Enum):
    CHARACTER = 1
    EVENT = 2
    THING = 3
    PLACE = 4
    ASPECT = 5

@dataclass
class Card:
    text: str
    type: CardType 
    interrupt: bool = False

    def __repr__(self) -> str:
        card = f"{self.text} ({self.type.name})"
        if self.interrupt:
            card += " (Interrupt)"
        return card

CARDS = [
    Card("Wolf", CardType.CHARACTER),
    Card("Prince", CardType.CHARACTER),
    Card("Princess", CardType.CHARACTER),
    Card("Knight", CardType.CHARACTER),
    Card("King", CardType.CHARACTER),
    Card("Queen", CardType.CHARACTER),
    Card("Fairy", CardType.CHARACTER),
    Card("Witch", CardType.CHARACTER),
    Card("Wizard", CardType.CHARACTER),
    Card("Dragon", CardType.CHARACTER),
    Card("Unicorn", CardType.CHARACTER),
    Card("Ogre", CardType.CHARACTER),
    Card("Giant", CardType.CHARACTER),
    Card("Troll", CardType.CHARACTER),
    Card("Dwarf", CardType.CHARACTER),
    Card("Elf", CardType.CHARACTER),
    Card("Goblin", CardType.CHARACTER),
    Card("Ghost", CardType.CHARACTER),
    Card("Vampire", CardType.CHARACTER, interrupt=True),
    Card("Werewolf", CardType.CHARACTER, interrupt=True),
    Card("Zombie", CardType.CHARACTER, interrupt=True),
    Card("Robot", CardType.CHARACTER, interrupt=True),
    Card("Alien", CardType.CHARACTER, interrupt=True),
    Card("Mermaid", CardType.CHARACTER, interrupt=True),
    Card("Pirate", CardType.CHARACTER, interrupt=True),
    Card("Ninja", CardType.CHARACTER, interrupt=True),
    Card("Dungeon", CardType.PLACE),
    Card("Castle", CardType.PLACE),
    Card("Forest", CardType.PLACE),
    Card("Mountain", CardType.PLACE),
    Card("Cave", CardType.PLACE),
    Card("River", CardType.PLACE),
    Card("Lake", CardType.PLACE),
    Card("Ocean", CardType.PLACE),
    Card("Island", CardType.PLACE),
    Card("Village", CardType.PLACE),
    Card("City", CardType.PLACE),
    Card("Town", CardType.PLACE),
    Card("School", CardType.PLACE),
    Card("Library", CardType.PLACE),
    Card("Museum", CardType.PLACE),
    Card("Market", CardType.PLACE),
    Card("Restaurant", CardType.PLACE),
    Card("Circus", CardType.PLACE, interrupt=True),
    Card("Amusement Park", CardType.PLACE, interrupt=True),
    Card("Carnival", CardType.PLACE, interrupt=True),
    Card("Cemetery", CardType.PLACE, interrupt=True),
    Card("Jungle", CardType.PLACE, interrupt=True),
    Card("Desert", CardType.PLACE, interrupt=True),
    Card("Space", CardType.PLACE, interrupt=True),
    Card("Underwater", CardType.PLACE, interrupt=True),
    Card("Axe", CardType.THING),
    Card("Sword", CardType.THING),
    Card("Shield", CardType.THING),
    Card("Bow", CardType.THING),
    Card("Arrow", CardType.THING),
    Card("Spear", CardType.THING),
    Card("Book", CardType.THING),
    Card("Scroll", CardType.THING),
    Card("Crown", CardType.THING),
    Card("Ring", CardType.THING),
    Card("Necklace", CardType.THING),
    Card("Chest", CardType.THING),
    Card("Key", CardType.THING),
    Card("Map", CardType.THING),
    Card("Compass", CardType.THING),
    Card("Lamp", CardType.THING),
    Card("Mirror", CardType.THING),
    Card("Painting", CardType.THING),
    Card("Statue", CardType.THING),
    Card("Candle", CardType.THING),
    Card("Rope", CardType.THING),
    Card("Potion", CardType.THING),
    Card("Wand", CardType.THING),
    Card("Magic Carpet", CardType.THING, interrupt=True),
    Card("Magic Mirror", CardType.THING, interrupt=True),
    Card("Magic Wand", CardType.THING, interrupt=True),
    Card("Fire", CardType.THING, interrupt=True),
    Card("Blind", CardType.ASPECT),
    Card("Deaf", CardType.ASPECT),
    Card("Poisoned", CardType.ASPECT),
    Card("Sleeping", CardType.ASPECT),
    Card("Cursed", CardType.ASPECT),
    Card("Blessed", CardType.ASPECT),
    Card("Lost", CardType.ASPECT),
    Card("Confused", CardType.ASPECT),
    Card("Frightened", CardType.ASPECT),
    Card("Invisible", CardType.ASPECT),
    Card("Frozen", CardType.ASPECT),
    Card("Sick", CardType.ASPECT),
    Card("Sad", CardType.ASPECT),
    Card("Happy", CardType.ASPECT),
    Card("Angry", CardType.ASPECT),
    Card("Jealous", CardType.ASPECT),
    Card("Brave", CardType.ASPECT),
    Card("Cowardly", CardType.ASPECT),
    Card("Strong", CardType.ASPECT),
    Card("Weak", CardType.ASPECT),
    Card("Smart", CardType.ASPECT, interrupt=True),
    Card("Dumb", CardType.ASPECT, interrupt=True),
    Card("Rich", CardType.ASPECT, interrupt=True),
    Card("Poor", CardType.ASPECT, interrupt=True),
    Card("Old", CardType.ASPECT, interrupt=True),
    Card("Young", CardType.ASPECT, interrupt=True),
    Card("Beautiful", CardType.ASPECT, interrupt=True),
    Card("Ugly", CardType.ASPECT, interrupt=True),
    Card("Found", CardType.EVENT),
    Card("Lost", CardType.EVENT),
    Card("Rescued", CardType.EVENT),
    Card("Meeting", CardType.EVENT),
    Card("Someone is hurt", CardType.EVENT),
    Card("Someone is missing", CardType.EVENT),
    Card("Someone is in danger", CardType.EVENT),
    Card("Falls in love", CardType.EVENT, interrupt=True),
    Card("Kidnapped", CardType.EVENT, interrupt=True),
]


@dataclass
class Hand:
    cards: List[Card]
    ending: Optional[str]

    @property
    def empty(self):
        return len(self.cards) == 0

    def play_card(self, card: Card):
        self.cards.remove(card)
        return card
    
    def __str__(self) -> str:
        return f"Cards in Hand: {self.cards}\nEnding: {self.ending}"


class Deck:
    def __init__(self, hand_size: int = 5):
        self.hand_size = hand_size
        self.reset()

    def reset(self) -> None:
        self.cards = CARDS.copy()
        self.endings = ENDINGS.copy()
        self.discards = []
        self.shuffle()

    def shuffle(self) -> None:
        self.cards = self.cards + self.discards
        random.shuffle(self.cards)
        self.discards = []
        random.shuffle(self.endings)

    def draw_card(self) -> Card:
        return self.cards.pop()

    def draw_ending(self) -> str:
        return self.endings.pop()

    def draw_hand(self) -> Hand:
        cards = []
        for _ in range(self.hand_size):
            if not self.cards:
                self.shuffle()
            if not self.cards:
                self.reset()
            cards.append(self.draw_card())
        ending = self.draw_ending()
        return Hand(cards=cards, ending=ending)


class ActionType(Enum):
    TELL_STORY = 1
    PASS = 2
    INTERRUPT = 3
    CHALLENGE = 4


def parse_action(action: str) -> Optional[ActionType]:
    if action.lower().startswith('interruption'):
        return ActionType.INTERRUPT
    if action.lower().startswith('pass'):
        return ActionType.PASS
    if action.lower().startswith('challenge'):
        return ActionType.CHALLENGE
    parser = Parser()
    action_type = parser(f'Which category does this action belong to?\n>{action}\nSay only "tell story", "pass", "interrupt", or "challenge".')
    if "tell story" in action_type.lower():
        return ActionType.TELL_STORY
    elif "pass" in action_type.lower():
        return ActionType.PASS
    elif "interrupt" in action_type.lower():
        return ActionType.INTERRUPT
    elif "challenge" in action_type.lower():
        return ActionType.CHALLENGE
    return None

def cards_used(action, cards) -> List[Card]:
    parser = Parser()
    cards_used_answer = parser(f'Which of the following story elements appeared in this paragraph?\nStory Elements: {cards}\nParagraph: {action}\nSay only the card text, separated by commas.')
    return [card for card in cards if card.text.lower() in cards_used_answer.lower()]

def used_ending(action, ending) -> bool:
    if action.lower().endswith(ending.lower()):
        return True
    parser = Parser()
    used_ending_answer = parser(f'Did the following paragraph contain the provided ending?\n>Ending: {ending}\nParagraph: {action}\nSay only "yes" or "no".')
    return "yes" in used_ending_answer.lower()

def valid_interrupt_card(action, cards, previous_story, previously_used_cards) -> Optional[Card]:
    parser = Parser()
    interrupt_answer = parser(f'There are two ways to validly interrupt a story:\n1. By using an interrupt card, and replacing a previously used element with the new card element, on an interrupt card.\n2. By using a story element that was mentioned in the story. This does not necessarily need to be an interrupt card.\nWas this a valid interruption?\nStory: {previous_story}\nUsed Elements: {previously_used_cards}\nStory Elements Available To Use as Interruption: {[c for c in cards]}\nAttempted Interruption: {action}\nSay only the card text of the card used as an interuption. If the interuption was invalid, say invalid.')
    for card in cards:
        if card.text.lower() in interrupt_answer.lower():
            return card
    return None

class GameMode(Enum):
    TELL_STORY = 1
    INTERJECTION = 2

@register_env
class OnceUponATime(Environment):
    type_name = "once_upon_a_time"

    def __init__(self, player_names: List[str], **kwargs):
        super().__init__(player_names, **kwargs)
        self.message_pool = MessagePool()

    def reset(self) -> TimeStep:
        self.deck = Deck()
        self.hands = {player_name: self.deck.draw_hand() for player_name in self.player_names}
        self.current_player = 0
        self.current_storyteller = 0
        self.challenges = 0
        self.game_mode = GameMode.TELL_STORY
        self._initialized = False
        self.message_pool.reset()
        self.moderator_speaks(f"Now the game starts! {self.player_names[self.current_storyteller]} is the first storyteller.")
        self.last_story = None
        self.last_story_cards = []
        return TimeStep(self.get_observation(), self.get_zero_rewards(), self.is_terminal())

    def get_observation(self, player_name: Optional[str] = None) -> List[Message]:
        if not player_name:
            return self.message_pool.get_all_messages()
        messages = self.message_pool.get_visible_messages(player_name, self.message_pool.last_turn + 1)
        current_hand = self.hands[player_name]
        messages.append(Message("System", f'Your current_hand is {current_hand}', self.message_pool.last_turn))
        messages.append(Message("System", f'The current storyteller is {self.player_names[self.current_storyteller]}', self.message_pool.last_turn))
        return messages

    def get_next_player(self) -> str:
        return self.player_names[self.current_player]

    def increment_player(self):
        self.current_player = (self.current_player + 1) % len(self.player_names)
    
    def increment_storyteller(self):
        self.current_storyteller = (self.current_storyteller + 1) % len(self.player_names)

    def moderator_speaks(self, text: str, visible_to: Union[str, List[str]] = "all"):
        message = Message(agent_name="Moderator", content=text, turn=self.message_pool.last_turn + 1, visible_to=visible_to)
        self.message_pool.append_message(message)

    def begin_interjection_round(self):
        self.game_mode = GameMode.INTERJECTION
        self.increment_player()
        self.moderator_speaks(f"Do you want to challenge or interrupt the story?")

    def end_interjection_round(self):
        self.game_mode = GameMode.TELL_STORY
        self.challenges = 0
        self.moderator_speaks(f"The interjection round is over, and {self.storyteller_name} is the storyteller again.")

    @property
    def storyteller_name(self):
        return self.player_names[self.current_storyteller]
    
    def storytell_step(self, player_name: str, action: str, action_type: ActionType) -> TimeStep:
        storyteller_hand = self.hands[player_name]
        self.moderator_speaks(f"Storyteller: {self.storyteller_name}; {storyteller_hand}", visible_to='Moderator')
        if action_type != ActionType.TELL_STORY:
            self.moderator_speaks(f"{player_name} couldn't continue the story.")
            self.pass_storyteller()
            return TimeStep(self.get_observation(), self.get_zero_rewards(), self.is_terminal())
        cards_used_this_turn = cards_used(action, storyteller_hand.cards)
        for card in cards_used_this_turn:
            storyteller_hand.play_card(card)
            self.deck.discards.append(card)
        self.message_pool.append_message(Message(player_name, action, self.message_pool.last_turn + 1))
        self.moderator_speaks(f"{player_name} continued the story with the following cards: {cards_used_this_turn}")
        self.last_story = action
        self.last_story_cards = cards_used_this_turn
        if storyteller_hand.empty:
            storyteller_used_ending = used_ending(action, storyteller_hand.ending)
            if storyteller_used_ending:
                self.moderator_speaks(f"{player_name} attempted to finish the story with the ending: {storyteller_hand.ending}", visible_to='Moderator')
                storyteller_hand.ending = None
        self.begin_interjection_round()
        return TimeStep(self.get_observation(), self.get_zero_rewards(), self.is_terminal())

    def challenge_succeeds(self):
        return self.challenges > len(self.player_names) / 2

    def pass_storyteller(self, to_player: Optional[str] = None):
        storyteller_hand = self.hands[self.player_names[self.current_storyteller]]
        storyteller_hand.cards.append(self.deck.draw_card())
        if storyteller_hand.ending is None:
            storyteller_hand.ending = self.deck.draw_ending()
        if to_player:
            self.current_storyteller = self.player_names.index(to_player)
        else:
            self.increment_storyteller()
        self.current_player = self.current_storyteller
        self.game_mode = GameMode.TELL_STORY
        self.challenges = 0
        self.moderator_speaks(f"{self.player_names[self.current_storyteller]} is now the storyteller.")

    def interject_step(self, player_name: str, action: str, action_type: ActionType) -> TimeStep:
        self.increment_player()
        if action_type == ActionType.INTERRUPT:
            interrupt_card = valid_interrupt_card(action, self.hands[player_name].cards, self.last_story, self.last_story_cards)
            if interrupt_card is None:
                self.moderator_speaks(f"{player_name} has the following cards available to interrupt: {self.hands[player_name].cards}", visible_to='Moderator')
                self.message_pool.append_message(Message(player_name, f'{action}', self.message_pool.last_turn + 1, visible_to='moderator'))
                self.moderator_speaks(f"{player_name} attempted to interrupt the story with an invalid card.", visible_to='Moderator')
            else:
                self.message_pool.append_message(Message(player_name, f'{action}', self.message_pool.last_turn + 1))
                self.moderator_speaks(f"{player_name} interrupted the story with the following card: {interrupt_card.text}")
                self.last_story_cards = [interrupt_card]
                self.last_story = action
                self.hands[player_name].cards.remove(interrupt_card)
                self.deck.discards.append(interrupt_card)
                self.pass_storyteller(to_player=player_name)
        if action_type == ActionType.PASS or action_type == ActionType.TELL_STORY:
            self.message_pool.append_message(Message(player_name, action, self.message_pool.last_turn + 1, visible_to='moderator'))
            self.moderator_speaks("This was not a challenge or an interruption", visible_to='moderator')
        if action_type == ActionType.CHALLENGE:
            self.challenges += 1
            self.message_pool.append_message(Message(player_name, f'{action}', self.message_pool.last_turn + 1))
            if self.challenge_succeeds():
                self.moderator_speaks(f"{self.player_names[self.current_storyteller]} was successfully challenged")
                self.pass_storyteller()
        return TimeStep(self.get_observation(), self.get_zero_rewards(), self.is_terminal())

    def step(self, player_name: str, action: str) -> TimeStep:
        assert player_name == self.get_next_player(), f"Wrong player! It is {self.get_next_player()} turn."
        action_type = parse_action(action)
        assert action_type is not None, f"Invalid action: {action}"
        if self.game_mode == GameMode.TELL_STORY:
            return self.storytell_step(player_name, action, action_type)
        elif self.game_mode == GameMode.INTERJECTION:
            timestep = self.interject_step(player_name, action, action_type)
            if self.current_player == self.current_storyteller:
                current_player_name = self.player_names[self.current_player]
                if self.hands[current_player_name].ending is None:
                    self.moderator_speaks(f"The game is over! {self.player_names[self.current_storyteller]} wins!")
                    rewards = {player_name: 1.0 if player_name == current_player_name else 0.0 for player_name in self.player_names}
                    return TimeStep(self.get_observation(), rewards, True)
                self.end_interjection_round()
            return timestep
        raise RuntimeError("Invalid game mode.")

