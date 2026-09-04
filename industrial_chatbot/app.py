"""
app.py — Premium AI Chatbot Interface
Ultra-modern glassmorphism dark theme with gradient orbs and premium animations
"""

import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from chatbot.document_loader import process_uploaded_file
from chatbot.vector_store import VectorStoreManager
from chatbot.llm import get_llm, MODEL_OPTIONS
from chatbot.pipeline import build_rag_pipeline, build_chat_pipeline, ask_question

st.set_page_config(page_title="NexusAI", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
    background: #080812 !important;
    color: #e2e8f0 !important;
    overflow-x: hidden;
}

/* Animated gradient orbs background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: -20%;
    left: -10%;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    animation: float1 8s ease-in-out infinite;
}
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    bottom: -20%;
    right: -10%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    animation: float2 10s ease-in-out infinite;
}
@keyframes float1 { 0%,100%{transform:translateY(0) translateX(0)} 50%{transform:translateY(40px) translateX(20px)} }
@keyframes float2 { 0%,100%{transform:translateY(0) translateX(0)} 50%{transform:translateY(-30px) translateX(-15px)} }

#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }

/* ── SIDEBAR ─────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(15, 15, 30, 0.85) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(99,102,241,0.2) !important;
    padding: 0 !important;
}
[data-testid="stSidebarContent"] { padding: 1.5rem 1rem !important; }

.sidebar-logo {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 700;
    background: linear-gradient(135deg, #818cf8, #c084fc, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 24px;
    letter-spacing: -0.5px;
}

.sb-section { font-size: 10px; font-weight: 600; letter-spacing: 0.12em; color: #475569; text-transform: uppercase; margin: 20px 0 8px; }

.sb-item {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 12px; border-radius: 10px;
    font-size: 13.5px; color: #94a3b8; cursor: pointer;
    transition: all 0.15s;
    margin-bottom: 2px;
    font-weight: 500;
}
.sb-item:hover { background: rgba(99,102,241,0.12); color: #c7d2fe; }
.sb-item.active { background: rgba(99,102,241,0.18); color: #a5b4fc; }

.doc-badge {
    display: flex; align-items: center; gap: 8px;
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px; color: #94a3b8;
    margin-bottom: 6px;
    word-break: break-word;
}

.stat-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.25);
    border-radius: 20px;
    padding: 4px 10px;
    font-size: 11px; color: #34d399; font-weight: 600;
    margin-top: 8px;
}

/* ── MAIN AREA ────────────────────────────────────────────────── */
.main .block-container {
    max-width: 820px !important;
    padding: 2rem 1.5rem 9rem !important;
    margin: 0 auto !important;
    position: relative; z-index: 1;
}

