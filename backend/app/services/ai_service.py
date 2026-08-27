from google import genai
from google.genai import types
from app.core.config import settings
from app.models.schemas import AIProductIdentification
import PIL.Image
import io

class AIService:
    def __init__(self):
        # Inicializar el cliente usando la clave del .env
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY != "mock_gemini" else None

    async def identify_product(self, image_bytes: bytes) -> AIProductIdentification:
        """
        Analiza la imagen usando Gemini 3.6-flash obligando a una salida estructurada exacta.
        """
        if not self.client:
            raise ValueError("GEMINI_API_KEY no configurada correctamente")
            
        try:
            image = PIL.Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            raise ValueError(f"No se pudo decodificar la imagen: {e}")
            
        prompt = """
        Eres un experto tasador de productos de segunda mano (electrónica, zapatillas, móviles, ropa, etc.).
        Analiza esta imagen y extrae los detalles del producto de forma precisa.
        Si no estás seguro de un dato, devuelve null. No inventes nunca el GTIN/código de barras.
        """
        
        # Obligamos a Gemini a devolver exactamente la estructura de Pydantic asíncronamente
        response = await self.client.aio.models.generate_content(
            model='gemini-3.6-flash',
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AIProductIdentification,
                temperature=0.1, # Temperatura baja para que sea determinista y analítico
            )
        )
        
        # Pydantic parsea y valida el JSON devuelto para garantizar el contrato
        return AIProductIdentification.model_validate_json(response.text)

ai_service = AIService()
