import logging

from chatarena.arena import Arena
from chatarena.backends.openai import OpenAIChat
from src.agents.react import ReActWrapper

logging.basicConfig(level=logging.INFO)

def log_react_agent_reasoning(arena: Arena) -> None:
    message_pool = arena.environment.message_pool
    for player in arena.players:
        if isinstance(player.backend, ReActWrapper):
            player.backend.message_pool = message_pool


def upgrade_to_gpt4(arena: Arena) -> None:
    for player in arena.players:
        backend = player.backend
        if isinstance(backend, ReActWrapper):
            backend = backend._backend
        if isinstance(backend, OpenAIChat):
            backend.model = 'gpt-4-1106-preview'

if __name__ == '__main__':
    arena = Arena.from_config('prisoner.json')
    log_react_agent_reasoning(arena)
    upgrade_to_gpt4(arena)
    arena.run(num_steps=50)
    arena.save_history('history.json')