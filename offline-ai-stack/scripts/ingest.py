"""Ingest a project directory into the local Chroma 'project-memory' collection."""
import sys

import chromadb
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

if len(sys.argv) < 2:
    print("Usage: ingest.py <project_dir>", file=sys.stderr)
    sys.exit(2)

client = chromadb.HttpClient(host="localhost", port=8002)
collection = client.get_or_create_collection("project-memory")
vstore = ChromaVectorStore(chroma_collection=collection)
storage = StorageContext.from_defaults(vector_store=vstore)
embed = HuggingFaceEmbedding(model_name="Qwen/Qwen3-Embedding-8B")

docs = SimpleDirectoryReader(
    sys.argv[1],
    recursive=True,
    required_exts=[".md", ".py", ".ts", ".tsx", ".rs", ".go", ".java"],
).load_data()
VectorStoreIndex.from_documents(docs, storage_context=storage, embed_model=embed)
print(f"Ingested {len(docs)} docs from {sys.argv[1]} into 'project-memory'.")
