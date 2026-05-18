"""Generate per-example Spider evaluation diagnostics.

This script keeps the standard Spider metrics, but writes one JSON object per
example so prompt changes can be analyzed by query type and failure mode.
"""

import argparse
import copy
import json
import os
from pathlib import Path

from eval.evaluation import (
    Evaluator,
    Schema,
    build_foreign_key_map_from_json,
    build_valid_col_units,
    eval_exec_match,
    get_schema,
    get_sql,
    rebuild_sql_col,
    rebuild_sql_val,
)


EMPTY_SQL = {
    "except": None,
    "from": {"conds": [], "table_units": []},
    "groupBy": [],
    "having": [],
    "intersect": None,
    "limit": None,
    "orderBy": [],
    "select": [False, []],
    "union": None,
    "where": [],
}


def _load_gold(path: Path) -> list[tuple[str, str]]:
    return [
        tuple(line.strip().split("\t"))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _load_predictions(path: Path) -> list[str]:
    return [
        line.strip().split("\t")[0]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _load_examples(path: Path | None) -> list[dict] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _partial_summary(partial_scores: dict) -> dict:
    return {
        metric_name: {
            "acc": metric_values["acc"],
            "rec": metric_values["rec"],
            "f1": metric_values["f1"],
            "pred_total": metric_values["pred_total"],
            "label_total": metric_values["label_total"],
        }
        for metric_name, metric_values in partial_scores.items()
    }


def build_report(
    gold_path: Path,
    pred_path: Path,
    db_dir: Path,
    table_path: Path,
    output_path: Path,
    dataset_json_path: Path | None,
) -> None:
    gold = _load_gold(gold_path)
    predictions = _load_predictions(pred_path)
    examples = _load_examples(dataset_json_path)

    if len(gold) != len(predictions):
        raise ValueError(
            f"Gold and prediction lengths differ: {len(gold)} != {len(predictions)}"
        )
    if examples is not None and len(examples) != len(gold):
        raise ValueError(
            f"Dataset JSON and gold lengths differ: {len(examples)} != {len(gold)}"
        )

    evaluator = Evaluator()
    kmaps = build_foreign_key_map_from_json(str(table_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as report_file:
        for idx, (pred_sql_text, (gold_sql_text, db_id)) in enumerate(
            zip(predictions, gold)
        ):
            db_path = os.path.join(str(db_dir), db_id, db_id + ".sqlite")
            schema = Schema(get_schema(db_path))

            gold_sql = get_sql(schema, gold_sql_text)
            hardness = evaluator.eval_hardness(gold_sql)

            parse_error = ""
            try:
                pred_sql = get_sql(schema, pred_sql_text)
            except Exception as exc:
                pred_sql = copy.deepcopy(EMPTY_SQL)
                parse_error = str(exc)

            kmap = kmaps[db_id]
            gold_valid_col_units = build_valid_col_units(
                gold_sql["from"]["table_units"], schema
            )
            pred_valid_col_units = build_valid_col_units(
                pred_sql["from"]["table_units"], schema
            )

            gold_sql = rebuild_sql_val(gold_sql)
            gold_sql = rebuild_sql_col(gold_valid_col_units, gold_sql, kmap)
            pred_sql = rebuild_sql_val(pred_sql)
            pred_sql = rebuild_sql_col(pred_valid_col_units, pred_sql, kmap)

            exec_score = eval_exec_match(
                db_path, pred_sql_text, gold_sql_text, pred_sql, gold_sql
            )
            exact_score = evaluator.eval_exact_match(pred_sql, gold_sql)
            partial_scores = _partial_summary(evaluator.partial_scores)

            example = examples[idx] if examples is not None else {}
            report_file.write(
                json.dumps(
                    {
                        "index": idx,
                        "source_index": example.get("source_index"),
                        "db_id": db_id,
                        "hardness": hardness,
                        "question": example.get("question"),
                        "gold_sql": gold_sql_text,
                        "pred_sql": pred_sql_text,
                        "execution": exec_score,
                        "exact": exact_score,
                        "partial": partial_scores,
                        "parse_error": parse_error,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--pred", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dataset-json", type=Path)
    args = parser.parse_args()

    build_report(
        gold_path=args.gold,
        pred_path=args.pred,
        db_dir=args.db,
        table_path=args.table,
        output_path=args.output,
        dataset_json_path=args.dataset_json,
    )


if __name__ == "__main__":
    main()
