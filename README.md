# Human-in-the-Loop (HITL) Email Assistant

A small learning project built with **LangGraph** to understand how **Human-in-the-Loop (HITL)** workflows work in AI agent systems.

## 📌 What This Project Does

This project builds an AI agent that:

1. Takes a topic from the user.
2. Uses an LLM (`ChatGroq` with `openai/gpt-oss-20b`) to draft a professional email based on that topic.
3. **Pauses execution** and asks a human to review the generated email.
4. If the human **approves**, the workflow ends and the final email is printed.
5. If the human **rejects**, the workflow loops back and regenerates the email — repeating until it's approved.

This is a classic example of a **Human-in-the-Loop** pattern: instead of letting the AI act fully autonomously, a person stays in control at a key decision point.

## 🧠 Key Concepts Learned

- **`interrupt()`** — pauses graph execution at a specific node and waits for external (human) input before continuing.
- **`Command(resume=...)`** — used to resume a paused graph with the human's decision.
- **Checkpointing (`MemorySaver`)** — persists the graph's state across the pause, so execution can resume exactly where it left off.
- **Conditional edges** — routes the graph to different nodes (`approved` → END, `rejected` → back to `write_mail`) based on the human's decision.
- **State management with `TypedDict`** — using `Annotated[list[str], operator.add]` to accumulate generated email drafts across loop iterations.

## 🗂️ How the Graph Works

```
START → write_mail → human_review → (approved) → END
                          ↑                ↓
                          └──── (rejected) ┘
```

- **`write_mail`**: Calls the LLM to generate an email based on the topic.
- **`human_review`**: Interrupts the graph and waits for the user to type `approve` or `reject`.
- **`route_after_review`**: Reads the decision and routes accordingly.

## ⚙️ Setup

1. Install dependencies:
   ```bash
   pip install langchain-groq langgraph
   ```

2. Set your Groq API key as an environment variable:
   ```bash
   export GROQ_API_KEY="your-api-key-here"
   ```

3. Run the script:
   ```bash
   python Human_In_The_Loop.py
   ```

## ▶️ Example Run

```
Enter your email topic: Requesting leave for a family event

========== GENERATED EMAIL ==========
Subject: Leave Request for Family Event
...
=====================================

Approve or Reject: reject

Rejected.
Generating a new email...

========== GENERATED EMAIL ==========
...
=====================================

Approve or Reject: approve

========== FINAL EMAIL ==========
...
=================================
```

## 🚀 Why This Matters

Human-in-the-Loop is an important pattern for building **trustworthy AI systems**, especially for tasks with real-world consequences (emails, transactions, approvals, etc.). Instead of fully trusting an LLM's output, HITL lets a human validate or reject AI-generated content before it's finalized — combining automation with accountability.

## 🛠️ Tech Stack

- [LangGraph](https://langchain-ai.github.io/langgraph/) — for building the stateful, interruptible graph
- [LangChain Groq](https://python.langchain.com/docs/integrations/chat/groq/) — for LLM inference
- Python's `TypedDict` and `operator` — for state schema and reducers

---

*This is a learning project built to explore Human-in-the-Loop workflows in agentic AI systems.*
