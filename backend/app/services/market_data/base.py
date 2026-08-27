from abc import ABC, abstractmethod

class MarketDataProvider(ABC):
    """
    Protocolo común para cualquier proveedor de datos de mercado (eBay, Wallapop, Mock, etc.).
    """
    @abstractmethod
    async def search_comps(self, query: str, limit: int = 15) -> dict:
        """
        Busca artículos comparables en el mercado.
        Debe devolver un diccionario con la estructura estándar:
        {
            "itemSummaries": [
                {
                    "itemId": str,
                    "title": str,
                    "price": {"value": str, "currency": str},
                    "condition": str
                }, ...
            ]
        }
        """
        pass
