from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from models import ExtractionRequest, GenerationRequest, LabReportData
from services.parser import LabReportParser
from services.renderer import VisualRenderer
import io
import base64
from PIL import Image

app = FastAPI(title="StrainAI Backend API")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = LabReportParser()
renderer = VisualRenderer()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        b64_content = base64.b64encode(contents)
        data = await parser.extract_data(b64_content, file.filename)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-preview")
async def generate_preview(data: LabReportData):
    try:
        img = renderer.generate_dashboard(data)
        
        # Convert image to base64 for preview
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return {"image_data": img_str}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For direct file upload if needed
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Read file, convert to base64, call extract
    contents = await file.read()
    b64_content = base64.b64encode(contents)
    # logic similar to extract
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
