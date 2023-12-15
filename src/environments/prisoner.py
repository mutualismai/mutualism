from collections import defaultdict
from typing import Dict, List

from chatarena.environments import register_env

from .parser import Parser
from .simple_round_game import Round, SimpleRoundEnvironment


def players_cooperated(round: Round) -> Dict[str, bool]:
    parser = Parser()
    cooperated = {}
    for player, action in round.player_actions.items():
        action = parser(f'Did this player cooperate or defect?\n>{action}\nSay only "cooperate" or "defect".')
        cooperated[player] = 'cooperate' in action.lower()
    return cooperated


def player_scores(round: Round, payouts: Dict[str, Dict[str, int]]) -> Dict[str, float]:
    assert round.is_complete
    scores = {}
    players_cooperated_in_round = players_cooperated(round)
    cooperated_count = sum(1 for cooperated in players_cooperated_in_round.values() if cooperated)

    for player, cooperated in players_cooperated_in_round.items():
        if cooperated:
            other_cooperated = cooperated_count - 1
            score = payouts['cooperate'][f'{other_cooperated}_others_cooperate']
        else:
            other_cooperated = cooperated_count
            score = payouts['defect'][f'{other_cooperated}_others_cooperate']
        scores[player] = score
    return scores


@register_env
class PrisonersDilemma(SimpleRoundEnvironment):
    type_name = "prisoner"

    def __init__(self, player_names: List[str], payouts: Dict[str, Dict[str, int]], **kwargs):
        self.payouts = payouts
        super().__init__(player_names=player_names, **kwargs)

    def begin_game(self):
        self._moderator_speak(f"The payout matrix is as follows: {self.payouts}")

    def begin_round(self) -> None:
        """
        start a new round
        """
        if len(self.rounds) == 0:
            self._moderator_speak(f"This the first round. Now everyone give your decision.")
        else:
            self._moderator_speak(f"You can look around others' decisions and think your decision for next round. Now let us move to next round")

    def complete_round(self) -> None:
        self._moderator_speak(f"Round {len(self.rounds)} is over.")
        self._moderator_speak("\n".join(
            [
                f"{player} said: {action}"
                for player, action in self.current_round.player_actions.items()
            ]
        ))

    def player_scores(self) -> Dict[str, float]:
        total_scores = defaultdict(float)
        for round in self.rounds:
            scores = player_scores(round, self.payouts)
            for player, score in scores.items():
                total_scores[player] += score
        return total_scores