"""
RAG Pipeline

Orchestrates the full RAG flow:
  Question → Embed → Retrieve → Build Prompt → Gemini → Answer

Exposes a simple `ask(question)` interface for MCP compatibility.
"""

import os
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv

from app.rag.retriever import PhilosophyRetriever
from app.rag.prompts import SYSTEM_PROMPT, build_prompt
from app.rag.ingest import run_ingest_pipeline

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")


class RAGPipeline:
    """
    Main RAG pipeline class.
    Simple interface: answer = rag.ask(question)
    """

    def __init__(self):
        self.retriever = PhilosophyRetriever()
        self._llm: Optional[ChatGoogleGenerativeAI] = None
        self._conversation_history: list[dict] = []

    @property
    def llm(self) -> ChatGoogleGenerativeAI:
        """Lazy-initialize the Gemini LLM."""
        if self._llm is None:
            self._llm = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.3,
                max_output_tokens=2048,
            )
        return self._llm

    def ask(self, question: str) -> str:
        """
        Ask a philosophy question. Returns the answer as a string.
        This is the MCP-compatible interface.
        """
        # Step 1: Retrieve relevant chunks
        context_docs = self.retriever.retrieve(question)

        # Step 2: Build prompt with context
        user_prompt = build_prompt(question, context_docs)

        # Step 3: Build messages
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
        ]

        # Add conversation history (last 6 exchanges for context)
        for entry in self._conversation_history[-6:]:
            messages.append(HumanMessage(content=entry["question"]))
            messages.append(AIMessage(content=entry["answer"]))

        messages.append(HumanMessage(content=user_prompt))

        # Step 4: Call Gemini
        response = self.llm.invoke(messages)
        answer = response.content

        # Step 5: Store in conversation history
        self._conversation_history.append({
            "question": question,
            "answer": answer,
        })

        return answer

    def clear_history(self):
        """Clear conversation history."""
        self._conversation_history.clear()

    def get_stats(self) -> dict:
        """Get pipeline statistics."""
        retriever_stats = self.retriever.get_collection_stats()
        return {
            "model": GEMINI_MODEL,
            "conversation_turns": len(self._conversation_history),
            "knowledge_base": retriever_stats,
        }

    def reload_knowledge_base(self, data_dir: Optional[str] = None) -> dict:
        """Re-ingest documents and reload the vector store."""
        vectorstore = run_ingest_pipeline(data_dir)
        self.retriever.reload()
        stats = self.retriever.get_collection_stats()
        return {
            "status": "reloaded",
            "stats": stats,
        }
