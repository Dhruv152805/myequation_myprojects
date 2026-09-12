"""
embeddings.py
-------------
WHAT ARE EMBEDDINGS?
  An embedding is a list of numbers (a "vector") that represents
  the MEANING of a piece of text.
  
  Example:
    "boiler pressure too high"  → [0.23, -0.87, 0.45, ... (384 numbers)]
    "steam pressure exceeded"   → [0.21, -0.85, 0.47, ... (very similar!)]
    "the cat sat on the mat"    → [-0.62, 0.33, -0.71, ... (very different)]
  
  Similar meanings → similar vectors → ChromaDB finds them together!

MODEL: sentence-transformers/all-MiniLM-L6-v2
  - Only 22MB download
  - Runs on CPU (no GPU needed)
  - Produces 384-dimensional vectors
  - Great balance of speed and quality
  - Trained specifically for semantic similarity tasks

@st.cache_resource:
  This decorator tells Streamlit to load the model ONCE and reuse it.
  Without it, the model would re-download every time the user interacts.
"""

import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings


@st.cache_resource(show_spinner=False)
def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Load the sentence-transformer embedding model.
    First call: downloads ~22MB and loads into memory.
    All subsequent calls: returns the cached model instantly.
    """
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},        # Use CPU (works on any PC)
        encode_kwargs={"normalize_embeddings": True},  # L2 normalize for cosine similarity
    )
