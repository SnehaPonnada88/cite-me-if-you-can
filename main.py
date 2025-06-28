from fastapi import FastAPI
from api.similarity_search import router as search_router
app = FastAPI()
app.include_router(search_router)
