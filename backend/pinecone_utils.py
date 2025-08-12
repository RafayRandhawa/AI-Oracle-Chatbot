from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()   


# Initialize Pinecone
pc = Pinecone(os.getenv('PINECONE_API_KEY'))

index_name = "chatbot"

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
def upsert_metadata(meta_chunks: list[dict], batch_size: int = 300):
    upserts = []
    total_upserted = 0

    for chunk in meta_chunks:
        _id = chunk.get("id")
        _vec = chunk.get("vector")
        _meta = chunk.get("metadata")

        if not isinstance(_id, str) or not isinstance(_vec, list) or not isinstance(_meta, dict):
            print(f"Invalid vector format: {chunk}")
            continue
        if not all(isinstance(x, float) for x in _vec):
            print(f"Vector for ID {_id} contains non-floats")
            continue

        upserts.append((_id, _vec, _meta))

        # When batch is full, upsert to Pinecone
        if len(upserts) == batch_size:
            index.upsert(vectors=upserts, namespace="chatbot")
            total_upserted += len(upserts)
            print(f"[✅] Upserted {len(upserts)} vectors.")
            upserts = []

    # Upsert any remaining vectors after the loop
    if upserts:
        index.upsert(vectors=upserts, namespace="chatbot")
        total_upserted += len(upserts)
        print(f"[✅] Upserted remaining {len(upserts)} vectors.")

    if total_upserted == 0:
        print("[⚠️] No valid vectors to upsert.")
    else:
        print(f"[✅] Finished. Total upserted vectors: {total_upserted}")


# Query similar metadata
def query_similar_metadata(embedding, top_k=5):
    response = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True,
        namespace="chatbot"
    )
    
    print(f"Query response: {response}")
    return [item["metadata"] for item in response.get("matches", [])]
