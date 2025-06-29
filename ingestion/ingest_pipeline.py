import fitz  # PyMuPDF
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from uuid import uuid4

class IngestionPipeline:
    def __init__(self, upload_dir="uploads", collection_name="journal_chunks"):
        self.upload_dir = Path(upload_dir)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection_name = collection_name
        self.vector_size = self.model.get_sentence_embedding_dimension()
        self.qdrant = QdrantClient(host="localhost", port=6333)

        # Create or recreate collection
        self.qdrant.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
        )

    def extract_text(self, pdf_path):
        doc = fitz.open(pdf_path)
        return "\n".join(page.get_text() for page in doc)

    def chunk_text(self, text, max_tokens=300):
        paragraphs = text.split("\n\n")
        chunks = []
        current = ""
        for para in paragraphs:
            if len(current.split()) + len(para.split()) < max_tokens:
                current += " " + para
            else:
                chunks.append(current.strip())
                current = para
        if current:
            chunks.append(current.strip())
        return chunks

    def process_and_store(self):
        all_points = []
        for file in self.upload_dir.glob("*.pdf"):
            print(f"📄 Processing: {file.name}")
            text = self.extract_text(file)
            chunks = self.chunk_text(text)
            embeddings = self.model.encode(chunks)

            for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
                chunk_id = str(uuid4())
                metadata = {
                    "id": chunk_id,
                    "source_doc_id": file.stem,
                    "section_heading": f"Chunk {i+1}",
                    "journal": "Unknown",           # Could later be inferred
                    "publish_year": "2024",         # Default or extracted
                    "usage_count": 0,
                    "attributes": {}
                }
                all_points.append(PointStruct(id=chunk_id, vector=vector.tolist(), payload=metadata))

        if all_points:
            self.qdrant.upsert(collection_name=self.collection_name, points=all_points)
            print(f"✅ Ingested {len(all_points)} chunks into Qdrant collection: {self.collection_name}")
        else:
            print("⚠️ No new files or valid content found.")

if __name__ == "__main__":
    pipeline = IngestionPipeline(upload_dir="uploads")
    pipeline.process_and_store()
