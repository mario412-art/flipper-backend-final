import hashlib
from .base import MarketDataProvider

class MockMarketProvider(MarketDataProvider):
    """
    Proveedor de mercado simulado. DETERMINISTA.
    Genera datos dinámicos relativos a un precio base calculado a partir de un hash de la query,
    para que la misma búsqueda SIEMPRE devuelva exactamente el mismo precio base.
    """
    async def search_comps(self, query: str, limit: int = 15) -> dict:
        # Generar un precio base determinista basado en la query (ej. entre 40 y 250)
        hash_val = int(hashlib.md5(query.encode('utf-8')).hexdigest(), 16)
        bp = 40 + (hash_val % 210)
        
        return {
            "itemSummaries": [
                # 1. Producto exacto (Ideal)
                {"itemId": "mock_001", "title": f"{query} en excelente estado", "price": {"value": str(bp), "currency": "EUR"}, "condition": "Usado"},
                {"itemId": "mock_002", "title": f"{query} casi nuevo", "price": {"value": str(bp - 15), "currency": "EUR"}, "condition": "Usado"},
                {"itemId": "mock_003", "title": f"{query} con garantía", "price": {"value": str(bp + 10), "currency": "EUR"}, "condition": "Reacondicionado"},
                
                # 2. Variante diferente (El engine debería ignorarlo o ponderarlo distinto)
                {"itemId": "mock_004", "title": f"{query} Pro Max Premium", "price": {"value": str(bp * 1.8), "currency": "EUR"}, "condition": "Usado"},
                {"itemId": "mock_005", "title": f"{query} Plus", "price": {"value": str(bp * 1.4), "currency": "EUR"}, "condition": "Usado"},
                
                # 3. Accesorios (Debería ser filtrado)
                {"itemId": "mock_006", "title": f"Funda silicona para {query}", "price": {"value": "15.00", "currency": "EUR"}, "condition": "Nuevo"},
                {"itemId": "mock_007", "title": f"Case transparente {query}", "price": {"value": "9.99", "currency": "EUR"}, "condition": "Nuevo"},
                {"itemId": "mock_008", "title": f"Cargador original compatible con {query}", "price": {"value": "25.00", "currency": "EUR"}, "condition": "Usado"},
                
                # 4. Producto roto / para piezas (Debería ser filtrado o penalizado fuertemente)
                {"itemId": "mock_009", "title": f"{query} para piezas no enciende", "price": {"value": str(round(bp * 0.2, 2)), "currency": "EUR"}, "condition": "Para desguace"},
                {"itemId": "mock_010", "title": f"{query} pantalla rota leer descripcion", "price": {"value": str(round(bp * 0.35, 2)), "currency": "EUR"}, "condition": "Usado"},
                
                # 5. Producto incompleto / Solo caja (Debería ser filtrado)
                {"itemId": "mock_011", "title": f"Solo caja original de {query} box only", "price": {"value": "12.00", "currency": "EUR"}, "condition": "Usado"},
                
                # 6. Outliers absolutos (Para probar percentiles)
                {"itemId": "mock_012", "title": f"{query} (Error de precio)", "price": {"value": "9.00", "currency": "EUR"}, "condition": "Usado"},
                {"itemId": "mock_013", "title": f"{query} Edición Limitada Coleccionista Sellado", "price": {"value": str(bp * 4), "currency": "EUR"}, "condition": "Nuevo"},
            ]
        }
