import base64
import httpx
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from .base import MarketDataProvider

class EbayMarketProvider(MarketDataProvider):
    def __init__(self):
        self.client_id = settings.EBAY_CLIENT_ID
        self.client_secret = settings.EBAY_CLIENT_SECRET
        self.oauth_url = "https://api.ebay.com/identity/v1/oauth2/token"
        self.search_url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        
        self._cached_token = None
        self._token_expires_at = None

    async def get_token(self) -> str:
        if self.client_id == "mock_ebay_id":
            raise ValueError("Credenciales de eBay no configuradas")
            
        if self._cached_token and self._token_expires_at and datetime.now(timezone.utc) < self._token_expires_at:
            return self._cached_token
            
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_base64 = base64.b64encode(auth_string.encode("ascii")).decode("ascii")
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_base64}"
        }
        data = {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.oauth_url, headers=headers, data=data)
            
            if response.status_code == 200:
                resp_json = response.json()
                self._cached_token = resp_json.get("access_token")
                expires_in = int(resp_json.get("expires_in", 7200))
                self._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 60)
                return self._cached_token
            else:
                raise Exception(f"Fallo al obtener token de eBay: {response.text}")

    async def search_comps(self, query: str, limit: int = 15) -> dict:
        try:
            token = await self.get_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "X-EBAY-C-MARKETPLACE-ID": "EBAY_ES"
            }
            params = {
                "q": query,
                "limit": limit
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.search_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Error de mercado: {response.status_code} - {response.text}")
                    
        except Exception as e:
            # TAREA 8: No devolver precios inventados si falla eBay. Lanza un error controlado.
            raise Exception(f"market_data_unavailable: {str(e)}")
