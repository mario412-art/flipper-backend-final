import uuid
import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import (
    ValuationRequest, 
    ValuationResponse, 
    ProductInfo, 
    MarketData, 
    ValuationResult
)
from app.api.dependencies import get_current_user
from app.core.config import settings
from app.services.ai_service import ai_service
from app.services.market_data.mock_provider import MockMarketProvider
from app.services.pricing_service import pricing_service
from app.services.storage_service import storage_service

router = APIRouter()

@router.post("/", response_model=ValuationResponse)
async def create_valuation(
    request: ValuationRequest,
    user_id: str = Depends(get_current_user)
):
    try:
        # TAREA 3: STORAGE SEGURO (El backend verifica que el archivo pertenece al usuario)
        if not request.storage_path.startswith(f"users/{user_id}/"):
            raise HTTPException(
                status_code=403, 
                detail="Acceso denegado: El archivo no te pertenece."
            )

        # 1. DESCARGA DE SUPABASE STORAGE
        try:
            image_bytes = storage_service.download_image(request.storage_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        # 2. IA (GEMINI)
        # Identifica el producto y extrae la marca, modelo y la query optimizada usando Structured Outputs.
        product_info = await ai_service.identify_product(image_bytes)
        
        # 3. MERCADO (PROVEEDOR DESACOPLADO)
        if settings.MARKET_DATA_PROVIDER == "ebay":
            from app.services.market_data.ebay_provider import EbayMarketProvider
            market_provider = EbayMarketProvider()
        else:
            market_provider = MockMarketProvider()
            
        search_query = product_info.search_query or f"{product_info.brand} {product_info.model}"
        
        try:
            market_results = await market_provider.search_comps(search_query, limit=20)
        except Exception as provider_error:
            # TAREA 8: No inventar datos si el proveedor falla, devolver 503 Market Unavailable.
            raise HTTPException(status_code=503, detail=str(provider_error))
        
        # 4. MOTOR DE PRECIOS (PRICING ENGINE)
        items = market_results.get("itemSummaries", [])
        market_data, valuation_result = pricing_service.calculate_valuation(search_query, items, product_info)

        valuation_id = str(uuid.uuid4())
        
        # 5. GUARDAR HISTORIAL EN SUPABASE POSTGRESQL (FASE 12)
        try:
            if storage_service.client:
                db_payload = {
                    "id": valuation_id,
                    "user_id": user_id,
                    "brand": product_info.brand,
                    "model": product_info.model,
                    "variant": product_info.variant,
                    "category": product_info.category,
                    "recommended_price": valuation_result.recommended,
                    "quick_sale_price": valuation_result.quick_sale,
                    "comps_found": market_data.comps_found,
                    "image_path": request.storage_path
                }
                storage_service.client.table("valuations_history").insert(db_payload).execute()
        except Exception as db_err:
            # Capturamos el error silenciosamente para no bloquearle la tasación al usuario
            print(f"AVISO: Fallo al guardar en la base de datos: {db_err}".encode("utf-8", errors="ignore").decode("utf-8"))

        return ValuationResponse(
            valuation_id=valuation_id,
            status="completed",
            product=ProductInfo(
                brand=product_info.brand,
                model=product_info.model,
                variant=product_info.variant,
                category=product_info.category,
                gtin=product_info.gtin,
                condition=request.condition or "usado",
            ),
            market_data=market_data,
            valuation=valuation_result,
            created_at=datetime.now(timezone.utc),
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("ERROR:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
