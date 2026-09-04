"""
document_loader.py
------------------
Ultra-Fast Universal Document Loader
Supports: PDF, DOCX, TXT, MD, CSV, JSON, PY, HTML, LOG
"""

import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def read_docx_fast(file_path: str) -> str:
    """Ultra-fast native XML reader for .docx files (no external library required)."""
    try:
        with zipfile.ZipFile(file_path) as z:
            xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            paragraphs = []
            for elem in tree.iter():
                if elem.tag.endswith("}p"):
                    texts = [e.text for e in elem.iter() if e.text]
                    if texts:
                        paragraphs.append("".join(texts))
            return "\n".join(paragraphs)
    except Exception as e:
        raise ValueError(f"Failed to read DOCX file: {e}")


def load_document(file_path: str, file_extension: str) -> list[Document]:
    """Load any document format fast and return LangChain Document objects."""
    ext = file_extension.lower().lstrip(".")
    
    if ext == "pdf":
        loader = PyPDFLoader(file_path)
        return loader.load()
    elif ext == "docx":
        text = read_docx_fast(file_path)
        return [Document(page_content=text, metadata={"source": file_path})]
    elif ext in ["txt", "md", "csv", "json", "py", "js", "html", "css", "log", "c", "cpp"]:
        # Direct fast text load with fallback encodings
        text = ""
        for encoding in ["utf-8", "latin-1", "cp1252"]:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    text = f.read()
                break
            except UnicodeDecodeError:
                continue
        return [Document(page_content=text, metadata={"source": file_path})]
    else:
        # Generic text fallback
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return [Document(page_content=text, metadata={"source": file_path})]


def chunk_documents(documents: list[Document], chunk_size: int = 400, chunk_overlap: int = 40) -> list[Document]:
    """Split documents into optimized chunks for fast vector searching."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def process_uploaded_file(uploaded_file) -> list[Document]:
    """Save uploaded streamlit file temporarily, load fast, chunk, and return."""
    ext = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else "txt"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        docs = load_document(tmp_path, ext)
        for doc in docs:
            doc.metadata["source_filename"] = uploaded_file.name
        chunks = chunk_documents(docs)
        return chunks
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
