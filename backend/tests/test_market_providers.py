import pytest
from app.services.market_data.base import MarketDataProvider
from app.services.market_data.mock_provider import MockMarketProvider
from app.services.market_data.ebay_provider import EbayMarketProvider

@pytest.mark.asyncio
async def test_mock_provider_is_deterministic():
    provider = MockMarketProvider()
    
    # Dos llamadas con el mismo query deben devolver EXACTAMENTE los mismos datos
    query = "Apple iPhone 15 128GB"
    result1 = await provider.search_comps(query)
    result2 = await provider.search_comps(query)
    
    assert result1 == result2
    assert len(result1["itemSummaries"]) > 0
    
    # Comprobar que incluye trampas
    titles = [item["title"].lower() for item in result1["itemSummaries"]]
    assert any("funda" in title or "case" in title for title in titles), "Debe contener accesorios trampa"
    assert any("roto" in title or "piezas" in title for title in titles), "Debe contener productos rotos"
    
    # Comprobar que un query distinto devuelve datos distintos
    query_different = "Nintendo Game Boy"
    result_different = await provider.search_comps(query_different)
    
    assert result1 != result_different

def test_providers_implement_same_interface():
    # Comprobar que ambas clases heredan de la base
    assert issubclass(MockMarketProvider, MarketDataProvider)
    assert issubclass(EbayMarketProvider, MarketDataProvider)
    
    # Comprobar que ambas tienen el método async search_comps
    import inspect
    assert inspect.iscoroutinefunction(MockMarketProvider.search_comps)
    assert inspect.iscoroutinefunction(EbayMarketProvider.search_comps)
