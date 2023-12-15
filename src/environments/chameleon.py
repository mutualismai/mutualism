from chatarena.environments import Chameleon, register_env

from .base import Parser


@register_env
class ImprovedModerationChameleon(Chameleon):
    type_name = "chameleon"

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parser = Parser()


    def _text2vote(self, text) -> str:
        """Convert text to vote, return a player's name."""
        # lower = text.lower().replace("[", "").replace("]", "").replace(".", "")
        text = self.parser(f'Who did the speaker think the chameleon was? Or who did they vote for as the chameleon?\n{text}\nJust return the name of the player.')
        
        text = text.lower()
        for name in self.player_names:
            candidates = [
                name.lower(),
                name.lower().replace(" ", ""),
                name.lower().replace(" ", "_"),
            ]
            if any([candidate in text for candidate in candidates]):
                return name
        return ""

    def _is_true_code(self, text) -> bool:
        """Check whether the text is the true code."""
        # Get the word enclosed by quote marks with regex
        code: str = self.code # type: ignore
        text = self.parser(f'Did the speaker guess the word {code} correctly? Here is what they guessed:\n{text}\nJust answer "correct" or "incorrect".')
        return 'correct' in text.lower() and 'incorrect' not in text.lower()

