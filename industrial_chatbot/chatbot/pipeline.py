"""
pipeline.py — Smart Dual-Mode RAG Pipeline
-------------------------------------------
Mode 1 — CHAT MODE: General greetings, casual questions → Direct LLM reply (instant, no file scan)
Mode 2 — RAG MODE:  Document questions → ChromaDB search + LLM grounded answer
"""

import re
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# ── Prompt for RAG Mode (Document Search) ─────────────────────────────────────
RAG_PROMPT_TEMPLATE = """You are a helpful AI assistant. Answer the user's question using the provided document context.

Instructions:
- Use ONLY the information in the Context below to answer
- Be concise and direct
- If the answer is not in the context, say: "I couldn't find that in the uploaded documents."

Context:
{context}

Question: {question}

Answer:"""

# ── Prompt for Direct Chat Mode (No file scanning) ────────────────────────────
CHAT_PROMPT_TEMPLATE = """You are a friendly and helpful AI assistant named Claude. Reply naturally and conversationally. Be concise.

User: {question}
Assistant:"""

# ── General Conversation Keywords (no file scan needed) ───────────────────────
CHAT_PATTERNS = [
    r"^(hi|hello|hey|hiya|howdy|good\s*(morning|afternoon|evening|night))\b",
    r"^(how are you|how r u|how's it going|what's up|sup|wassup)\b",
    r"^(thanks|thank you|ty|thx|appreciate it|cool|ok|okay|got it|great|nice)\b",
    r"^(who are you|what are you|what can you do|tell me about yourself)\b",
    r"^(bye|goodbye|see you|cya|later|take care)\b",
    r"^(yes|no|sure|of course|definitely|nope|yep|yeah)\b",
]


def is_casual_message(text: str) -> bool:
    """
    Returns True if message is general chat (no need to scan documents).
    Short messages under 4 words with no domain keywords are also treated as casual.
    """
    text_clean = text.strip().lower()
    
    # Check against known casual patterns
    for pattern in CHAT_PATTERNS:
        if re.search(pattern, text_clean, re.IGNORECASE):
            return True
    
    # Short messages (≤4 words) with no document-specific keywords are casual
    word_count = len(text_clean.split())
    doc_keywords = ["what", "how", "why", "explain", "describe", "list", "find",
                    "document", "file", "resume", "manual", "specification", "pressure",
                    "safety", "maintenance", "procedure", "show", "tell me about"]
    has_doc_keyword = any(kw in text_clean for kw in doc_keywords)
    
    if word_count <= 3 and not has_doc_keyword:
        return True
    
    return False


def _format_docs(docs: list) -> str:
    """Combine retrieved document chunks into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_pipeline(llm, retriever):
    """Build the LCEL RAG chain for document search mode."""
    prompt = PromptTemplate(
        template=RAG_PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )
    chain = RunnableParallel(
        {
            "source_docs": retriever,
            "question":    RunnablePassthrough(),
        }
    ).assign(
        context=lambda x: _format_docs(x["source_docs"]),
    ).assign(
        answer=prompt | llm | StrOutputParser()
    )
    return chain


def build_chat_pipeline(llm):
    """Build the direct LLM chat chain (no RAG, no file scan)."""
    prompt = PromptTemplate(
        template=CHAT_PROMPT_TEMPLATE,
        input_variables=["question"],
    )
    chain = prompt | llm | StrOutputParser()
    return chain


def ask_question(rag_chain, chat_chain, question: str) -> dict:
    """
    Smart router:
    - Casual message → direct LLM reply (instant, no file scanning)
    - Document question → RAG pipeline (ChromaDB search + LLM answer)
    Returns: { "answer": str, "source_docs": list, "mode": "chat" | "rag" }
    """
    if is_casual_message(question):
        # Direct chat mode — no document scanning
        answer = chat_chain.invoke({"question": question})
        return {
            "answer":      answer.strip() if answer else "Hello! How can I help you?",
            "source_docs": [],
            "mode":        "chat",
        }
    else:
        # RAG mode — scan documents for grounded answer
        result = rag_chain.invoke(question)
        return {
            "answer":      result.get("answer", "No answer generated.").strip(),
            "source_docs": result.get("source_docs", []),
            "mode":        "rag",
        }
