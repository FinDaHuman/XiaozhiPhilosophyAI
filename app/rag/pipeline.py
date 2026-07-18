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
from app.rag.prompts import SYSTEM_PROMPT, VOICE_SYSTEM_PROMPT, ROUTER_PROMPT, build_prompt
from app.rag.ingest import run_ingest_pipeline

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Heuristic routing markers: obvious cases skip the router LLM round-trip.
# Question markers win over greeting markers ("Chào Lily, độc quyền là gì?"
# must route to QUESTION).
_QUESTION_MARKERS = (
    "?", "là gì", "la gi", "tại sao", "tai sao", "vì sao", "vi sao",
    "như thế nào", "nhu the nao", "thế nào", "the nao", "trình bày",
    "trinh bay", "giải thích", "giai thich", "so sánh", "so sanh",
    "ví dụ", "vi du", "phân tích", "phan tich", "nêu", "tóm tắt",
    "tom tat", "slide", "khái niệm", "khai niem", "quy luật", "quy luat",
    "mâu thuẫn", "mau thuan", "độc quyền", "doc quyen", "cạnh tranh",
    "canh tranh", "tư bản", "tu ban", "vnindex", "cổ phiếu", "co phieu",
    "chứng khoán", "chung khoan", "tín hiệu", "tin hieu",
    "donganh", "hiro",
)
_GREETING_MARKERS = (
    "chào", "chao", "hello", "hi", "helo", "alo",
    "cảm ơn", "cam on", "thank", "cám ơn",
    "tạm biệt", "tam biet", "bye", "ok", "oke", "okay", "tuyệt", "tuyet",
)


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

    @staticmethod
    def _classify_fast(question: str):
        """
        Heuristic GREETING/QUESTION classification for obvious inputs.
        Returns None for the ambiguous middle (falls through to the
        router LLM), so a bare topic like "vật chất" still gets the
        careful route. Real questions can only gain speed, never quality:
        they take the same QUESTION path either way.
        """
        q = question.lower().strip()
        if any(marker in q for marker in _QUESTION_MARKERS):
            return "QUESTION"
        if len(q) > 50:
            return "QUESTION"
        if any(marker in q for marker in _GREETING_MARKERS):
            return "GREETING"
        return None

    def _prepare_messages(
        self,
        question: str,
        *,
        history: Optional[list] = None,
        voice: bool = False,
    ) -> list:
        """
        Build the message list for generation: routing, retrieval, prompt
        construction and history splicing. `history` (list of dicts with
        "question"/"answer") overrides the server-side shared history;
        `voice` selects the spoken-style persona for the robot.
        """
        # Step 1: Routing (GREETING vs QUESTION) — heuristic first, router
        # LLM only for the ambiguous middle (short input, no markers).
        route = self._classify_fast(question)
        if route is None:
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
            {"role": "system", "content": VOICE_SYSTEM_PROMPT if voice else SYSTEM_PROMPT},
        ]

        # Voice mode is stateless per question (the robot cloud manages its
        # own conversation); otherwise use the provided or shared history.
        effective_history = [] if voice else (
            history if history is not None else self._conversation_history
        )
        for entry in effective_history[-6:]:
            messages.append({"role": "user", "content": entry["question"]})
            messages.append({"role": "assistant", "content": entry["answer"]})

        messages.append({"role": "user", "content": user_prompt})
        return messages

    def ask(
        self,
        question: str,
        *,
        history: Optional[list] = None,
        voice: bool = False,
    ) -> str:
        """
        Ask a philosophy question. Returns the answer as a string.
        This is the MCP-compatible interface. Called with no kwargs it
        behaves exactly as before (shared server-side history).
        """
        messages = self._prepare_messages(question, history=history, voice=voice)

        # Step 5: Call Groq
        completion = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=300 if voice else 2048,
        )
        answer = completion.choices[0].message.content or ""

        # Step 6: Store in shared conversation history — only on the legacy
        # path; when the client sends its own history (or voice mode) the
        # server keeps no state.
        if history is None and not voice:
            self._conversation_history.append({
                "question": question,
                "answer": answer,
            })

        return answer

    def ask_stream(self, question: str, *, history: Optional[list] = None):
        """
        Streaming variant of ask(): yields answer tokens as they arrive.
        Same retrieval/prompt path; history semantics match ask().
        """
        messages = self._prepare_messages(question, history=history, voice=False)

        stream = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
            stream=True,
        )
        parts = []
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                parts.append(delta)
                yield delta

        if history is None:
            self._conversation_history.append({
                "question": question,
                "answer": "".join(parts),
            })

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
