from dataclasses import dataclass
from typing import Dict, List, Union

from chatarena.environments import Environment, TimeStep, register_env
from chatarena.message import Message, MessagePool

from .parser import Parser

DEFAULT_TOPIC = """

The scoring is as follows:
- If all three choose to cooperate, they each get 3 points.
- If all three choose to defect, they each get 1 point.
- If one chooses to defect and the others choose to cooperate, the betrayer gets 100 points and the collaborators each get 0 points.
- If two choose to defect and the other chooses to cooperate, the betrayers each get 2 points, and the collaborator gets 0 points.

The game is played for 5 rounds, and the total score is calculated at the end to determine the winner.

"""

@dataclass
class Round:
    player_cooperated: Dict[str, bool]

    @property
    def cooperate_count(self):
        return sum(1 for c in self.player_cooperated.values() if c)

    @property
    def is_complete(self):
        return len(self.player_cooperated) == 3

    def __getitem__(self, player_name):
        return 'cooperate' if self.player_cooperated[player_name] else 'defect'

    def player_scores(self, payouts: Dict[str, Dict[str, int]]) -> Dict[str, float]:
        assert self.is_complete
        scores = {}
        for player, cooperated in self.player_cooperated.items():
            if cooperated:
                other_cooperated = self.cooperate_count - 1
                score = payouts['cooperate'][f'{other_cooperated}_others_cooperate']
            else:
                other_cooperated = self.cooperate_count
                score = payouts['defect'][f'{other_cooperated}_others_cooperate']
            scores[player] = score
        return scores


@register_env
class PrisonersDilemma(Environment):
    type_name = "prisoner"

    def __init__(self, player_names: List[str], rounds: int, payouts: Dict[str, Dict[str, int]], **kwargs):
        super().__init__(player_names=player_names, **kwargs)
        self.payouts = payouts
        self.total_rounds = rounds
        self.rounds = []
        self.message_pool = MessagePool()
        self.parser = Parser()
        self.reset()

    def reset(self):
        self.rounds = []
        self._current_turn = 0
        self._next_player_idx = 0
        self.message_pool.reset()

        self._moderator_speak(f"Now the game starts! There are {self.total_rounds} rounds.")
        self._moderator_speak(f"The payout matrix is as follows: {self.payouts}")
        self.new_round()
        self._initialized = True

    def get_next_player(self) -> str:
        """
        get the next player
        """
        return self.player_names[self._next_player_idx]

    def new_round(self) -> None:
        """
        start a new round
        """
        if len(self.rounds) > 0:
            self._moderator_speak(f"You can look around others' decisions and think your decision for next round. Now let us move to next round")
        else:
            self._moderator_speak(f"This the first round. Now everyone give your decision.")
        self._current_turn += 1

        self.rounds.append(Round(player_cooperated={}))
        self._next_player_idx = 0

    @property
    def current_round(self) -> Round:
        return self.rounds[-1]

    def complete_round(self) -> None:
        self._moderator_speak(f"Round {len(self.rounds)} is over.")
        self._moderator_speak(f"Player 1 said: {self.current_round['Player 1']} \nPlayer 2 said: {self.current_round['Player 2']}  \nPlayer 3 said: {self.current_round['Player 3']}")

    def add_decision(self, player_name: str, decision: bool):
        """
        add decision to the current round
        """
        self.current_round.player_cooperated[player_name] = decision

    def print(self):
        self.message_pool.print()

    def player_scores(self) -> Dict[str, float]:
        return {
            player: sum(round.player_scores(self.payouts)[player] for round in self.rounds)
            for player in self.player_names
        }

    def get_observation(self, player_name=None) -> List[Message]:
        """
        get observation for the player
        """
        if player_name is None:
            return self.message_pool.get_all_messages()
        else:
            return self.message_pool.get_visible_messages(player_name, turn=self._current_turn)

    def _moderator_speak(self, text: str, visible_to: Union[str, List[str]] = "all"):
        """
        moderator say something
        """
        message = Message(agent_name="Moderator", content=text, turn=self._current_turn, visible_to=visible_to)
        self.message_pool.append_message(message)

    def is_terminal(self) -> bool:
        """
        check if the conversation is over
        """
        return len(self.rounds) == self.total_rounds

    def decision_from_action(self, action: str) -> bool:
        """
        convert action to decision
        """
        action = self.parser(f'Did this player cooperate or defect?\n>{action}\nSay only "cooperate" or "defect".')
        return 'cooperate' in action.lower()

    def step(self, player_name: str, action: str) -> TimeStep:
        """
        step function that is called by the arena
        Args:
            player_name: the name of the player that takes the action
            action: the action that the agents wants to take
        """
        # If not initialized, reset the environment
        if not self._initialized:
            self.reset()

        assert player_name == self.get_next_player(), f"Wrong player! It is {self.get_next_player()} turn."
        message = Message(agent_name=player_name, content=action, turn=self._current_turn, visible_to="Moderator")
        self.message_pool.append_message(message)
        self._current_turn += 1
        self._next_player_idx += 1
        decision = self.decision_from_action(action)
        self.add_decision(player_name, decision)

        if self.current_round.is_complete:
            self.complete_round()

            if self.is_terminal():
                self._moderator_speak(f"{self.total_rounds} rounds of decisions have been completed.")
                self._moderator_speak(f"The scores are {self.player_scores()}")
                return TimeStep(observation=self.get_observation(), reward=self.player_scores(), terminal=True)
        
            self.new_round()
        
        return TimeStep(observation=self.get_observation(), reward=self.get_zero_rewards(), terminal=False)
