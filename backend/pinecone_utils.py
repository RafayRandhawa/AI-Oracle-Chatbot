from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()   


# Initialize Pinecone
pc = Pinecone(os.getenv('PINECONE_API_KEY'))

index_name = "oracle-metadata"

# Create index if it doesn't exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

index = pc.Index(index_name)

# Upsert metadata
def upsert_metadata(meta_chunks: list[dict]):
    upserts = []

    for chunk in meta_chunks:
        _id = chunk.get("id")
        _vec = chunk.get("vector")
        _meta = chunk.get("metadata")

        if not isinstance(_id, str) or not isinstance(_vec, list) or not isinstance(_meta, dict):
            print(f"[❌] Invalid vector format: {chunk}")
            continue
        if not all(isinstance(x, float) for x in _vec):
            print(f"[❌] Vector for ID {_id} contains non-floats")
            continue

        upserts.append((_id, _vec, _meta))

    if upserts:
        index.upsert(vectors=upserts, namespace="ai oracle metadata")
        print(f"[✅] Upserted {len(upserts)} vectors.")
    else:
        print("[⚠️] No valid vectors to upsert.")




# Query similar metadata
def query_similar_metadata(embedding, top_k=5):
    response = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True
    )
    return [item["metadata"]["text"] for item in response["matches"]]
