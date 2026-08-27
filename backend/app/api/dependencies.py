from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.core.config import settings

# HTTPBearer extraerá automáticamente el token de la cabecera 'Authorization: Bearer <token>'
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Valida el JWT emitido por Supabase Auth y extrae el ID del usuario.
    Retorna el 'user_id' (UUID) que hizo la petición.
    """
    token = credentials.credentials
    
    # El backend obtiene el user_id EXCLUSIVAMENTE del JWT real emitido por Supabase.
    # Dado que tu proyecto usa las nuevas "JWT Signing Keys" (migradas del legacy secret),
    # usamos el SDK oficial de Supabase para validar el token asimétrico sin rompernos la cabeza.
    try:
        from app.services.storage_service import storage_service
        
        if not storage_service.client:
            raise HTTPException(status_code=500, detail="El cliente de Supabase no está inicializado en el backend.")
            
        # get_user llama internamente a la API de Supabase Auth para validar el token y devolver el usuario
        user_response = storage_service.client.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token inválido o expirado según Supabase"
            )
            
        return user_response.user.id
        
    except Exception as e:
        print(f"DEBUG Auth Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales de autenticación inválidas (Fallo al validar con Supabase)"
        )
