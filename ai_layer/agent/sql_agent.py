"""SQL agent that translates natural language questions into SQL queries
against the FinClose AI marts layer, executes them, and returns answers.

Uses LangChain's create_sql_agent with OpenAI as the LLM, customized with
an FP&A-aware system prompt to ensure accounting-correct interpretations.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage

from ai_layer.agent.connection import get_database
from ai_layer.agent.prompts import FPA_SYSTEM_PROMPT

# Load .env from project root
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def build_agent(verbose: bool = True):
    """Build and return a SQL agent configured for the FinClose AI marts.

    The agent is customized with an FP&A-aware system prompt so it
    interprets accounting data correctly.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not found in environment. "
            "Check your .env file."
        )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=api_key,
    )

    db = get_database()
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=verbose,
        agent_type="tool-calling",
        prefix=FPA_SYSTEM_PROMPT,
    )

    return agent


def ask(question: str, verbose: bool = True) -> str:
    """Ask a natural language question to the agent and return the answer."""
    agent = build_agent(verbose=verbose)
    result = agent.invoke({"input": question})
    return result["output"]


if __name__ == "__main__":
    # Manual smoke test with the same question as before
    question = "Which 3 accounts have the largest budget variance in Q1 2026? Explain what this means."
    print(f"Q: {question}\n")
    answer = ask(question)
    print(f"\n=== FINAL ANSWER ===")
    print(answer)