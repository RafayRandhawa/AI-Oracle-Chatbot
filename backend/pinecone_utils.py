from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()   


# Initialize Pinecone
pc = Pinecone(api_key='pcsk_2zM3GB_EEG9zdqHWBne9D8bxyLSwSHUo5z947ep85VJvaxZ7WUDV4VJMHmeNWk3agQAyFQ')

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
def upsert_metadata(texts, vectors):
    upserts = []
    for i in range(len(texts)):
        _id = f"meta-{i}"
        _vec = vectors[i]
        _meta = {"text": texts[i]}

        # Check validity
        if not isinstance(_id, str) or not isinstance(_vec, list) or not isinstance(_meta, dict):
            print(f"[❌] Invalid vector format at index {i}")
            continue
        if not all(isinstance(x, float) for x in _vec):
            print(f"[❌] Vector at index {i} contains non-floats")
            continue

        upserts.append((_id, _vec, _meta))

    #print(f"[✅] Prepared {len(upserts)} vectors for upsert")
    #print("Sample vector:", upserts[0] if upserts else "None")

    index.upsert(vectors=upserts, namespace="ai oracle metadata")



# Query similar metadata
def query_similar_metadata(embedding, top_k=5):
    response = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True
    )
    return [item["metadata"]["text"] for item in response["matches"]]
