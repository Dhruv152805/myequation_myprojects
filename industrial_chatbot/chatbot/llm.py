"""
llm.py — Local CPU LLM Engine
Always uses HuggingFacePipeline (100% local, no API routing issues).
"""

import streamlit as st
from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline

MODEL_OPTIONS = {
    "⚡ Fast Agent — Qwen 0.5B (Sub-second)":    "Qwen/Qwen2.5-0.5B-Instruct",
    "🎯 Balanced Agent — Qwen 1.5B (Better Quality)": "Qwen/Qwen2.5-1.5B-Instruct",
}


@st.cache_resource(show_spinner=False)
def get_llm(api_token: str = "", model_name: str = "⚡ Fast Agent — Qwen 0.5B (Sub-second)", temperature: float = 0.1, max_tokens: int = 250):
    """
    Always loads a local HuggingFace pipeline.
    No external API calls — runs entirely on your CPU.
    """
    model_id = MODEL_OPTIONS.get(model_name, "Qwen/Qwen2.5-0.5B-Instruct")

    pipe = pipeline(
        "text-generation",
        model=model_id,
        max_new_tokens=max_tokens,
        do_sample=False,          # Greedy decoding — fastest & most deterministic
        return_full_text=False,   # Return only new tokens, not the prompt
    )
    return HuggingFacePipeline(pipeline=pipe)
