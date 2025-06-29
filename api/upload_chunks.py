from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import json
import requests
import os
import sys
from tempfile import NamedTemporaryFile

# Add ingestion directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ingestion.ingest_pipeline import IngestionPipeline

router = APIRouter()

@router.put("/api/upload")
async def upload_json_file(
    schema_version: str = Form(...),
    file: UploadFile = File(None),
    file_url: str = Form(None)
):
    if not schema_version:
        raise HTTPException(status_code=400, detail="schema_version is required")

    # Get file contents from upload or URL
    if file:
        contents = await file.read()
    elif file_url:
        response = requests.get(file_url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch file from URL")
        contents = response.content
    else:
        raise HTTPException(status_code=400, detail="Either file or file_url must be provided.")

    # Validate JSON structure
    try:
        data = json.loads(contents.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

    # Save to a temporary file and pass to pipeline
    with NamedTemporaryFile("w+", suffix=".json", delete=False) as temp_file:
        json.dump(data, temp_file)
        temp_file_path = temp_file.name

    # Run ingestion
    pipeline = IngestionPipeline(data_path=temp_file_path)
    pipeline.process_and_store()

    return JSONResponse(
        status_code=202,
        content={"uploaded": len(data), "schema_version": schema_version}
    )
