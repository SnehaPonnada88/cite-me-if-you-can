from fastapi import APIRouter
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, SearchRequest

# Setup
router = APIRouter()
model = SentenceTransformer("all-MiniLM-L6-v2")
qdrant = QdrantClient(host="localhost", port=6333)
collection_name = "journal_chunks"

# Request schema
class SearchQuery(BaseModel):
    query: str
    k: int = 5
    min_score: float = 0.25  # Optional filtering


@router.post("/api/similarity_search")
def similarity_search(payload: SearchQuery):
    vector = model.encode(payload.query).tolist()

    results = qdrant.search(
        collection_name=collection_name,
        query_vector=vector,
        limit=payload.k,
        with_payload=True
    )

    output = []
    for r in results:
        if r.score >= payload.min_score:
            output.append({
                "score": r.score,
                "text": r.payload.get("text"),
                "source": r.payload.get("source_doc_id"),
                "section": r.payload.get("section_heading"),
                "journal": r.payload.get("journal"),
                "year": r.payload.get("publish_year")
            })

    return {"query": payload.query, "results": output}
