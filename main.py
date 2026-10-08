from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
import logging
from utils.ocr import extract_details
from utils.classify import is_aadhar_image

app = FastAPI()

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/jpg"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPG/JPEG images are allowed"
        )
    
    # Create a safe filename (handle special characters)
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._- ").rstrip()
    file_location = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        # Save uploaded file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Check if it's Aadhaar
        is_aadhar = is_aadhar_image(file_location)
        result = {"is_aadhar": is_aadhar, "details": {}}
        
        # Only extract details if it's Aadhaar
        if is_aadhar:
            result["details"] = extract_details(file_location)
            
        return result
    
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_location):
            os.remove(file_location)

@app.get("/debug_ocr")
async def debug_ocr(image_path: str):
    return extract_details(image_path)