"""Ingest a project directory into the local Chroma 'project-memory' collection.

Embedding model is loaded from a local path under ~/offline-ai-stack/models/
(populated by scripts/offline-prep.sh). No HuggingFace repo IDs are used at
runtime; the path is plain filesystem and resolves without touching the
HF Hub, even if `HF_HUB_OFFLINE` weren't set.
"""
import os
import sys
from pathlib import Path

import chromadb
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

if len(sys.argv) < 2:
    print("Usage: ingest.py <project_dir>", file=sys.stderr)
    sys.exit(2)

STACK_HOME = Path(os.environ.get("STACK_HOME", str(Path.home() / "offline-ai-stack")))
EMBED_MODEL_PATH = STACK_HOME / "models" / "qwen3-embedding-8b"
if not EMBED_MODEL_PATH.is_dir():
    print(
        f"Embedding model missing at {EMBED_MODEL_PATH}. "
        f"Run `make offline-prep` to populate it.",
        file=sys.stderr,
    )
    sys.exit(2)

client = chromadb.HttpClient(host="localhost", port=8002)
collection = client.get_or_create_collection("project-memory")
vstore = ChromaVectorStore(chroma_collection=collection)
storage = StorageContext.from_defaults(vector_store=vstore)
# Local-path string; sentence-transformers/transformers will load files
# from disk and never resolve a repo ID against the HF Hub.
embed = HuggingFaceEmbedding(model_name=str(EMBED_MODEL_PATH))

docs = SimpleDirectoryReader(
    sys.argv[1],
    recursive=True,
    required_exts=[".md", ".py", ".ts", ".tsx", ".rs", ".go", ".java"],
).load_data()
VectorStoreIndex.from_documents(docs, storage_context=storage, embed_model=embed)
print(f"Ingested {len(docs)} docs from {sys.argv[1]} into 'project-memory'.")
