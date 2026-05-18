# Strategy comparison on `diagnostic_test_40`

The following results were computed on the `diagnostic_test_40` sample from the
Spider dataset. Three SQL generation strategies were compared: Chain-of-Thought,
ReAct-lite, and Plan-and-Solve. The experiments were run with the local
`Qwen2.5-1.5B-Instruct` model and the stronger `groq-qwen3-32b` model.

## Main metrics

| Model | Strategy | Execution Accuracy | Exact Match |
|---|---:|---:|---:|
| `Qwen2.5-1.5B-Instruct` | CoT | 25.0% | 12.5% |
| `Qwen2.5-1.5B-Instruct` | ReAct-lite | 25.0% | 17.5% |
| `Qwen2.5-1.5B-Instruct` | Plan-and-Solve | 20.0% | 7.5% |
| `groq-qwen3-32b` | CoT | 55.0% | 47.5% |
| `groq-qwen3-32b` | ReAct-lite | 60.0% | 47.5% |
| `groq-qwen3-32b` | Plan-and-Solve | 47.5% | 27.5% |

## Partial Matching F1

| Model | Strategy | Select | Where | Group | Order | Keywords |
|---|---|---:|---:|---:|---:|---:|
| `Qwen2.5-1.5B-Instruct` | CoT | 38.1% | 43.8% | 27.6% | 21.1% | 41.4% |
| `Qwen2.5-1.5B-Instruct` | ReAct-lite | 46.9% | 46.2% | 34.3% | 43.5% | 57.6% |
| `Qwen2.5-1.5B-Instruct` | Plan-and-Solve | 34.9% | 37.0% | 40.0% | 38.1% | 48.3% |
| `groq-qwen3-32b` | CoT | 83.8% | 81.2% | 66.7% | 69.6% | 76.5% |
| `groq-qwen3-32b` | ReAct-lite | 78.9% | 76.5% | 65.0% | 75.0% | 81.7% |
| `groq-qwen3-32b` | Plan-and-Solve | 74.3% | 66.7% | 73.2% | 80.0% | 73.8% |

## Conclusions

Switching from the local `Qwen2.5-1.5B-Instruct` model to `groq-qwen3-32b`
significantly improved the results for all strategies. For CoT, execution
accuracy increased from 25.0% to 55.0%, while exact match increased from 12.5%
to 47.5%.

The highest execution accuracy was achieved by ReAct-lite with the
`groq-qwen3-32b` model, reaching 60.0%. CoT and ReAct-lite achieved the same
exact match score with the stronger model, 47.5%. Plan-and-Solve obtained lower
exact match scores for both model variants, especially with the local model.

The results suggest that ReAct-lite is comparable to CoT, and with a stronger
model it may achieve better execution accuracy. At the same time, the weaker
local model has a limited ability to benefit from additional reasoning and
correction steps, which is reflected in the substantially lower scores across
all strategies.
