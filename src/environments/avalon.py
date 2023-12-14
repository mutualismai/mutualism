from enum import Enum
from typing import List

from chatarena.config import EnvironmentConfig
from chatarena.environments import Environment, register_env, TimeStep
from chatarena.message import Message

class Phase(Enum):
    TEAM_SELECTION = 1
    VOTING = 2
    QUEST = 3
    ASSASINATION = 4

class Role(Enum):
    SERVANT = 1
    MINION = 2
    MERLIN = 3
    ASSASIN = 4

@register_env
class Avalon(Environment):
    type_name = None

    def __init__(self, player_names: List[str], **kwargs):
        super().__init__(player_names=player_names, **kwargs)

    def reset(self):
        pass


    def get_next_player(self) -> str:
        pass

    def get_observation(self, player_name=None) -> List[Message]:


    def print(self):
        pass

    def step(self, player_name: str, action: str) -> TimeStep:
        """
        Execute a step in the environment given an action from a player.

        Note:
            This method must be implemented by subclasses.

        Parameters:
            player_name (str): The name of the player.
            action (str): The action that the player wants to take.

        Returns:
            TimeStep: An object of the TimeStep class containing the observation, reward, and done state.
        """
        pass

    def check_action(self, action: str, player_name: str) -> bool:
        """
        Check whether a given action is valid for a player.

        Note:
            This method must be implemented by subclasses.

        Parameters:
            action (str): The action to be checked.
            player_name (str): The name of the player.

        Returns:
            bool: True if the action is valid, False otherwise.
        """
        return True

    def is_terminal(self) -> bool:
        """
        Check whether the environment is in a terminal state (end of episode).

        Note:
            This method must be implemented by subclasses.

        Returns:
            bool: True if the environment is in a terminal state, False otherwise.
        """
        pass
