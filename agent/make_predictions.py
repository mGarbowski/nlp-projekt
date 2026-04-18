import argparse

import json
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint
from typing import Self

from loguru import logger

from .agent import get_model, setup_db, build_agent_graph, run_agent
from .logging_config import configure_logging


@dataclass(frozen=True)
class Config:
    dataset_json: Path
    databases_dir: Path
    predictions_file: Path

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> Self:
        return cls(
            dataset_json=args.dataset_json,
            databases_dir=args.databases_dir,
            predictions_file=args.predictions_file,
        )


def make_predictions_for_database(
    model, database_id, examples: list[dict], config: Config
) -> list[str]:
    logger.info(
        f"Making predictions for {len(examples)} examples from db {database_id}"
    )
    db_path = config.databases_dir / database_id / f"{database_id}.sqlite"
    db = setup_db(str(db_path))
    agent = build_agent_graph(model, db, only_query=True)
    predictions = []
    for example in examples:
        question = example["question"]
        final_state = run_agent(agent, question)
        predictions.append(final_state["generated_query"])
        break

    return predictions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset-json", type=Path, default="data/spider_data/test.json"
    )
    parser.add_argument(
        "--databases-dir", type=Path, default="data/spider_data/test_database"
    )
    parser.add_argument(
        "--predictions-file", type=Path, default="results/predictions.txt"
    )

    config = Config.from_args(parser.parse_args())
    configure_logging()

    logger.info(f"Config: {config}")

    dataset_file: Path = config.dataset_json
    examples = json.loads(dataset_file.read_text())
    pprint(examples[:3])
    print(len(examples))
    examples_by_db = {}
    for example in examples:
        db_id = example["db_id"]
        if db_id not in examples_by_db:
            examples_by_db[db_id] = [example]
        else:
            examples_by_db[db_id].append(example)

    print(len(examples_by_db))
    for db_id, examples in examples_by_db.items():
        print(db_id, len(examples))

    model = get_model()
    all_predictions = []
    for db_id, examples in examples_by_db.items():
        predictions = make_predictions_for_database(model, db_id, examples, config)
        all_predictions.extend(predictions)
        break

    config.predictions_file.parent.mkdir(parents=True, exist_ok=True)
    config.predictions_file.write_text("\n".join(all_predictions))


if __name__ == "__main__":
    main()
