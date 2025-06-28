from fastapi import APIRouter
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

router = APIRouter()
model = SentenceTransformer("all-MiniLM-L6-v2")
qdrant = QdrantClient(host="localhost", port=6333)
collection_name = "journal_chunks"

openai = OpenAI(api_key=OPENAI_API_KEY)

class AskRequest(BaseModel):
    question: str
    k: int = 3

@router.post("/api/ask_with_context")
def ask_with_context(payload: AskRequest):
    vector = model.encode(payload.question).tolist()

    results = qdrant.search(
        collection_name=collection_name,
        query_vector=vector,
        limit=payload.k,
        with_payload=True
    )

    chunks = []
    citations = []

    for r in results:
        content = r.payload.get("text", "")
        meta = f"[{r.payload.get('journal', 'unknown')} - {r.payload.get('section_heading', '')}]"
        chunks.append(f"{content}\n{meta}")
        citations.append(meta)

    context = "\n\n".join(chunks)

    prompt = f"""You are a scientific research assistant.
Answer the question below using the provided context. Include citations in [brackets].

Question: {payload.question}

Context:
{context}

Answer:"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "question": payload.question,
        "citations": citations,
        "answer": response.choices[0].message.content
    }
