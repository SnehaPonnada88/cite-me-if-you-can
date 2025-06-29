from fastapi import FastAPI
from api.similarity_search import router as search_router
from api.ask_with_context import router as ask_router
from api.upload_chunks import router as upload_router
from api.usage_count import router as usage_router
from api.journal_metadata import router as journal_router
app = FastAPI()

# Include both routers
app.include_router(search_router)
app.include_router(ask_router)
app.include_router(upload_router)
app.include_router(usage_router)
app.include_router(journal_router)