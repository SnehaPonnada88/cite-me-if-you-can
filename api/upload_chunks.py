from fastapi import APIRouter, File, UploadFile, HTTPException
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
import uuid
import json

router = APIRouter()
model = SentenceTransformer("all-MiniLM-L6-v2")
qdrant = QdrantClient(host="localhost", port=6333)
collection_name = "journal_chunks"
vector_size = 384

# Optional: create collection if it doesn't exist
if not qdrant.collection_exists(collection_name):
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )

@router.post("/api/upload")
async def upload_json_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are allowed.")

    contents = await file.read()
    try:
        chunks = json.loads(contents)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file.")

    points = []
    for chunk in chunks:
        vector = model.encode(chunk["text"]).tolist()
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=chunk  # Payload contains all metadata (journal, section, etc.)
            )
        )

    qdrant.upsert(collection_name=collection_name, points=points)

    return {"status": "success", "uploaded": len(points)}
