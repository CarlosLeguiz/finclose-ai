"""SQL agent that translates natural language questions into SQL queries
against the FinClose AI marts layer, executes them, and returns answers.

Uses LangChain's create_sql_agent with OpenAI as the LLM, customized with
an FP&A-aware system prompt to ensure accounting-correct interpretations.

Includes guardrails:
- Read-only SQL enforcement at the database layer (read_only=True)
- Top-level error handling in ask()
- In-memory cache for repeated questions (lru_cache)
- Simple logging of every question to logs/ai_queries.log
"""

import logging
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

from ai_layer.agent.connection import get_database
from ai_layer.agent.prompts import FPA_SYSTEM_PROMPT

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

# Set up logging to file (created on first call)
LOG_PATH = PROJECT_ROOT / "logs" / "ai_queries.log"
LOG_PATH.parent.mkdir(exist_ok=True)
logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def build_agent(verbose: bool = True):
    """Build and return a SQL agent configured for the FinClose AI marts."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not found in environment. Check your .env file."
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


@lru_cache(maxsize=128)
def _cached_ask(question: str, verbose: bool) -> str:
    """Internal cached layer. Same question → same answer until process restart.

    @lru_cache stores up to 128 (question, verbose) tuples in memory.
    """
    agent = build_agent(verbose=verbose)
    result = agent.invoke({"input": question})
    return result["output"]


def ask(question: str, verbose: bool = False) -> str:
    """Ask a natural language question and return the agent's analysis.

    Logs every question to logs/ai_queries.log and caches results in memory.
    Top-level error handling returns a user-friendly message instead of
    propagating raw exceptions to the dashboard.
    """
    logger.info(f"QUESTION: {question[:200]}")
    try:
        answer = _cached_ask(question, verbose)
        logger.info(f"ANSWER_OK: {answer[:200]}")
        return answer
    except Exception as e:
        logger.error(f"AGENT_ERROR: {type(e).__name__}: {e}")
        return (
            f"I could not complete the analysis due to a technical error: "
            f"{type(e).__name__}. Please try a different question or contact support."
        )


if __name__ == "__main__":
    question = "Which 3 accounts have the largest budget variance in Q1 2026? Explain what this means."
    print(f"Q: {question}\n")
    answer = ask(question, verbose=True)
    print(f"\n=== FINAL ANSWER ===")
    print(answer)