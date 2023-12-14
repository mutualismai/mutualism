from typing import List, Optional

from chatarena.backends import (IntelligenceBackend, load_backend,
                                register_backend)
from chatarena.config import BackendConfig
from chatarena.message import SYSTEM_NAME, Message

REASONING_PROMPT = "Before reponding to the previous message, first think step-by-step about your response. Give only your reasoning, not the response itself."


@register_backend
class ReActWrapper(IntelligenceBackend):
    type_name = 'react'
    stateful = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # registers the arguments with Configurable
        backend_kwargs = kwargs.get('backend', {})
        backend_config = BackendConfig(**backend_kwargs)
        self._backend = load_backend(backend_config)
        self.message_pool = None

    def get_reasoning(self, query_method, history_messages, request_msg, **kwargs):
        """Returns the reasoning of a query method."""
        reasoning_history = history_messages + [request_msg] if request_msg else history_messages
        reasoning_request_msg = Message(SYSTEM_NAME, REASONING_PROMPT, history_messages[-1].turn)
        return query_method(history_messages=reasoning_history, request_msg=reasoning_request_msg, **kwargs)


    def get_action(self, query_method, history_messages, request_msg, agent_name, **kwargs):
        """Returns the response of a query method."""
        reasoning = self.get_reasoning(query_method, history_messages=history_messages, request_msg=request_msg, agent_name=agent_name, **kwargs)
        reasoning = f'Thinking to myself: {reasoning} Next, when asked, I will give my response.'
        reasoning_message = Message(agent_name, reasoning, history_messages[-1].turn, logged=True, visible_to=[])
        if self.message_pool:
            self.message_pool.append_message(reasoning_message)
        if not request_msg:
            request_msg = Message(SYSTEM_NAME, f"Now you speak, {agent_name}.", history_messages[-1].turn)
        return query_method(history_messages=history_messages + [reasoning_message], request_msg=request_msg, agent_name=agent_name, **kwargs)


    def query(
        self,
        agent_name: str,
        role_desc: str,
        history_messages: List[Message],
        global_prompt: Optional[str] = None,
        request_msg: Optional[Message] = None,
        *args,
        **kwargs,
    ) -> str:
        return self.get_action(self._backend.query, agent_name=agent_name, role_desc=role_desc, history_messages=history_messages, global_prompt=global_prompt, request_msg=request_msg, *args, **kwargs)

    async def async_query(
        self,
        agent_name: str,
        role_desc: str,
        history_messages: List[Message],
        global_prompt: Optional[str] = None,
        request_msg: Optional[Message] = None,
        *args,
        **kwargs,
    ) -> str:
        return self.get_action(self._backend.async_query, agent_name=agent_name, role_desc=role_desc, history_messages=history_messages, global_prompt=global_prompt, request_msg=request_msg, *args, **kwargs)
