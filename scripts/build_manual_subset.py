"""Build a small Spider subset from manually selected source indexes."""

import argparse
import json
from pathlib import Path


def read_indices(path: Path) -> list[int]:
    indices = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        clean = line.split("#", 1)[0].strip()
        if not clean:
            continue
        try:
            indices.append(int(clean))
        except ValueError as exc:
            raise ValueError(f"Invalid index at {path}:{line_no}: {line!r}") from exc
    return indices


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-json",
        type=Path,
        default=Path("data/spider_data/test.json"),
    )
    parser.add_argument(
        "--source-gold",
        type=Path,
        default=Path("data/spider_data/test_gold.sql"),
    )
    parser.add_argument(
        "--indices",
        type=Path,
        default=Path("data/spider_data/manual_test_indices.txt"),
    )
    parser.add_argument(
        "--output-prefix",
        type=Path,
        default=Path("data/spider_data/manual_test"),
    )
    args = parser.parse_args()

    examples = json.loads(args.source_json.read_text(encoding="utf-8"))
    gold_lines = [
        line
        for line in args.source_gold.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(examples) != len(gold_lines):
        raise ValueError(
            f"Source JSON and gold length differ: {len(examples)} != {len(gold_lines)}"
        )

    indices = read_indices(args.indices)
    if not indices:
        raise ValueError(f"No indexes selected in {args.indices}")

    seen = set()
    selected_examples = []
    selected_gold = []
    metadata_examples = []
    for idx in indices:
        if idx in seen:
            raise ValueError(f"Duplicate index selected: {idx}")
        if idx < 0 or idx >= len(examples):
            raise IndexError(
                f"Index out of range: {idx}; valid range 0..{len(examples) - 1}"
            )
        seen.add(idx)

        example = dict(examples[idx])
        gold_sql, gold_db_id = gold_lines[idx].split("\t")
        if example["db_id"] != gold_db_id or example["query"] != gold_sql:
            raise ValueError(f"Gold alignment mismatch at source index {idx}")

        selected_examples.append(example)
        selected_gold.append(gold_lines[idx])
        metadata_examples.append(
            {
                "source_index": idx,
                "db_id": example["db_id"],
                "question": example["question"],
                "query": example["query"],
            }
        )

    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    args.output_prefix.with_suffix(".json").write_text(
        json.dumps(selected_examples, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.output_prefix.parent.joinpath(
        args.output_prefix.name + "_gold.sql"
    ).write_text(
        "\n".join(selected_gold) + "\n",
        encoding="utf-8",
    )
    args.output_prefix.parent.joinpath(
        args.output_prefix.name + "_metadata.json"
    ).write_text(
        json.dumps(
            {
                "source_json": str(args.source_json),
                "source_gold": str(args.source_gold),
                "indices_file": str(args.indices),
                "count": len(indices),
                "examples": metadata_examples,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {len(indices)} examples:")
    print(f"- {args.output_prefix}.json")
    print(f"- {args.output_prefix}_gold.sql")
    print(f"- {args.output_prefix}_metadata.json")


if __name__ == "__main__":
    main()
