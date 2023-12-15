from abc import abstractmethod
from typing import Dict, List, Type, Union

from chatarena.environments import Environment
from chatarena.environments.base import TimeStep
from chatarena.message import Message, MessagePool


class Round:
    def __init__(self, player_names: List[str], round_number: int) -> None:
        self.player_actions = {}
        self.player_names = player_names
        self.round_number = round_number

    @property
    def is_complete(self) -> bool:
        return len(self.player_actions) == len(self.player_names)

    def process_action(self, player_name: str, action: str):
        self.player_actions[player_name] = action


class SimpleRoundEnvironment(Environment):
    def __init__(self, *args, total_rounds: int, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_rounds = total_rounds
        self._initialized = False
        self.message_pool = MessagePool()
        self.reset()

    @property
    def round_class(self) -> Type[Round]:
        return Round

    @abstractmethod
    def player_scores(self) -> Dict[str, float]:
        pass

    @abstractmethod
    def begin_game(self):
        pass

    @abstractmethod
    def begin_round(self):
        pass

    @abstractmethod
    def complete_round(self):
        pass

    def reset(self):
        self.rounds = []
        self.message_pool.reset()
        self._moderator_speak(f"Now the game starts! There are {self.total_rounds} rounds.")
        self.begin_game()
        self.increment_round()
        self.begin_round()
        self._initialized = True
        return TimeStep(self.get_observation(), self.get_zero_rewards(), self.is_terminal())

    @property
    def current_round(self):
        return self.rounds[-1]

    def is_terminal(self) -> bool:
        return len(self.rounds) == self.total_rounds and self.current_round and self.current_round.is_complete
    
    def increment_round(self):
        self.rounds.append(self.round_class(self.player_names, len(self.rounds) + 1))
        self._next_player_idx = 0

    def _moderator_speak(self, text: str, visible_to: Union[str, List[str]] = "all"):
        """
        moderator say something
        """
        message = Message(agent_name="Moderator", content=text, turn=len(self.rounds), visible_to=visible_to)
        self.message_pool.append_message(message)

    def get_next_player(self) -> str:
        """
        get the next player
        """
        return self.player_names[self._next_player_idx]

    def get_observation(self, player_name=None) -> List[Message]:
        """
        get observation for the player
        """
        if player_name is None:
            return self.message_pool.get_all_messages()
        else:
            return self.message_pool.get_visible_messages(player_name, turn=len(self.rounds))

    def step(self, player_name: str, action: str) -> TimeStep:
        assert player_name == self.get_next_player(), f"Wrong player! It is {self.get_next_player()} turn."
        message = Message(agent_name=player_name, content=action, turn=len(self.rounds), visible_to="Moderator")
        self.message_pool.append_message(message)
        self.current_round.process_action(player_name, action)
        self._next_player_idx += 1
        if self.current_round.is_complete:
            self.complete_round()

            if self.is_terminal():
                self._moderator_speak(f"{self.total_rounds} rounds of decisions have been completed.")
                self._moderator_speak(f"The scores are {self.player_scores()}")
                return TimeStep(observation=self.get_observation(), reward=self.player_scores(), terminal=True)
        
            self.increment_round()
            self.begin_round()
        return TimeStep(observation=self.get_observation(), reward=self.get_zero_rewards(), terminal=False)
