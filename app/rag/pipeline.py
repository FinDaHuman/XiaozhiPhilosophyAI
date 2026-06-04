"""
RAG Pipeline

Orchestrates the full RAG flow:
  Question → Embed → Retrieve → Build Prompt → Groq → Answer

Exposes a simple `ask(question)` interface for MCP compatibility.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from groq import Groq

from app.rag.retriever import PhilosophyRetriever
from app.rag.prompts import SYSTEM_PROMPT, ROUTER_PROMPT, build_prompt
from app.rag.ingest import run_ingest_pipeline

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


class RAGPipeline:
    """
    Main RAG pipeline class.
    Simple interface: answer = rag.ask(question)
    """

    def __init__(self):
        self.retriever = PhilosophyRetriever()
        self._client: Optional[Groq] = None
        self._conversation_history: list[dict] = []

    @property
    def client(self) -> Groq:
        """Lazy-initialize the Groq client."""
        if self._client is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("Missing GROQ_API_KEY in .env")
            self._client = Groq(api_key=api_key)
        return self._client

    def ask(self, question: str) -> str:
        """
        Ask a philosophy question. Returns the answer as a string.
        This is the MCP-compatible interface.
        """
        
        # Step 1: Agentic Routing (GREETING vs QUESTION)
        router_messages = [
            {"role": "user", "content": ROUTER_PROMPT.format(question=question)}
        ]
        router_completion = self.client.chat.completions.create(
            model="llama-3.1-8b-instant", # Use fast model for routing
            messages=router_messages,
            temperature=0,
            max_tokens=10,
        )
        route = router_completion.choices[0].message.content.strip().upper()
        
        if "GREETING" in route:
            # Skip retrieval for greetings
            user_prompt = question
        else:
            # Step 2: Retrieve relevant chunks (MultiQuery + Hybrid)
            context_docs = self.retriever.retrieve(question)

            # Step 3: Build prompt with context
            user_prompt = build_prompt(question, context_docs)

        # Step 4: Build messages for generation
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        # Add conversation history (last 6 exchanges for context)
        for entry in self._conversation_history[-6:]:
            messages.append({"role": "user", "content": entry["question"]})
            messages.append({"role": "assistant", "content": entry["answer"]})

        messages.append({"role": "user", "content": user_prompt})

        # Step 5: Call Groq
        completion = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
        )
        answer = completion.choices[0].message.content or ""

        # Step 6: Store in conversation history
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
            "model": GROQ_MODEL,
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
