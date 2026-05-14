from abc import ABC, abstractmethod

from langchain_community.utilities import SQLDatabase
from langchain_core.language_models import BaseChatModel

from agent.common.state import BaseAgentState


class BaseAgent(ABC):
    @abstractmethod
    def build_graph(self, model: BaseChatModel, db: SQLDatabase, only_query: bool): ...

    @abstractmethod
    def get_initial_state(
        self, user_question: str, max_correction_attempts: int = 2
    ) -> BaseAgentState: ...

    @abstractmethod
    def run(self, user_question: str) -> BaseAgentState: ...
