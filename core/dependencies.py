from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

from .enum import UserRole
from .security import verify_access_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """
    Dependency que extrae y valida el JWT Token del header de autorización.
    Retorna el usuario autenticado o lanza httpException si la autenticación falla.
    """
    # Extrae el token del header de autorización
    token =  credentials.credentials

    # Verifica y decodifica el token
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta información de usuario"
        )
    
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency que verifica si el usuario es administrador.
    
    Uso en endpoints:
        @router.delete("/users/{user_id}")
        def delete_user(admin: User = Depends(require_admin)):
            # Solo admins pueden ejecutar esto
    
    Returns:
        User: El usuario admin autenticado
        
    Raises:
        HTTPException 403: Si el usuario no es admin
    """

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requieren privilegios de administrador"
        )
    
    return current_user

def require_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency que verifica que el usuario esté autenticado.
    
    Es prácticamente un alias de get_current_user(), pero hace
    explícito en el código que el endpoint requiere autenticación.
    
    Uso en endpoints:
        @router.get("/my-tasks")
        def get_my_tasks(user: User = Depends(require_user)):
            # Cualquier usuario autenticado puede acceder
    """
    return current_user