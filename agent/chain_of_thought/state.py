from agent.common.state import BaseAgentState


class ChainOfThoughtAgentState(BaseAgentState):
    reasoning_trace: str
