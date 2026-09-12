import operator
from typing import Annotated, TypedDict

from langchain_groq import ChatGroq

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver


# =========================
# LLM
# =========================

llm = ChatGroq(
    model="openai/gpt-oss-20b"
)


# =========================
# STATE
# =========================

class MailState(TypedDict):
    topic: str
    generated_mail: Annotated[list[str], operator.add]
    decision: str


# =========================
# WRITE MAIL
# =========================

def write_mail(state: MailState):

    topic = state["topic"]

    prompt = f'''
    You are an AI email writing assistant.

    Write a professional and well-structured email based on the user's topic.

    User's topic:
    {topic}

    Requirements:
    - Understand the purpose of the email from the topic.
    - Use a professional and polite tone.
    - Include an appropriate subject line.
    - Keep the email concise and natural.
    - Do not add unnecessary information.
    - Return only the complete email.
    '''

    generated_mail = llm.invoke(prompt).content

    print("\n========== GENERATED EMAIL ==========")
    print(generated_mail)
    print("=====================================")

    return {
        "generated_mail": [generated_mail]
    }


# =========================
# HUMAN REVIEW
# =========================

def human_review(state: MailState):

    decision = interrupt(
        "Do you approve this email? Type approve or reject."
    )

    return {
        "decision": decision
    }


# =========================
# ROUTING
# =========================

def route_after_review(state: MailState):

    if state["decision"].lower() == "approve":
        return "approved"

    return "rejected"


# =========================
# GRAPH
# =========================

graph = StateGraph(MailState)

graph.add_node("write_mail", write_mail)
graph.add_node("human_review", human_review)

graph.add_edge(START, "write_mail")
graph.add_edge("write_mail", "human_review")

graph.add_conditional_edges(
    "human_review",
    route_after_review,
    {
        "approved": END,
        "rejected": "write_mail"
    }
)


# =========================
# CHECKPOINTER
# =========================

checkpointer = MemorySaver()

workflow = graph.compile(
    checkpointer=checkpointer
)


# =========================
# USER INPUT
# =========================

topic = input("Enter your email topic: ")


config = {
    "configurable": {
        "thread_id": "mail_1"
    }
}


# =========================
# FIRST RUN
# =========================

workflow.invoke(
    {
        "topic": topic,
        "generated_mail": [],
        "decision": ""
    },
    config=config
)


# =========================
# HITL LOOP
# =========================

while True:

    decision = input("\nApprove or Reject: ").strip().lower()

    if decision not in ["approve", "reject"]:

        print("Please type only 'approve' or 'reject'.")
        continue

    result = workflow.invoke(
        Command(resume=decision),
        config=config
    )

    # APPROVED
    if decision == "approve":

        final_mail = result["generated_mail"][-1]

        print("\n========== FINAL EMAIL ==========")
        print(final_mail)
        print("=================================")

        break

    # REJECTED
    else:

        print("\nRejected.")
        print("Generating a new email...")