from enum import Enum


class ReasoningMode(Enum):
    CHAIN_OF_THOUGHT = "cot"
    PLAN_AND_SOLVE = "plan_and_solve"
    REACT_LITE = "react_lite"
    REACT = "react"
    BASE = "none"

    @classmethod
    def from_string(cls, string: str):
        match string:
            case "cot":
                return cls.CHAIN_OF_THOUGHT
            case "plan_and_solve":
                return cls.PLAN_AND_SOLVE
            case "react_lite":
                return cls.REACT_LITE
            case "react":
                return cls.REACT
            case "none":
                return cls.BASE
            case _:
                raise ValueError(f"Unknown reasoning mode: {string}")
