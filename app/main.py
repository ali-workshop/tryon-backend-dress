import os
import uuid
import shutil
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from app.tryon import run_tryon
import base64
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
origins = [
    "http://localhost:3000",  # your frontend origin
    "https://try-cloth-on.sophitica.ai" ,  # add production frontend if needed
    "https://virtual-try-on.majdoleen-irq.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Allowed origins
    allow_credentials=True,
    allow_methods=["*"],            # Allow GET, POST, etc.
    allow_headers=["*"],            # Allow all headers
)
@app.post("/tryon/dress")
async def tryon(model_image: UploadFile = File(...), garment_image: UploadFile = File(...)):
    # Create temp filenames
    model_path = f"/tmp/{uuid.uuid4()}_{model_image.filename}"
    garment_path = f"/tmp/{uuid.uuid4()}_{garment_image.filename}"

    # Save uploaded files temporarily
    with open(model_path, "wb") as f:
        shutil.copyfileobj(model_image.file, f)

    with open(garment_path, "wb") as f:
        shutil.copyfileobj(garment_image.file, f)

    try:
        # Run try-on logic
        result_bytes = run_tryon(model_path, garment_path)

        # Convert to base64 for frontend
        result_base64 = base64.b64encode(result_bytes).decode("utf-8")

        return {
            "success": True,
            "image_base64": result_base64
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
    finally:
        # Cleanup temp files
        if os.path.exists(model_path):
            os.remove(model_path)
        if os.path.exists(garment_path):
            os.remove(garment_path)
