import base64
import json
import io
import os
from PIL import Image
from typing import Dict, Any, List, Optional
# Heavy imports deferred
HAS_TRANSFORMERS = True # Assume true, check internally

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    print("Warning: google-generativeai not found.")

from models import LabReportData, Cannabinoid, Terpene

class LabReportParser:
    def __init__(self, use_remote_api: bool = False, hf_token: Optional[str] = None):
        self.use_remote_api = use_remote_api
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        self.gemini_token = os.getenv("GEMINI_API_KEY") # NEW
        
        if HAS_GEMINI and self.gemini_token:
            genai.configure(api_key=self.gemini_token)
            self.gemini_model = genai.GenerativeModel('gemini-flash-latest')
            print("INFO: Gemini 1.5 Flash Parser Initialized!")

    async def extract_data(self, file_content: str, file_name: str) -> LabReportData:
        # OPTION 1: Gemini (Superior)
        if HAS_GEMINI and self.gemini_token:
            try:
                extraction = await self._gemini_extraction(file_content, file_name)
                if extraction and extraction.strain_name:
                    return extraction
            except Exception as e:
                print(f"Gemini Extraction Failed (falling back): {e}")

        # OPTION 2: Legacy OCR + Regex (Fallback)
        return await self._legacy_extraction(file_content, file_name)

    async def _gemini_extraction(self, file_content: str, file_name: str) -> LabReportData:
        import google.generativeai as genai
        # Format for Gemini API (mime_type + data)
        mime_type = "application/pdf" if file_name.lower().endswith('.pdf') else "image/jpeg"
        # If it's B64 string, keep it as is. If it's a file path, we'd need to read it.
        # file_content here is base64 string from frontend
        
        prompt = """
        You are an expert in cannabis lab reports (COAs). 
        Extract the following information from this lab report and return it as a VALID JSON object matching this structure:
        {
          "strain_name": "Name of the cannabis strain",
          "strain_type": "Indica, Sativa, or Hybrid",
          "dominance": "e.g., Indica-dominant",
          "lab_name": "Name of the testing lab",
          "producer": "Company that grew/produced it",
          "batch": "Batch number",
          "lot_number": "Lot ID",
          "sample_id": "Sample ID",
          "test_date": "YYYY-MM-DD",
          "origin": "Country or State",
          "genetics": "Lineage if mentioned",
          "cannabinoids": [
            {"name": "THC", "value": 24.5, "unit": "%"},
            {"name": "CBD", "value": 0.1, "unit": "%"}
          ],
          "terpenes": [
            {"name": "Myrcene", "value": 1.2, "unit": "%"},
            {"name": "Limonene", "value": 0.8, "unit": "%"}
          ],
          "confidence": 0.95
        }
        Return ONLY the raw JSON object. If you don't find a value, use null or omit. Be precise with THC, CBD and specific terpenes.
        """
        
        # Part for Gemini
        try:
            image_data = base64.b64decode(file_content)
            
            # Try multiple model names if one fails
            models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-2.0-flash', 'gemini-pro']
            response = None
            last_error = ""

            for model_name in models_to_try:
                try:
                    current_model = genai.GenerativeModel(model_name)
                    response = current_model.generate_content([
                        prompt,
                        {
                            "mime_type": mime_type,
                            "data": image_data
                        }
                    ])
                    if response: break
                except Exception as e:
                    last_error = str(e)
                    continue
            
            if not response:
                print(f"DEBUG: All Gemini models failed. Last error: {last_error}")
                return None

            # Extract JSON from response
            text = response.text
            # Robust JSON extraction
            json_str = ""
            if "{" in text and "}" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                json_str = text[start:end]
            
            if not json_str:
                return None

            data = json.loads(json_str)
            
            # Safety check for strain_name
            if not data.get("strain_name") or data["strain_name"] == "null":
                data["strain_name"] = file_name.split(".")[0].replace("_", " ").replace("-", " ").title()
            
            data["file_name"] = file_name
            data["source_type"] = f"gemini_api"
            
            # Ensure cannabinoids and terpenes are lists
            if not isinstance(data.get("cannabinoids"), list): data["cannabinoids"] = []
            if not isinstance(data.get("terpenes"), list): data["terpenes"] = []

            return LabReportData(**data)
        except Exception as e:
            print(f"DEBUG: Gemini Processing Error: {e}")
            return None

    async def _legacy_extraction(self, file_content: str, file_name: str) -> LabReportData:
        # Move all current logic here as fallback
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
                    for img in images[:2]:
                        raw_text += pytesseract.image_to_string(img)
            else:
                pil_image = Image.open(io.BytesIO(image_data))
                raw_text = pytesseract.image_to_string(pil_image)

            if pil_image:
                buffered = io.BytesIO()
                pil_image.save(buffered, format="JPEG", quality=95)
                image_to_process_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        except Exception as e:
            print(f"Legacy OCR Error: {e}")

        import re
        thc_val = 0.0
        cbd_val = 0.0
        thc_match = re.search(r'(?:Total\s*THC|THC\s*Total|Potency)[:\s]*([\d\.]+)', raw_text, re.I)
        if thc_match:
            try: thc_val = float(thc_match.group(1))
            except: pass
        cbd_match = re.search(r'(?:Total\s*CBD|CBD\s*Total)[:\s]*([\d\.]+)', raw_text, re.I)
        if cbd_match:
            try: cbd_val = float(cbd_match.group(1))
            except: pass

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

        return LabReportData(
            strain_name=strain_name,
            cannabinoids=[
                Cannabinoid(name="Total THC", value=thc_val, unit="%"),
                Cannabinoid(name="Total CBD", value=cbd_val, unit="%")
            ],
            file_name=file_name,
            confidence=0.8 if thc_val > 0 else 0.5,
            source_type="ai_legacy_fallback"
        )

    def _empty_extraction(self, file_name: str) -> LabReportData:
        return LabReportData(
            strain_name=file_name.split(".")[0].title(),
            cannabinoids=[Cannabinoid(name="Total THC", value=0.0)],
            confidence=0.0,
            file_name=file_name,
            source_type="error"
        )

    async def normalize(self, data: Dict[str, Any]) -> LabReportData:
        return LabReportData(**data)
