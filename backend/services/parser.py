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
        # 1. Ensure we have an image even if it's a PDF
        image_to_process = None
        try:
            image_data = base64.b64decode(file_content)
            if file_name.lower().endswith('.pdf'):
                from pdf2image import convert_from_bytes
                images = convert_from_bytes(image_data)
                if images:
                    # Use the first page for extraction
                    buffered = io.BytesIO()
                    images[0].save(buffered, format="JPEG")
                    image_to_process = base64.b64encode(buffered.getvalue()).decode("utf-8")
            else:
                image_to_process = file_content # Already an image
        except Exception as e:
            print(f"Error preparing file for extraction: {e}")

        # 2. Use the Inference API for real extraction
        if self.hf_token and image_to_process:
            try:
                import requests
                API_URL = "https://api-inference.huggingface.co/models/impira/layoutlm-document-qa"
                headers = {"Authorization": f"Bearer {self.hf_token}"}
                
                def query(question):
                    payload = {
                        "inputs": {
                            "image": image_to_process,
                            "question": question
                        }
                    }
                    response = requests.post(API_URL, headers=headers, json=payload)
                    return response.json()

                # Attempt real extractions
                strain_resp = query("What is the strain name?")
                thc_resp = query("What is the Total THC percentage?")
                cbd_resp = query("What is the Total CBD percentage?")
                
                # If we get credible answers, we build a real object
                if isinstance(strain_resp, list) and len(strain_resp) > 0:
                    real_strain = strain_resp[0].get("answer", "Blue Dream")
                    real_thc = 0.0
                    if isinstance(thc_resp, list) and len(thc_resp) > 0:
                        try:
                            # Clean "22.5%" -> 22.5
                            thc_str = thc_resp[0].get("answer", "0").replace("%", "").strip()
                            real_thc = float(thc_str)
                        except: pass

                    return LabReportData(
                        strain_name=real_strain,
                        cannabinoids=[Cannabinoid(name="Total THC", value=real_thc)],
                        file_name=file_name,
                        confidence=strain_resp[0].get("score", 0.0),
                        source_type="api"
                    )
            except Exception as e:
                print(f"Inference API failed, falling back to mock: {e}")

        # Fallback to mock
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
