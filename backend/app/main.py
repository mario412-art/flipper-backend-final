import hashlib
import logging
from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router

# TAREA 12: Configurar logging de errores técnicos
logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend de tasación con IA y eBay",
    version="1.0.0"
)

# Configuración permisiva de CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TAREA 12: Manejo de errores 500 (No exponer str(e) al cliente)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error interno crítico (500): {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error interno en el servidor. Por favor, inténtalo más tarde."},
    )

# ENDPOINT PARA VERIFICACIÓN DE EBAY MARKETPLACE ACCOUNT DELETION
@app.get("/ebay-webhook", tags=["eBay"])
async def ebay_verification_get(request: Request, challenge_code: str = Query(None)):
    if challenge_code:
        # 1. El token secreto configurado en el portal de eBay y en nuestras variables de entorno
        verification_token = settings.EBAY_ACCOUNT_DELETION_VERIFICATION_TOKEN
        
        # 2. El endpoint URL exacto al que eBay está llamando (fijado por variable de entorno)
        endpoint = settings.EBAY_ACCOUNT_DELETION_ENDPOINT
        
        # 3. Fórmula de eBay: challengeCode + verificationToken + endpointUrl
        raw_string = challenge_code + verification_token + endpoint
        
        # 4. Encriptar en SHA-256 (hex)
        hashed = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()
        
        return JSONResponse(content={"challengeResponse": hashed})
    
    return JSONResponse(status_code=400, content={"error": "Missing challenge_code parameter"})

@app.post("/ebay-webhook", tags=["eBay"])
async def ebay_verification_post(request: Request):
    # Recibir las notificaciones de eliminación de cuenta
    try:
        payload = await request.json()
        # Registrar de forma segura la recepción (sin exponer PII)
        logger.info(f"Recibida notificación de eBay Account Deletion para tipo de evento: {payload.get('metadata', {}).get('topic')}")
        
        # Por ahora no hacemos nada más que reconocer la recepción y devolver 200 OK
        return JSONResponse(status_code=200, content={"status": "acknowledged"})
    except Exception as e:
        logger.error("Error procesando payload de eBay webhook")
        return JSONResponse(status_code=400, content={"error": "Bad request"})

# TAREA 13: Health Check
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

# Montar las rutas de la API bajo el prefijo /v1
app.include_router(api_router, prefix="/v1")
