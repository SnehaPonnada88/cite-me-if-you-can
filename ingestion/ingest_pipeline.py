import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams, CollectionStatus
from uuid import uuid4


class IngestionPipeline:
    def __init__(self, data_path, collection_name="journal_chunks"):
        self.data_path = Path(data_path)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection_name = collection_name
        self.vector_size = self.model.get_sentence_embedding_dimension()
        self.qdrant = QdrantClient(host="localhost", port=6333)

        # Create collection (if not exists)
        self.qdrant.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
        )

    def load_chunks(self):
        """Load pre-chunked sample data from JSON file"""
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def process_and_store(self):
        chunks = self.load_chunks()
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.model.encode(texts)

        points = []
        for chunk, vector in zip(chunks, embeddings):
            point_id = str(uuid4())
            metadata = {
                "id": chunk["id"],
                "source_doc_id": chunk["source_doc_id"],
                "section_heading": chunk["section_heading"],
                "journal": chunk["journal"],
                "publish_year": chunk["publish_year"],
                "usage_count": chunk["usage_count"],
                "attributes": chunk["attributes"],
                "link": chunk.get("link", "")
            }

            points.append(PointStruct(id=point_id, vector=vector.tolist(), payload=metadata))

        self.qdrant.upsert(collection_name=self.collection_name, points=points)
        print(f"✅ Ingested {len(points)} chunks into Qdrant collection: {self.collection_name}")


if __name__ == "__main__":
    pipeline = IngestionPipeline(data_path="data/Sample_chunks.json")
    pipeline.process_and_store()
