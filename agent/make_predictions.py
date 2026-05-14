"""Use the agent to make predictions on the Spider dataset.

Save the predicted SQL queries to a file for later evaluation.
"""

import argparse

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from langchain_core.language_models import BaseChatModel
from loguru import logger
from tqdm import tqdm

from agent.agent import setup_db, make_agent, get_model
from agent.common.logging_config import configure_logging
from agent.common.modes import ReasoningMode


@dataclass(frozen=True)
class Config:
    dataset_json: Path
    databases_dir: Path
    predictions_file: Path
    """Make predictions on a small subset of the database"""
    short: bool
    short_n: int = 5

    max_correction_attempts: int = 2
    reasoning_mode: ReasoningMode = ReasoningMode.BASE

    def __post_init__(self):
        assert self.dataset_json.exists()
        assert self.databases_dir.exists()

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> Self:
        return cls(
            dataset_json=args.dataset_json,
            databases_dir=args.databases_dir,
            predictions_file=args.predictions_file,
            short=args.short,
            max_correction_attempts=args.max_correction_attempts,
            reasoning_mode=ReasoningMode.from_string(args.reasoning_mode),
        )


def sanitize_query(query: str) -> str:
    return query.replace("\n", " ").strip()


def make_predictions_for_database(
    model: BaseChatModel, database_id: str, examples: list[dict], config: Config
) -> list[str]:
    logger.info(
        f"Making predictions for {len(examples)} examples from db {database_id}"
    )
    db_path = config.databases_dir / database_id / f"{database_id}.sqlite"
    db = setup_db(str(db_path))
    agent = make_agent(config.reasoning_mode, model, db, only_query=True)
    predictions = []
    for example in tqdm(examples, desc=f"Examples from {database_id}"):
        question = example["question"]
        final_state = agent.run(question)
        generated_query = sanitize_query(final_state["generated_query"])
        predictions.append(generated_query)

        with config.predictions_file.open("a", encoding="utf-8") as f:
            f.write(generated_query + "\n")

    return predictions


def load_examples(config: Config) -> list[dict]:
    dataset_file: Path = config.dataset_json
    examples = json.loads(dataset_file.read_text())

    if config.short:
        examples = examples[: config.short_n]

    return examples


def group_examples_by_db(examples: list[dict]) -> dict[str, list[dict]]:
    """Examples from the same db grouped together.

    To avoid unnecessary agent initialization for each database.
    """
    examples_by_db = {}
    for example in examples:
        db_id = example["db_id"]
        if db_id not in examples_by_db:
            examples_by_db[db_id] = [example]
        else:
            examples_by_db[db_id].append(example)

    return examples_by_db


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset-json", type=Path, default="data/spider_data/dev.json"
    )
    parser.add_argument(
        "--databases-dir", type=Path, default="data/spider_data/test_database"
    )
    parser.add_argument(
        "--predictions-file", type=Path, default="results/predictions.txt"
    )
    parser.add_argument(
        "--short",
        action="store_true",
        help="Make predictions on a subset of the database",
    )
    parser.add_argument(
        "--max-correction-attempts",
        type=int,
        default=2,
        help="Maximum number of self-correction retries after validation or execution failure.",
    )

    parser.add_argument(
        "--reasoning-mode",
        type=str,
        choices=["none", "cot", "plan_and_solve", "react"],
        default="none",
        help="Strategy for the agent reasoning.",
    )

    config = Config.from_args(parser.parse_args())
    configure_logging()
    logger.info(f"Config: {config}")

    examples = load_examples(config)
    logger.info(f"Examples to process: {len(examples)}")

    examples_by_db = group_examples_by_db(examples)
    logger.info(f"Number of databases: {len(examples_by_db)}")
    logger.info(
        f"Number of examples per database: {[(db_id, len(examples)) for db_id, examples in examples_by_db.items()]}"
    )

    model = get_model()
    config.predictions_file.parent.mkdir(parents=True, exist_ok=True)
    config.predictions_file.write_text("", encoding="utf-8")

    for db_id, examples in tqdm(examples_by_db.items(), desc="Databases"):
        _ = make_predictions_for_database(model, db_id, examples, config)


if __name__ == "__main__":
    main()
