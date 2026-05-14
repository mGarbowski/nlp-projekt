"""Simple agent demo."""

import argparse

from langchain_community.utilities import SQLDatabase
from langchain_core.language_models import BaseChatModel
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from loguru import logger

from agent.chain_of_thought.agent import ChainOfThoughtAgent
from agent.common.agent import BaseAgent
from agent.common.logging_config import configure_logging
from agent.common.modes import ReasoningMode
from agent.plan_and_solve.agent import PlanAndSolveAgent


def get_model() -> BaseChatModel:
    logger.info("Loading model")
    llm = HuggingFacePipeline.from_model_id(
        model_id="Qwen/Qwen2.5-1.5B-Instruct",
        task="text-generation",
        pipeline_kwargs={"max_new_tokens": 1024, "temperature": 0.3},
    )
    return ChatHuggingFace(llm=llm)


def setup_db(db_path: str = "data/Chinook.db") -> SQLDatabase:
    logger.info(f"Initializing database resources for {db_path}")
    return SQLDatabase.from_uri(f"sqlite:///{db_path}")


def make_agent(
    mode: ReasoningMode, model: BaseChatModel, db: SQLDatabase, only_query: bool
) -> BaseAgent:
    match mode:
        case ReasoningMode.PLAN_AND_SOLVE:
            return PlanAndSolveAgent(model, db, only_query)
        case ReasoningMode.CHAIN_OF_THOUGHT:
            return ChainOfThoughtAgent(model, db, only_query)
        case _:
            raise NotImplementedError("Variant not yet implemented")


def run_agent(
    agent: BaseAgent,
    user_question: str,
):
    logger.info("Starting agent run")
    logger.info(f"User question: {user_question}")

    final_state = agent.run(user_question)

    logger.info("Final query: {}", final_state["generated_query"])
    if final_state["final_answer"]:
        logger.info("Final answer: {}", final_state["final_answer"])
    if final_state["execution_error"]:
        logger.warning("Final execution error: {}", final_state["execution_error"])

    return final_state


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reasoning-mode",
        type=str,
        choices=["none", "cot", "plan_and_solve", "react"],
        default="none",
    )
    args = parser.parse_args()

    reasoning_mode = ReasoningMode.from_string(args.reasoning_mode)
    configure_logging()
    model = get_model()
    db = setup_db()
    agent = make_agent(reasoning_mode, model, db, only_query=False)

    question = "Which genre on average has the longest tracks?"
    _ = run_agent(agent, question)

    logger.info("Agent completed successfully")


if __name__ == "__main__":
    main()