/* ── HERO ──────────────────────────────────────────────────────── */
.hero-wrap {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero-icon {
    width: 62px; height: 62px;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    border-radius: 18px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 28px;
    box-shadow: 0 0 40px rgba(99,102,241,0.4);
    margin-bottom: 18px;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 36px; font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin-bottom: 10px;
}
.hero-title span {
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub { font-size: 15px; color: #64748b; font-weight: 400; }

/* ── CHAT MESSAGES ─────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 0 !important;
    gap: 14px !important;
}

/* User bubble */
.user-bubble {
    background: linear-gradient(135deg, rgba(79,70,229,0.35), rgba(124,58,237,0.25));
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    font-size: 14.5px; color: #e2e8f0;
    max-width: 82%;
    margin-left: auto;
    backdrop-filter: blur(8px);
    line-height: 1.6;
    box-shadow: 0 4px 20px rgba(79,70,229,0.15);
}

/* AI bubble */
.ai-bubble {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(51,65,85,0.5);
    border-radius: 4px 18px 18px 18px;
    padding: 14px 18px;
    font-size: 14.5px; color: #cbd5e1;
    backdrop-filter: blur(8px);
    line-height: 1.7;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

/* Source tag */
.src-tag {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px; color: #818cf8;
    margin: 6px 4px 0 0;
    font-weight: 500;
}

/* ── QUICK CHIPS ──────────────────────────────────────────────── */
.chips { display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin: 20px 0; }
.chip {
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(51,65,85,0.6);
    border-radius: 22px;
    padding: 8px 16px;
    font-size: 13px; color: #94a3b8; font-weight: 500;
    cursor: pointer;
    backdrop-filter: blur(10px);
    transition: all 0.2s;
    display: flex; align-items: center; gap: 7px;
}
.chip:hover { border-color: rgba(99,102,241,0.5); color: #a5b4fc; background: rgba(99,102,241,0.08); }

/* ── AGENT SELECTOR ────────────────────────────────────────────── */
.agent-wrap {
    display: flex; justify-content: center; margin-bottom: 18px;
}
.agent-label {
    font-size: 11px; color: #475569; text-transform: uppercase;
    letter-spacing: 0.08em; font-weight: 600; text-align: center;
    margin-bottom: 8px;
}

/* ── FLOATING INPUT ─────────────────────────────────────────────── */
[data-testid="stChatInput"] > div {
    background: rgba(15, 23, 42, 0.9) !important;
    border: 1px solid rgba(99,102,241,0.35) !important;
    border-radius: 18px !important;
    box-shadow: 0 0 0 1px rgba(99,102,241,0.1), 0 20px 40px rgba(0,0,0,0.4) !important;
    backdrop-filter: blur(20px) !important;
    transition: border-color 0.2s !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: rgba(129,140,248,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12), 0 20px 40px rgba(0,0,0,0.4) !important;
}
[data-testid="stChatInput"] textarea {
    color: #e2e8f0 !important;
    font-size: 14.5px !important;
    background: transparent !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #475569 !important; }

/* Submit button inside input */
[data-testid="stChatInputSubmitButton"] > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    transition: opacity 0.2s !important;
}
[data-testid="stChatInputSubmitButton"] > button:hover { opacity: 0.85 !important; }

/* Streamlit Buttons */
div[data-testid="stButton"] > button {
    background: rgba(99,102,241,0.1) !important;
    color: #a5b4fc !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stButton"] > button:hover {
    background: rgba(99,102,241,0.2) !important;
    border-color: rgba(99,102,241,0.4) !important;
    color: #c7d2fe !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    color: #a5b4fc !important;
    font-size: 13px !important;
}

/* Popover */
[data-testid="stPopover"] > button {
    background: rgba(99,102,241,0.1) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
    color: #818cf8 !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    transition: all 0.2s !important;
}
[data-testid="stPopover"] > button:hover {
    background: rgba(99,102,241,0.2) !important;
    border-color: rgba(129,140,248,0.5) !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: rgba(15,23,42,0.5) !important;
    border: 1px solid rgba(51,65,85,0.5) !important;
    border-radius: 10px !important;
    margin-top: 6px !important;
}

/* Spinner */
[data-testid="stSpinner"] { color: #818cf8 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for key, val in {
    "chat_history": [], "vs_manager": None, "rag_chain": None,
    "chat_chain": None, "indexed_files": [], "active_agent": list(MODEL_OPTIONS.keys())[0]
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

if st.session_state.vs_manager is None:
    st.session_state.vs_manager = VectorStoreManager()

api_token    = os.environ.get("HUGGINGFACEHUB_API_TOKEN", "")
chunk_count  = st.session_state.vs_manager.get_chunk_count()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">✦ NexusAI</div>', unsafe_allow_html=True)

    if st.button("＋  New Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("""
    <div class="sb-item active">💬 &nbsp;Chat</div>
    <div class="sb-item">📁 &nbsp;Projects</div>
    <div class="sb-item">🎨 &nbsp;Artifacts</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Knowledge Base</div>', unsafe_allow_html=True)
    if st.session_state.indexed_files:
        for fname in st.session_state.indexed_files:
            st.markdown(f'<div class="doc-badge">📄 {fname}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:12px;color:#475569;padding:4px 0;">No files attached yet</p>', unsafe_allow_html=True)

    if chunk_count > 0:
        st.markdown(f'<div class="stat-pill">✓ {chunk_count} chunks indexed</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-section" style="margin-top:28px;">Agent</div>', unsafe_allow_html=True)
    chosen_agent = st.selectbox("Agent", list(MODEL_OPTIONS.keys()), index=0, label_visibility="collapsed")

    if chosen_agent != st.session_state.active_agent:
        st.session_state.active_agent = chosen_agent
        st.session_state.rag_chain    = None
        st.session_state.chat_chain   = None

    if chunk_count > 0:
        st.markdown('<div style="margin-top:auto; padding-top:24px;"></div>', unsafe_allow_html=True)
        if st.button("🗑  Clear Knowledge Base", use_container_width=True):
            st.session_state.vs_manager.clear_all()
            st.session_state.indexed_files = []
            st.session_state.rag_chain = None
            st.session_state.chat_history = []
            st.rerun()

# ── PIPELINE INIT (cached via @st.cache_resource) ────────────────────────────
if st.session_state.chat_chain is None:
    _llm = get_llm(api_token=api_token, model_name=chosen_agent)
    st.session_state.chat_chain = build_chat_pipeline(_llm)
    if chunk_count > 0:
        st.session_state.rag_chain = build_rag_pipeline(_llm, st.session_state.vs_manager.get_retriever(k=2))
elif st.session_state.rag_chain is None and chunk_count > 0:
    _llm = get_llm(api_token=api_token, model_name=chosen_agent)
    st.session_state.rag_chain = build_rag_pipeline(_llm, st.session_state.vs_manager.get_retriever(k=2))

# ── HERO ──────────────────────────────────────────────────────────────────────
if not st.session_state.chat_history:
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-icon">✦</div>
        <div class="hero-title">Hello, <span>Dhruv</span></div>
        <div class="hero-title" style="font-size:30px;color:#475569;font-weight:500;">How can I help you today?</div>
        <p class="hero-sub" style="margin-top:12px;">Ask anything · Attach documents · Switch agents</p>
    </div>
    <div class="chips">
        <div class="chip">💡 Explain a concept</div>
        <div class="chip">📄 Summarize a document</div>
        <div class="chip">🔍 Find key info</div>
        <div class="chip">⚙️ Technical questions</div>
        <div class="chip">✍️ Draft & write</div>
    </div>
    """, unsafe_allow_html=True)

# ── CHAT HISTORY RENDER ───────────────────────────────────────────────────────
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        with st.chat_message("user", avatar=None):
            st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(f'<div class="ai-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("mode") == "rag" and msg.get("sources"):
                tags = "".join(
                    f'<span class="src-tag">📄 {doc.metadata.get("source_filename","doc")} #{i}</span>'
                    for i, doc in enumerate(msg["sources"], 1)
                )
                st.markdown(f'<div style="margin-top:8px;">{tags}</div>', unsafe_allow_html=True)
                for i, doc in enumerate(msg["sources"], 1):
                    fname = doc.metadata.get("source_filename", "document")
                    with st.expander(f"Excerpt #{i} — {fname}", expanded=False):
                        st.markdown(f"*{doc.page_content}*")

# ── ATTACH BUTTON + CHAT INPUT ────────────────────────────────────────────────
with st.popover("➕  Attach File  (PDF · DOCX · TXT · CSV · JSON · Code)", use_container_width=True):
    st.markdown("#### Attach to Knowledge Base")
    up_files = st.file_uploader(
        "Drag & drop any file",
        type=["pdf","docx","txt","md","csv","json","py","js","html","log","c","cpp"],
        accept_multiple_files=True,
        key="file_up",
    )
    if up_files:
        if st.button("⚡ Index Now", use_container_width=True):
            new_f = [f for f in up_files if f.name not in st.session_state.indexed_files]
            if new_f:
                with st.spinner("Indexing…"):
                    total = 0
                    for f in new_f:
                        chunks = process_uploaded_file(f)
                        st.session_state.vs_manager.add_documents(chunks)
                        st.session_state.indexed_files.append(f.name)
                        total += len(chunks)
                    st.session_state.rag_chain = None
                    st.success(f"✓ Indexed {total} chunks from {len(new_f)} file(s)")
                    st.rerun()

# ── PROMPT HANDLING ────────────────────────────────────────────────────────────
prompt = st.chat_input("Message NexusAI…")

if prompt:
    with st.chat_message("user", avatar=None):
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner(""):
            try:
                result = ask_question(
                    rag_chain=st.session_state.rag_chain,
                    chat_chain=st.session_state.chat_chain,
                    question=prompt,
                )
                answer  = result["answer"]
                sources = result["source_docs"]
                mode    = result["mode"]
            except Exception as e:
                answer, sources, mode = f"Error: {e}", [], "chat"

        st.markdown(f'<div class="ai-bubble">{answer}</div>', unsafe_allow_html=True)

        if mode == "rag" and sources:
            tags = "".join(
                f'<span class="src-tag">📄 {doc.metadata.get("source_filename","doc")} #{i}</span>'
                for i, doc in enumerate(sources, 1)
            )
            st.markdown(f'<div style="margin-top:8px;">{tags}</div>', unsafe_allow_html=True)
            for i, doc in enumerate(sources, 1):
                fname = doc.metadata.get("source_filename", "document")
                with st.expander(f"Excerpt #{i} — {fname}", expanded=False):
                    st.markdown(f"*{doc.page_content}*")

    st.session_state.chat_history.append({
        "role": "assistant", "content": answer,
        "sources": sources, "mode": mode,
    })
