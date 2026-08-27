import hashlib
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_ebay_webhook_get():
    # Setup test variables as per eBay challenge requirement
    challenge_code = "abc123"
    settings.EBAY_ACCOUNT_DELETION_VERIFICATION_TOKEN = "token_de_test"
    settings.EBAY_ACCOUNT_DELETION_ENDPOINT = "https://example.com/ebay-webhook"
    
    # Calculate expected hash
    expected_hash = hashlib.sha256(
        (challenge_code + "token_de_test" + "https://example.com/ebay-webhook").encode('utf-8')
    ).hexdigest()
    
    # Call the endpoint
    response = client.get(f"/ebay-webhook?challenge_code={challenge_code}")
    
    # Verify response
    assert response.status_code == 200
    assert response.json() == {"challengeResponse": expected_hash}

def test_ebay_webhook_post():
    # Test POST endpoint for account deletion notifications
    payload = {
        "metadata": {
            "topic": "MARKETPLACE_ACCOUNT_DELETION"
        }
    }
    response = client.post("/ebay-webhook", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"status": "acknowledged"}
