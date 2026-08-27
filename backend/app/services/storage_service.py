from supabase import create_client, Client
from app.core.config import settings

class StorageService:
    def __init__(self):
        # Si las claves son mock, no instanciamos para no dar error de conexión
        if settings.SUPABASE_URL != "mock_url" and settings.SUPABASE_KEY != "mock_key":
            self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        else:
            self.client = None

    def download_image(self, storage_path: str, bucket_name: str = "valuations") -> bytes:
        """
        Descarga la imagen desde Supabase Storage y la devuelve en bytes.
        """
        if not self.client:
            raise ValueError("Las credenciales reales de Supabase no están configuradas en el .env")
            
        try:
            # Supabase Python SDK: storage.from_().download() devuelve los bytes
            image_bytes = self.client.storage.from_(bucket_name).download(storage_path)
            return image_bytes
        except Exception as e:
            raise Exception(f"Fallo al descargar '{storage_path}' del bucket '{bucket_name}': {str(e)}")

storage_service = StorageService()
