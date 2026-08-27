from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class ValuationRequest(BaseModel):
    storage_path: str
    condition: Optional[str] = None

class ProductInfo(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    variant: Optional[str] = None
    category: Optional[str] = None
    gtin: Optional[str] = None
    condition: Optional[str] = None

class AIProductIdentification(BaseModel):
    brand: Optional[str] = Field(None, description="Marca del producto (ej. Apple, Nike).")
    model: Optional[str] = Field(None, description="Modelo específico (ej. iPhone 15, Air Jordan 1).")
    variant: Optional[str] = Field(None, description="Variante, color o capacidad (ej. 128GB, Space Gray).")
    category: Optional[str] = Field(None, description="Categoría general para clasificación.")
    color: Optional[str] = Field(None, description="Color principal dominante.")
    gtin: Optional[str] = Field(None, description="Código de barras EAN/UPC. NUNCA lo inventes. Devuelve null si no se ve claramente.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Nivel de confianza en la identificación, entre 0.0 y 1.0.")
    search_query: str = Field(..., description="Query optimizada de 3-5 palabras para buscar este producto en eBay.")


class MarketData(BaseModel):
    search_query: str
    comps_found: int = Field(ge=0)

    p25: Optional[float] = None
    median: Optional[float] = None
    p75: Optional[float] = None

    currency: str = "EUR"

class ValuationResult(BaseModel):
    quick_sale: Optional[float] = None
    recommended: Optional[float] = None
    maximum: Optional[float] = None
    currency: str = "EUR"
    confidence: str

class ValuationResponse(BaseModel):
    valuation_id: str
    status: str
    product: Optional[ProductInfo] = None
    market_data: Optional[MarketData] = None
    valuation: Optional[ValuationResult] = None
    created_at: datetime
