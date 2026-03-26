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
        # 1. Ensure we have an image
        image_to_process = None
        try:
            image_data = base64.b64decode(file_content)
            if file_name.lower().endswith('.pdf'):
                from pdf2image import convert_from_bytes
                images = convert_from_bytes(image_data)
                if images:
                    buffered = io.BytesIO()
                    images[0].save(buffered, format="JPEG", quality=90)
                    image_to_process = base64.b64encode(buffered.getvalue()).decode("utf-8")
            else:
                image_to_process = file_content
        except Exception as e:
            print(f"Error preparing file: {e}")

        # 2. Inference API
        print(f"DEBUG: HF_TOKEN exists: {self.hf_token is not None}")
        if self.hf_token and image_to_process:
            try:
                import requests
                API_URL = "https://api-inference.huggingface.co/models/impira/layoutlm-document-qa"
                headers = {"Authorization": f"Bearer {self.hf_token}"}
                
                results = {}
                questions = {
                    "strain": "What is the strain name or sample name?",
                    "thc": "What is the total THC percentage?",
                    "cbd": "What is the total CBD percentage?",
                    "lab": "What is the name of the lab?",
                    "date": "What is the test date?"
                }
                
                for key, q in questions.items():
                    payload = {"inputs": {"image": image_to_process, "question": q}}
                    resp = requests.post(API_URL, headers=headers, json=payload).json()
                    print(f"DEBUG: Response for {key}: {resp}")
                    if isinstance(resp, list) and len(resp) > 0:
                        results[key] = resp[0]

                if "strain" in results:
                    strain_name = results["strain"].get("answer", "Unknown Strain")
                    thc_val = 0.0
                    if "thc" in results:
                        try:
                            # Extract number like "22.5" from "22.5%"
                            val_str = "".join(c for c in results["thc"]["answer"] if c.isdigit() or c == ".")
                            thc_val = float(val_str)
                        except: pass

                    print(f"AI Success: {strain_name} - THC: {thc_val}%")
                    return LabReportData(
                        strain_name=strain_name,
                        lab_name=results.get("lab", {}).get("answer"),
                        test_date=results.get("date", {}).get("answer"),
                        cannabinoids=[
                            Cannabinoid(name="Total THC", value=thc_val),
                            Cannabinoid(name="Total CBD", value=0.0) # simplify for now
                        ],
                        file_name=file_name,
                        confidence=results["strain"].get("score", 0.0),
                        source_type="ai_real"
                    )
            except Exception as e:
                print(f"AI Extraction failed: {e}")

        return self._mock_extraction(file_name)

    def _mock_extraction(self, file_name: str) -> LabReportData:
        # This mocks the data format we expect from a successful extraction
        return LabReportData(
            strain_name="Blue Dream",
            strain_type="Sativa-dominant",
            dominance="60% Sativa",
            lab_name="GSI Labs",
            producer="Pacific Green",
            batch="BD-2024-001",
            lot_number="L-8829",
            sample_id="SAMPLE-X",
            test_date="2024-03-24",
            origin="California, USA",
            genetics="Blueberry x Haze",
            cannabinoids=[
                Cannabinoid(name="THC", value=22.5, unit="%", display_label="High Potency"),
                Cannabinoid(name="THCA", value=19.2, unit="%"),
                Cannabinoid(name="Total THC", value=18.5, unit="%"),
                Cannabinoid(name="CBD", value=0.1, unit="%"),
                Cannabinoid(name="CBG", value=1.2, unit="%")
            ],
            terpenes=[
                Terpene(name="Myrcene", value=0.85, unit="%", display_effects=["Relaxing", "Sedating"]),
                Terpene(name="Pinene", value=0.45, unit="%"),
                Terpene(name="Caryophyllene", value=0.32, unit="%")
            ],
            confidence=0.95,
            source_type="mock",
            file_name=file_name
        )

    async def normalize(self, data: Dict[str, Any]) -> LabReportData:
        return LabReportData(**data)
