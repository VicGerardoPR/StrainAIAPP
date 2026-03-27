from pydantic import BaseModel, Field
from typing import List, Optional

class Cannabinoid(BaseModel):
    name: str
    value: float
    unit: str = "%"
    display_label: Optional[str] = None

class Terpene(BaseModel):
    name: str
    value: float
    unit: str = "%"
    display_effects: Optional[List[str]] = None

class LabReportData(BaseModel):
    strain_name: str = Field("Unknown Strain", description="Name of the cannabis strain")
    strain_type: Optional[str] = Field(None, description="Indica, Sativa, or Hybrid")
    dominance: Optional[str] = Field(None, description="e.g., Indica-dominant")
    lab_name: Optional[str] = None
    producer: Optional[str] = None
    batch: Optional[str] = None
    lot_number: Optional[str] = None
    sample_id: Optional[str] = None
    test_date: Optional[str] = None
    origin: Optional[str] = None
    genetics: Optional[str] = None
    cannabinoids: List[Cannabinoid] = []
    terpenes: List[Terpene] = []
    confidence: float = 0.0
    source_type: str = "unknown"
    file_name: str = ""

class ExtractionRequest(BaseModel):
    file_content: str  # Base64 encoded file content
    file_name: str
    content_type: str

class GenerationRequest(BaseModel):
    data: LabReportData
    width: Optional[int] = 1920
    height: Optional[int] = 1080
