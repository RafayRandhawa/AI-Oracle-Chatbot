import oracledb
from db_handler import get_connection,extract_db_metadata  # reuse your existing logic
from embedder import embed_texts
from pinecone_utils import upsert_metadata
import json
from dotenv import load_dotenv
import os

load_dotenv()   



def build_meta_chunks_from_metadata(metadata: dict, embeddings: list[list[float]]) -> list[dict]:
    chunks = []
    
    if not metadata or not embeddings:
        print("❌ No metadata or embeddings provided")
        return chunks
        
    if len(embeddings) != len(metadata):
        print(f"❌ Mismatch: {len(metadata)} tables vs {len(embeddings)} embeddings")
        return chunks
    
    tables = list(metadata.items())
    for i, (table, table_meta) in enumerate(tables):
        if i >= len(embeddings):
            print(f"❌ Not enough embeddings for table {table}")
            continue
            
        # Build a comprehensive description of the entire table
        columns_description = "\n".join([
            f"  - {col['name']}: {col['type']} {'(PK)' if col['name'] in table_meta['primary_keys'] else ''}"
            f"{'(FK)' if any(fk['column'] == col['name'] for fk in table_meta['foreign_keys']) else ''}"
            f" - Nullable: {col['nullable']}"
            f" - Comment: {col['comment'] or 'No comment'}"
            for col in table_meta["columns"]
        ])
        
        # Foreign keys relationships
        fk_relationships = "\n".join([
            f"  - {fk['column']} → {fk['references']['table']}.{fk['references']['column']}"
            for fk in table_meta["foreign_keys"]
        ]) if table_meta["foreign_keys"] else "None"
        
        # Primary keys
        pk_list = ", ".join(table_meta["primary_keys"]) if table_meta["primary_keys"] else "None"
        
        # Build the complete table description
        text_chunk = f"""TABLE: {table}
Description: {table_meta['table_comment'] or 'No table comment'}

COLUMNS:
{columns_description}

PRIMARY KEYS: {pk_list}

FOREIGN KEY RELATIONSHIPS:
{fk_relationships}

TABLE STRUCTURE SUMMARY:
This table contains {len(table_meta['columns'])} columns with {len(table_meta['primary_keys'])} primary key(s) 
and {len(table_meta['foreign_keys'])} foreign key relationship(s)."""
        
        # Prepare SIMPLIFIED metadata for Pinecone (only strings, numbers, booleans, or lists of strings)
        table_metadata = {
            "table": table,
            "table_comment": table_meta['table_comment'] or "",
            "column_count": len(table_meta['columns']),
            "primary_keys": table_meta['primary_keys'],  # List of strings is OK
            "foreign_key_count": len(table_meta['foreign_keys']),
            # Convert complex objects to strings for Pinecone compatibility
            "columns_summary": f"{len(table_meta['columns'])} columns",
            "foreign_keys_summary": f"{len(table_meta['foreign_keys'])} foreign keys" if table_meta['foreign_keys'] else "No foreign keys"
        }
        
        # Add column names as a list of strings (Pinecone compatible)
        table_metadata["column_names"] = [col['name'] for col in table_meta['columns']]
        
        # Add primary key indicator for each column
        for col in table_meta['columns']:
            if col['name'] in table_meta['primary_keys']:
                table_metadata[f"col_{col['name']}_is_pk"] = True
        
        # Add foreign key information as strings
        for j, fk in enumerate(table_meta['foreign_keys']):
            table_metadata[f"fk_{j}"] = f"{fk['column']}->{fk['references']['table']}.{fk['references']['column']}"
        
        chunks.append({
            "id": f"table-{table}",
            "text": text_chunk,
            "vector": embeddings[i],
            "metadata": table_metadata
        })
    
    return chunks

def full_metadata_embedding_pipeline(owner=os.getenv('DB_USER')):
    # 1. Extract metadata
    print("📋 Extracting metadata...")
    metadata = extract_db_metadata(owner=owner)
    print(f"📊 Found {len(metadata)} tables")
    
    if not metadata:
        print("❌ No metadata extracted")
        return

    # 2. Generate table-level text chunks for embedding
    print("📝 Generating text chunks...")
    text_chunks = []
    for table, table_meta in metadata.items():
        # Build columns description
        columns_description = "\n".join([
            f"  - {col['name']}: {col['type']} {'(PK)' if col['name'] in table_meta['primary_keys'] else ''}"
            f"{'(FK)' if any(fk['column'] == col['name'] for fk in table_meta['foreign_keys']) else ''}"
            f" - Nullable: {col['nullable']}"
            f" - Comment: {col['comment'] or 'No comment'}"
            for col in table_meta["columns"]
        ])
        
        # Foreign keys relationships
        fk_relationships = "\n".join([
            f"  - {fk['column']} → {fk['references']['table']}.{fk['references']['column']}"
            for fk in table_meta["foreign_keys"]
        ]) if table_meta["foreign_keys"] else "None"
        
        # Primary keys
        pk_list = ", ".join(table_meta["primary_keys"]) if table_meta["primary_keys"] else "None"
        
        # Build the complete table description
        text_chunk = f"""TABLE: {table}
Description: {table_meta['table_comment'] or 'No table comment'}

COLUMNS:
{columns_description}

PRIMARY KEYS: {pk_list}

FOREIGN KEY RELATIONSHIPS:
{fk_relationships}"""
        
        text_chunks.append(text_chunk)

    # 3. Embed the table-level texts
    print("🧠 Generating embeddings...")
    embeddings = embed_texts(text_chunks)
    
    if not embeddings:
        print("❌ No embeddings generated")
        return
        
    if len(embeddings) != len(text_chunks):
        print(f"❌ Embedding count mismatch: {len(text_chunks)} chunks vs {len(embeddings)} embeddings")
        # Continue with available embeddings but log warning
        print(f"⚠️ Proceeding with {min(len(embeddings), len(text_chunks))} embeddings")

    # 4. Build metadata chunks (now table-level)
    print("🔨 Building metadata chunks...")
    meta_chunks = build_meta_chunks_from_metadata(metadata, embeddings)
    print(f"✅ Built {len(meta_chunks)} metadata chunks")

    if not meta_chunks:
        print("❌ No metadata chunks built")
        return

    # 5. Upsert into Pinecone
    print("🚀 Upserting to Pinecone...")
    upsert_metadata(meta_chunks)
    return meta_chunks


