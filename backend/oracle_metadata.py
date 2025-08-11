import oracledb
from db_handler import get_connection,extract_db_metadata  # reuse your existing logic
from embedder import embed_texts
from pinecone_utils import upsert_metadata
import json
def get_metadata_rows():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name, column_name, data_type, nullable
        FROM all_tab_columns
        WHERE owner = 'SYSTEM'
    """)
    return cursor.fetchall()

def format_metadata_rows(rows):
    return [
        f"Table: {table}, Column: {column}, Type: {dtype}, Nullable: {nullable}"
        for table, column, dtype, nullable in rows
    ]


def build_meta_chunks_from_metadata(metadata: dict, embeddings: list[list[float]]) -> list[dict]:
    chunks = []
    i = 0
    for table, table_meta in metadata.items():
        for col in table_meta["columns"]:
            column_name = col["name"]
            fk_ref = next(
                (fk["references"] for fk in table_meta["foreign_keys"] if fk["column"] == column_name),
                None
            )
            fk_info = f"{fk_ref['table']}.{fk_ref['column']}" if fk_ref else "None"

            # Truncate long comments to 200 characters max
            col_comment = (col["comment"] or "")[:200]
            tbl_comment = (table_meta["table_comment"] or "")[:200]

            text_chunk =f"""Table: {table}
                            Column: {column_name}
                            Type: {col['type']}
                            Nullable: {col['nullable']}
                            Column Comment: {col_comment}
                            Table Comment: {tbl_comment}
                            Primary Key: {"Yes" if column_name in table_meta["primary_keys"] else "No"}
                            Foreign Key: {fk_info}"""

            chunks.append({
                "id": f"meta-{table}-{column_name}",
                "text": text_chunk,
                "vector": embeddings[i],
                "metadata": {
                    "table": table,
                    "column": column_name,
                    "type": col["type"],
                    "nullable": col["nullable"],
                    "is_primary_key": column_name in table_meta["primary_keys"],
                    "is_foreign_key": fk_ref is not None,
                    "foreign_key_ref": fk_info  # Now a string, safe
                }
            })
            i += 1
    return chunks

def full_metadata_embedding_pipeline(owner="SYSTEM"):
    # 1. Extract metadata
    metadata = extract_db_metadata(owner=owner)

    # 2. Generate text chunks for embedding
    text_chunks = [
        f"""Table: {table}
            Column: {col['name']}
            Type: {col['type']}
            Nullable: {col['nullable']}
            Column Comment: {col['comment']}
            Table Comment: {table_meta['table_comment']}
            Primary Key: {"Yes" if col['name'] in table_meta['primary_keys'] else "No"}
            Foreign Key: {[
                f"{fk['references']['table']}.{fk['references']['column']}"
                for fk in table_meta["foreign_keys"]
                if fk["column"] == col["name"]
            ] or "No"}
        """
        for table, table_meta in metadata.items()
        for col in table_meta["columns"]
    ]
    # print(text_chunks)
    # 3. Embed the texts
    embeddings = embed_texts(text_chunks)
    # print(embeddings)
    if len(embeddings) != len(text_chunks):
        print("[❌] Embedding count does not match text chunk count")
        return

    # 4. Build metadata chunks
    meta_chunks = build_meta_chunks_from_metadata(metadata, embeddings)

    # 5. Upsert into Pinecone
    upsert_metadata(meta_chunks)
