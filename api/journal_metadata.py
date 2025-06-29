from fastapi import APIRouter, HTTPException
from qdrant_client import QdrantClient

router = APIRouter()

qdrant = QdrantClient(host="localhost", port=6333)
collection_name = "journal_chunks"

@router.get("/api/{journal_id}")
def get_journal_by_id(journal_id: str):
    try:
        scroll_result, _ = qdrant.scroll(
            collection_name=collection_name,
            scroll_filter={
                "must": [
                    {"key": "source_doc_id", "match": {"value": journal_id}}
                ]
            },
            with_payload=True,
            limit=100  # or increase as needed
        )

        if not scroll_result:
            raise HTTPException(status_code=404, detail="Journal ID not found")

        return {
            "journal_id": journal_id,
            "total_chunks": len(scroll_result),
            "chunks": [point.payload for point in scroll_result]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving journal: {str(e)}")