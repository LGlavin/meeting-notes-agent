from typing import Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
from tools import all_tools
from config import LLM_MODEL, MAX_ITERATIONS

SYSTEM_PROMPT = """You are a meeting notes agent that processes meeting transcripts.

When given a transcript, you must:
1. First, check if there are past meeting notes for any attendees mentioned (use get_past_meeting_notes)
2. Save the notes to Airtable (use save_meeting_notes)
3. AFTER saving, you MUST display the full structured notes in your final response using this exact format:

## Summary
(2-3 sentence summary)

## Action Items
- **[Owner]**: task description (deadline if mentioned)

## Decisions
- decision 1
- decision 2

## Follow Ups for Next Meeting
- follow up item 1
- follow up item 2

## Previous Follow-Up Status
(If past meetings were found, list which previous follow-ups were addressed and which are still open. If no past meetings, write "No previous meetings found.")

Rules:
- Be concise and specific
- Always attribute action items to a person
- If you can't identify speakers by name, use Speaker 1, Speaker 2, etc.
- Always check for past meetings before generating notes
- Always save to Airtable after generating notes
- ALWAYS end with the full formatted notes above. Never just say "saved successfully"."""


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def call_model(state: AgentState) -> AgentState:
    llm = ChatOpenAI(model=LLM_MODEL, temperature=0).bind_tools(all_tools)
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def build_agent(transcript: str, meeting_date: str):
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(all_tools))
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")

    graph = workflow.compile()

    initial_messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Meeting date: {meeting_date}\n\n"
            f"Transcript:\n{transcript}"
        )),
    ]

    return graph, initial_messages
