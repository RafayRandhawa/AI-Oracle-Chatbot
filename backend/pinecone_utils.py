from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()   

# Initialize Pinecone
pc = Pinecone(os.getenv('PINECONE_API_KEY'))

index_name = os.getenv('PINECONE_INDEX_NAME')

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
def upsert_metadata(meta_chunks: list[dict], batch_size: int = 100):  # Reduced batch size
    upserts = []
    total_upserted = 0
    failed_count = 0

    for chunk in meta_chunks:
        try:
            _id = chunk.get("id")
            _vec = chunk.get("vector")
            _meta = chunk.get("metadata")

            # Validation checks
            if not _id or not _vec or not _meta:
                print(f"❌ Missing required fields in chunk: {chunk}")
                failed_count += 1
                continue
                
            if not isinstance(_id, str):
                print(f"❌ Invalid ID type: {type(_id)} for {_id}")
                failed_count += 1
                continue
                
            if not isinstance(_vec, list) or len(_vec) == 0:
                print(f"❌ Invalid vector for ID {_id}: {_vec}")
                failed_count += 1
                continue
                
            if not all(isinstance(x, (float, int)) for x in _vec):
                print(f"❌ Vector for ID {_id} contains non-numeric values")
                failed_count += 1
                continue

            upserts.append((_id, _vec, _meta))
            print(f"✅ Prepared vector for {_id}")

            # Upsert in batches
            if len(upserts) >= batch_size:
                try:
                    response = index.upsert(
                        vectors=upserts, 
                        namespace=os.getenv('PINECONE_NAMESPACE', 'ai-oracle-metadata')
                    )
                    total_upserted += len(upserts)
                    print(f"[✅] Upserted {len(upserts)} vectors. Response: {response}")
                    upserts = []
                except Exception as e:
                    print(f"❌ Batch upsert failed: {e}")
                    failed_count += len(upserts)
                    upserts = []

        except Exception as e:
            print(f"❌ Error processing chunk: {e}")
            failed_count += 1
            continue

    # Upsert remaining vectors
    if upserts:
        try:
            response = index.upsert(
                vectors=upserts, 
                namespace=os.getenv('PINECONE_NAMESPACE', 'ai-oracle-metadata')
            )
            total_upserted += len(upserts)
            print(f"[✅] Upserted remaining {len(upserts)} vectors. Response: {response}")
        except Exception as e:
            print(f"❌ Final upsert failed: {e}")
            failed_count += len(upserts)

    print(f"\n📊 Summary:")
    print(f"✅ Successfully upserted: {total_upserted}")
    print(f"❌ Failed: {failed_count}")
    
    if total_upserted == 0:
        print("[⚠️] No vectors were upserted. Check the validation logs above.")


def check_pinecone_connection():
    """Verify Pinecone connection and index status"""
    try:
        # Check connection
        print("🔗 Checking Pinecone connection...")
        indexes = pc.list_indexes()
        print(f"✅ Connected to Pinecone. Available indexes: {indexes.names()}")
        
        # Check if our index exists
        if index_name in indexes.names():
            print(f"✅ Index '{index_name}' exists")
            
            # Check index stats
            stats = index.describe_index_stats()
            print(f"📊 Index stats: {stats}")
            
            return True
        else:
            print(f"❌ Index '{index_name}' does not exist")
            return False
            
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return False

# Query similar metadata - UPDATED FOR TABLE-LEVEL EMBEDDINGS
def query_similar_metadata(embedding, top_k=5):
    try:
        response = index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=os.getenv('PINECONE_NAMESPACE', 'ai oracle metadata')
        )
        
        results = []
        for match in response.get("matches", []):
            metadata = match.get("metadata", {})
            
            # Debug: Print the actual metadata structure
            print(f"DEBUG - Metadata received: {metadata}")
            
            # Handle table-level format (new)
            if "table" in metadata and "columns" in metadata:
                result = {
                    "table": metadata.get("table", ""),
                    "score": match.get("score", 0),
                    "table_comment": metadata.get("table_comment", ""),
                    "column_count": metadata.get("column_count", 0),
                    "primary_keys": metadata.get("primary_keys", []),
                    "foreign_keys": metadata.get("foreign_keys", []),
                    "columns": metadata.get("columns", [])
                }
                results.append(result)
            
            # Handle column-level format (old - fallback)
            elif "table" in metadata and "column" in metadata:
                result = {
                    "table": metadata.get("table", ""),
                    "column": metadata.get("column", ""),
                    "score": match.get("score", 0),
                    "type": metadata.get("type", ""),
                    "nullable": metadata.get("nullable", ""),
                    "is_primary_key": metadata.get("is_primary_key", False),
                    "is_foreign_key": metadata.get("is_foreign_key", False),
                    "foreign_key_ref": metadata.get("foreign_key_ref", "")
                }
                results.append(result)
            
            # Handle unexpected format
            else:
                print(f"WARNING: Unexpected metadata format: {metadata}")
                results.append({
                    "raw_metadata": metadata,
                    "score": match.get("score", 0)
                })
        
        return results
        
    except Exception as e:
        print(f"Error querying Pinecone: {e}")
        raise