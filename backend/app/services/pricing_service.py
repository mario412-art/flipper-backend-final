from typing import List, Tuple
from app.models.schemas import MarketData, ValuationResult, AIProductIdentification

from typing import List, Tuple
from app.models.schemas import MarketData, ValuationResult, AIProductIdentification

class PricingService:
    def _clean_data(self, items: List[dict]) -> List[dict]:
        """Paso 1: Limpieza básica de formato de datos (precios nulos, errores)"""
        cleaned = []
        for item in items:
            try:
                # El mock trae price como string ("419.00"). En un API real, dependerá.
                price_val = item.get("price", {}).get("value", 0)
                price = float(price_val)
                if price <= 0:
                    continue
                
                cleaned.append({
                    "external_id": item.get("itemId", ""),
                    "title": item.get("title", "").lower(),
                    "price": price,
                    "currency": item.get("price", {}).get("currency", "EUR"),
                    "condition": item.get("condition", "").lower()
                })
            except (ValueError, TypeError):
                continue
        return cleaned

    def _match_similarity(self, comp: dict, product_info: AIProductIdentification) -> float:
        """Paso 2: Matching de similitud basado en el título del comparable"""
        title = comp["title"]
        score = 1.0

        # Palabras negativas estrictas (Descartar instantáneo)
        negatives = ["caja", "box only", "funda", "case", "repuestos", "piezas", "parts", 
                     "roto", "broken", "desguace", "solo", "empty", "cargador", "pantalla rota"]
        for kw in negatives:
            if kw in title:
                return 0.0 # Similitud cero, se descartará

        # Si el modelo tiene la variante detectada (ej "Pro Max"), el comparable también debería tenerla
        if product_info.variant:
            variant_lower = product_info.variant.lower()
            if variant_lower not in title and len(variant_lower) > 3:
                score -= 0.5 # Penalizar fuertemente si es otra variante
                
        # Detectar variantes incompatibles (Si yo NO tengo Pro Max, pero el anuncio sí)
        incompatible_variants = ["pro max", "pro", "plus", "ultra"]
        my_variant = (product_info.variant or "").lower()
        my_model = (product_info.model or "").lower()
        
        for inc in incompatible_variants:
            if inc in title and inc not in my_variant and inc not in my_model:
                score -= 0.8 # Es casi seguro que es otro producto superior
        
        return max(0.0, score)

    def _filter_comps(self, comps: List[dict], product_info: AIProductIdentification) -> List[dict]:
        """Paso 3: Filtrar comparables aplicando el score de matching"""
        filtered = []
        for comp in comps:
            score = self._match_similarity(comp, product_info)
            if score >= 0.5: # Umbral de aceptación
                filtered.append(comp)
        return filtered

    def _remove_outliers(self, prices: List[float]) -> List[float]:
        """Paso 4: Eliminar valores atípicos (outliers) extremos por IQR o heurística básica"""
        if len(prices) < 4:
            return prices # Demasiado pocos para quitar outliers estadísticos
            
        prices.sort()
        q1 = prices[len(prices) // 4]
        q3 = prices[(len(prices) * 3) // 4]
        iqr = q3 - q1
        
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)
        
        return [p for p in prices if lower_bound <= p <= upper_bound]

    def _calculate_statistics(self, prices: List[float]) -> dict:
        """Paso 5: Estadísticas finales"""
        if not prices:
            return {"p25": 0, "median": 0, "p75": 0}
            
        prices.sort()
        n = len(prices)
        p25 = prices[n // 4]
        median = prices[n // 2]
        p75 = prices[(n * 3) // 4]
        
        return {"p25": p25, "median": median, "p75": p75}

    def calculate_valuation(self, search_query: str, items: List[dict], product_info: AIProductIdentification) -> Tuple[MarketData, ValuationResult]:
        """Paso 6: Valoración final y orquestación"""
        
        # Flujo estricto: Limpieza -> Matching -> Filtrado -> Outliers -> Estadísticas
        cleaned = self._clean_data(items)
        filtered = self._filter_comps(cleaned, product_info)
        
        raw_prices = [c["price"] for c in filtered]
        valid_prices = self._remove_outliers(raw_prices)
        
        stats = self._calculate_statistics(valid_prices)
        
        comps_found = len(valid_prices)
        median = stats["median"]
        p25 = stats["p25"]
        p75 = stats["p75"]
        
        quick_sale = round(median * 0.85, 2) if median > 0 else 0.0
        recommended = round(median, 2)
        maximum = round(p75, 2)
        
        confidence_str = "high" if comps_found >= 5 else ("medium" if comps_found >= 2 else "low")

        market_data = MarketData(
            search_query=search_query,
            comps_found=comps_found,
            p25=round(p25, 2) if p25 else None,
            median=round(median, 2) if median else None,
            p75=round(p75, 2) if p75 else None,
            currency="EUR"
        )

        valuation_result = ValuationResult(
            quick_sale=quick_sale if quick_sale else None,
            recommended=recommended if recommended else None,
            maximum=maximum if maximum else None,
            currency="EUR",
            confidence=confidence_str
        )

        return market_data, valuation_result

pricing_service = PricingService()
