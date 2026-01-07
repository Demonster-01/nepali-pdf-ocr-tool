import os
import shutil
import uuid
import asyncio
from typing import Dict, Optional
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Import our OCR logic
import pdf_ocr

app = FastAPI(title="Nepali PDF OCR API")

# Setup directories
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# In-memory store for task status
tasks: Dict[str, dict] = {}

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: int
    total_pages: int
    result_url: Optional[str] = None
    sample_text: Optional[list] = None

def ocr_progress_sync(task_id: str, current: int, total: int, status: str, sample: list = None):
    """Sync callback for OCR progress updates"""
    tasks[task_id].update({
        "progress": current,
        "total_pages": total,
        "status": status
    })
    if sample:
        tasks[task_id]["sample_text"] = sample

def run_ocr_task(task_id: str, input_path: str, output_path: str, mode: str):
    """Background task runner for OCR"""
    try:
        tasks[task_id]["status"] = "processing"
        
        dpi_map = {'fast': 150, 'balanced': 200, 'accurate': 300}
        dpi = dpi_map.get(mode, 200)

        # Run the OCR with callback that includes sample text
        result = pdf_ocr.process_pdf(
            input_path, 
            output_path, 
            dpi=dpi, 
            progress_callback=lambda c, t, s, samp=None: ocr_progress_sync(task_id, c, t, s, samp)
        )
        
        if result:
            tasks[task_id].update({
                "status": "completed",
                "progress": result["page_count"],
                "total_pages": result["page_count"],
                "result_url": f"/download/{task_id}",
                "sample_text": result["sample_text"]
            })
        else:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = "OCR failed to produce results"
            
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

@app.post("/upload")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...), mode: str = "balanced"):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    task_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{task_id}.pdf")
    output_path = os.path.join(OUTPUT_DIR, f"{task_id}_ocr.pdf")
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    tasks[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "progress": 0,
        "total_pages": 0,
        "filename": file.filename
    }
    
    background_tasks.add_task(run_ocr_task, task_id, input_path, output_path, mode)
    
    return {"task_id": task_id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.get("/download/{task_id}")
async def download_file(task_id: str):
    output_path = os.path.join(OUTPUT_DIR, f"{task_id}_ocr.pdf")
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Result file not found")
    
    filename = tasks[task_id].get("filename", "processed.pdf")
    if not filename.endswith(".pdf"):
        filename += "_ocr.pdf"
    else:
        filename = filename[:-4] + "_ocr.pdf"
        
    return FileResponse(output_path, media_type="application/pdf", filename=filename)

# Mount static files (will create this next)
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
