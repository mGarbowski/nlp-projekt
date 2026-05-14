from langchain_community.utilities import SQLDatabase
from langchain_core.language_models import BaseChatModel


def build_plan_and_solve_agent(model: BaseChatModel, db: SQLDatabase, only_query: bool):
    pass
