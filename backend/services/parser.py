import base64
import json
import io
import os
from PIL import Image
from typing import Dict, Any, List, Optional
try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("Warning: transformers not found. Using mock extraction.")
from models import LabReportData, Cannabinoid, Terpene

# Simulation of Hugging Face pipeline for document understanding
# In reality, this would use: pipeline("document-question-answering", model="impira/layoutlm-document-qa")
# Or a multimodal model like Donut: model="naver-clova-ix/donut-base-finetuned-docvqa"

class LabReportParser:
    def __init__(self, use_remote_api: bool = False, hf_token: Optional[str] = None):
        self.use_remote_api = use_remote_api
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        
    async def extract_data(self, file_content: str, file_name: str) -> LabReportData:
        # 1. Prepare Images and OCR Text
        raw_text = ""
        image_to_process_b64 = None
        pil_image = None
        try:
            import pytesseract
            image_data = base64.b64decode(file_content)
            if file_name.lower().endswith('.pdf'):
                from pdf2image import convert_from_bytes
                images = convert_from_bytes(image_data)
                if images:
                    pil_image = images[0]
                    # Also extract text from all pages to be safe
                    for img in images[:2]: # First 2 pages
                        raw_text += pytesseract.image_to_string(img)
            else:
                pil_image = Image.open(io.BytesIO(image_data))
                raw_text = pytesseract.image_to_string(pil_image)

            if pil_image:
                buffered = io.BytesIO()
                pil_image.save(buffered, format="JPEG", quality=95)
                image_to_process_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        except Exception as e:
            print(f"OCR/Image Pre-processing Error: {e}")

        # 2. Extract Using RegEx (Fast & Reliable for Numbers)
        import re
        thc_val = 0.0
        cbd_val = 0.0
        
        # Look for THC/CBD patterns
        thc_match = re.search(r'(?:Total\s*THC|THC\s*Total|Potency)[:\s]*([\d\.]+)', raw_text, re.I)
        if thc_match:
            try: thc_val = float(thc_match.group(1))
            except: pass
            
        cbd_match = re.search(r'(?:Total\s*CBD|CBD\s*Total)[:\s]*([\d\.]+)', raw_text, re.I)
        if cbd_match:
            try: cbd_val = float(cbd_match.group(1))
            except: pass

        # 3. Use Inference API for Naming (Context is better there)
        strain_name = file_name.replace(".pdf", "").replace(".png", "").replace(".jpg", "").title()
        if self.hf_token and image_to_process_b64:
            try:
                import requests
                API_URL = "https://api-inference.huggingface.co/models/impira/layoutlm-document-qa"
                headers = {"Authorization": f"Bearer {self.hf_token}"}
                payload = {"inputs": {"image": image_to_process_b64, "question": "What is the strain name?"}}
                resp = requests.post(API_URL, headers=headers, json=payload).json()
                if isinstance(resp, list) and len(resp) > 0:
                    answer = resp[0].get("answer", "").title()
                    if len(answer) > 2 and "unknown" not in answer.lower():
                        strain_name = answer
            except: pass

        # 4. Final Data Assembly
        print(f"DEBUG: OCR Extraction - THC: {thc_val}%, Name: {strain_name}")
        
        # If OCR got data, or we use a smart fallback
        return LabReportData(
            strain_name=strain_name,
            strain_type="Hybrid", # default
            cannabinoids=[
                Cannabinoid(name="Total THC", value=thc_val, unit="%"),
                Cannabinoid(name="Total CBD", value=cbd_val, unit="%")
            ],
            terpenes=[],
            file_name=file_name,
            confidence=0.8 if thc_val > 0 else 0.5,
            source_type="ai_hybrid"
        )

    def _empty_extraction(self, file_name: str) -> LabReportData:
        # Not needed anymore as extract_data is now more robust, but kept for compatibility
        return LabReportData(
            strain_name=file_name.split(".")[0].title(),
            cannabinoids=[Cannabinoid(name="Total THC", value=0.0)],
            confidence=0.0,
            file_name=file_name,
            source_type="error"
        )

    async def normalize(self, data: Dict[str, Any]) -> LabReportData:
        return LabReportData(**data)
