from fastapi import FastAPI
from api.similarity_search import router as search_router
from api.ask_with_context import router as ask_router
from api.upload_chunks import router as upload_router
app = FastAPI()

# Include both routers
app.include_router(search_router)
app.include_router(ask_router)
app.include_router(upload_router)