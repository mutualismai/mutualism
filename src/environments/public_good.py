from typing import Dict, List

from chatarena.environments import register_env

from .base import Parser, SimpleRoundEnvironment


def calculate_contributions(player_actions: Dict[str, str]) -> Dict[str, float]:
    parser = Parser()
    contributions = {}
    for player, action in player_actions.items():
        action = parser(f'How many points did this player contribute?\n>{action}\nSay only a number.')
        contributions[player] = float(action)
    return contributions

def updated_scores(scores: Dict[str, float], contributions: Dict[str, float], interest_multiplier: float) -> Dict[str, float]:
    total_contributions = sum(contributions.values())
    payback = total_contributions * interest_multiplier / len(scores)
    for player in scores.keys():
        scores[player] = scores[player] - contributions[player] + payback
    return scores


@register_env
class PublicGood(SimpleRoundEnvironment):
    type_name = "public_good"

    def __init__(self, player_names: List[str], interest_multiplier: float, **kwargs):
        self.interest_multiplier = interest_multiplier
        self.starting_points = 100.0
        self._player_scores = {player_name: self.starting_points for player_name in player_names}
        super().__init__(player_names=player_names, **kwargs)

    def begin_game(self):
        self._moderator_speak(f"Each player has {self.starting_points} points at the beginning.")

    def begin_round(self) -> None:
        """
        start a new round
        """
        if len(self.rounds) == 1:
            self._moderator_speak(f"This the first round. Now everyone give your decision.")
        else:
            self._moderator_speak(f"You can look at others' decisions for previous rounds, and think about your decision for the current round.")

    def complete_round(self) -> None:
        self._moderator_speak(f"Round {len(self.rounds)} is over.")
        self._moderator_speak("\n".join(
            [
                f"{player} said: {action}"
                for player, action in self.current_round.player_actions.items()
            ]
        ))
        contributions = calculate_contributions(self.current_round.player_actions)
        self._player_scores = updated_scores(self._player_scores, contributions, self.interest_multiplier)
        self._moderator_speak(f"Current scores: {self._player_scores}")

    def player_scores(self) -> Dict[str, float]:
        return self._player_scores
