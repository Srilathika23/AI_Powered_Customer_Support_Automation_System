"""
Task 5: Specialized Department Agents
======================================
Four department agents + one memory recall agent. Each agent retrieves
context from the local RAG pipeline and conversation history, then builds
a response with rule-based templates. No API key, no LLM call required.

Agents:
  - Sales Agent
  - Technical Support Agent
  - Billing Agent         (also flags high-risk requests)
  - Account Agent
  - Memory Recall Agent   (no RAG, uses SQLite history only)
"""

import re
from src.state import CustomerSupportState
from src.rag import get_chunks, retrieve_context
from src.memory import format_history_for_prompt
from src.approval import needs_human_approval


def _extract_plan_block(context: str, plan_name: str) -> str:
    pattern = rf"{plan_name} PLAN.*?(?=\n\n|\Z)"
    match = re.search(pattern, context, re.DOTALL | re.IGNORECASE)
    return match.group(0).strip() if match else ""


def _build_response(department: str, persona: str, query: str, context: str,
                     customer_name: str = "Valued Customer") -> str:
    """
    NOTE: This response intentionally does NOT include conversation
    history. History is display-only (shown to the customer alongside
    this response) and must never be embedded into the text that gets
    persisted to memory, or each saved turn would contain the previous
    turn's history, re-embedding and growing without bound.
    """
    return f"""Hello {customer_name},

Thank you for contacting ABC Technologies {department}.

I understand your query: "{query}"

Based on our knowledge base, here is the information relevant to your request:

{context}

Please do not hesitate to reach out if you need further assistance.

Best regards,
{persona}
ABC Technologies {department}""".strip()


def sales_agent(state: CustomerSupportState) -> CustomerSupportState:
    print("[Sales Agent] Processing query...")
    chunks = get_chunks()
    context = retrieve_context(chunks, state["query"])
    history_text = format_history_for_prompt(state.get("conversation_history", []))

    response = _build_response(
        department="Sales",
        persona="Alex | Sales Specialist",
        query=state["query"],
        context=context,
        customer_name=state.get("customer_name") or "Valued Customer",
    )

    return {
        **state,
        "department": "Sales",
        "retrieved_context": context,
        "draft_response": response,
        "history_display": history_text,
        "requires_approval": False,
    }


def technical_agent(state: CustomerSupportState) -> CustomerSupportState:
    print("[Technical Agent] Processing query...")
    chunks = get_chunks()
    context = retrieve_context(chunks, state["query"])
    history_text = format_history_for_prompt(state.get("conversation_history", []))

    if any(kw in state["query"].lower() for kw in ["crash", "error", "upload", "not working"]):
        extra = retrieve_context(chunks, "file upload troubleshooting application error", k=2)
        extra_unique = "\n\n---\n\n".join(
            part for part in extra.split("\n\n---\n\n") if part not in context
        )
        if extra_unique:
            context = context + "\n\n--- Additional Troubleshooting ---\n" + extra_unique

    response = _build_response(
        department="Technical Support",
        persona="Sam | Technical Support Engineer",
        query=state["query"],
        context=context,
        customer_name=state.get("customer_name") or "Valued Customer",
    )

    return {
        **state,
        "department": "Technical Support",
        "retrieved_context": context,
        "draft_response": response,
        "history_display": history_text,
        "requires_approval": False,
    }


def billing_agent(state: CustomerSupportState) -> CustomerSupportState:
    print("[Billing Agent] Processing query...")
    chunks = get_chunks()
    context = retrieve_context(chunks, state["query"])
    history_text = format_history_for_prompt(state.get("conversation_history", []))

    requires_approval = needs_human_approval(state["query"])

    if requires_approval:
        print("[Billing Agent] HIGH-RISK request detected -> flagging for human approval.")
        response = (
            f"Hello {state.get('customer_name') or 'Valued Customer'},\n\n"
            "Thank you for contacting ABC Technologies Billing Support.\n\n"
            f"I have received your request regarding: \"{state['query']}\"\n\n"
            "This request requires review and approval from our billing supervisor "
            "before it can be processed. Your case has been escalated and you will "
            "receive a response within 24 business hours.\n\n"
            "Reference information from our policy:\n\n"
            f"{context}\n\n"
            "Best regards,\nJordan | Billing Support Specialist\nABC Technologies Billing"
        )
    else:
        response = _build_response(
            department="Billing",
            persona="Jordan | Billing Support Specialist",
            query=state["query"],
            context=context,
            customer_name=state.get("customer_name") or "Valued Customer",
        )

    return {
        **state,
        "department": "Billing",
        "retrieved_context": context,
        "draft_response": response,
        "history_display": history_text,
        "requires_approval": requires_approval,
        "approval_status": "pending" if requires_approval else None,
    }


def account_agent(state: CustomerSupportState) -> CustomerSupportState:
    print("[Account Agent] Processing query...")
    chunks = get_chunks()
    context = retrieve_context(chunks, state["query"])
    history_text = format_history_for_prompt(state.get("conversation_history", []))

    response = _build_response(
        department="Account Management",
        persona="Riley | Account Support Specialist",
        query=state["query"],
        context=context,
        customer_name=state.get("customer_name") or "Valued Customer",
    )

    return {
        **state,
        "department": "Account Management",
        "retrieved_context": context,
        "draft_response": response,
        "history_display": history_text,
        "requires_approval": False,
    }


def memory_recall_agent(state: CustomerSupportState) -> CustomerSupportState:
    """
    NOTE: Unlike the other agents, this response's whole purpose IS to show
    history, so history_text is embedded here intentionally. To avoid this
    turn's response (a full history dump) being re-saved and snowballing
    into FUTURE turns, the caller saves "memory_safe_response" (a short,
    generic summary) to the database instead of the full draft_response.
    """
    print("[Memory Recall Agent] Retrieving conversation history...")
    history = state.get("conversation_history", [])
    customer_name = state.get("customer_name") or "Valued Customer"

    if not history:
        response = (
            f"Hello {customer_name},\n\n"
            "I checked our records but could not find any previous interactions "
            "associated with your account. This may be your first contact with us, "
            "or your history may have been stored under a different customer ID.\n\n"
            "Please feel free to describe your current issue and I'll be happy to help!\n\n"
            "Best regards,\nABC Technologies Support Team"
        )
        memory_safe_response = response
        history_text = ""
    else:
        history_text = format_history_for_prompt(history)
        last_issues = [h for h in history if h["role"] == "customer"]
        last_issue_summary = last_issues[-1]["message"] if last_issues else "Not found"

        response = (
            f"Hello {customer_name},\n\n"
            "I've retrieved your previous support history from our records.\n\n"
            f"Your most recent support query was:\n\"{last_issue_summary}\"\n\n"
            f"Full conversation history:\n\n{history_text}\n\n"
            "Is there anything else I can help you with today?\n\n"
            "Best regards,\nABC Technologies Support Team"
        )

        memory_safe_response = (
            f"Hello {customer_name},\n\n"
            "I retrieved your previous support history and shared a summary "
            f"of your most recent query (\"{last_issue_summary}\") with you.\n\n"
            "Best regards,\nABC Technologies Support Team"
        )

    return {
        **state,
        "department": "Memory Recall",
        "draft_response": response,
        "memory_safe_response": memory_safe_response,
        "history_display": history_text,
        "requires_approval": False,
        "retrieved_context": "N/A - Memory recall query",
    }