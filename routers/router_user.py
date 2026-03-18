from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, require_admin
from core.enum import UserRole
from database import get_db
from models import User
from schemas import schema_user
from services import service_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# Endpoin para obtener todos los usuarios
@router.get('/', response_model=list[schema_user.UserResponse], status_code=status.HTTP_200_OK)
def get_all_users(
    admin: User = Depends(require_admin), 
    db: Session = Depends(get_db)):

    """
    Obtener todos los usuarios 
    REQUIERE: Rol administrador
    """
    return service_user.get_users(db)

# Endpoint para obetener un usuario por su ID
@router.get('/{user_id}', response_model=schema_user.UserResponse, status_code=status.HTTP_200_OK)
def get_user(
    user_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)):
    """ 
    Obtener un usuario por su ID 
    Los usuarios pueden ver su propio perfil, los admins pueden ver cualquier perfil.
    """
    user = service_user.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: No tienes permiso para ver este perfil"
        )
    return user

@router.get('/me/profile', response_model=schema_user.UserResponse, status_code=status.HTTP_200_OK)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """ 
    Obtener el perfil del usuario autenticado.
    Es mas facil que usar el endpoint general, porque no requiere pasar el ID del usuario.
    """
    return current_user

# Endpoint para crear un nuevo usuario
@router.post('/register', response_model=schema_user.UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_data: schema_user.UserCreate, 
    db: Session = Depends(get_db)):
    """
    Crear un nuevo usuario (registro público).
    Por defecto, los usuarios se crean con rol 'user'.
    Para crear un admin, debe hacerlo otro admin en /create-admin
    """
    if service_user.get_user_by_email(user_data.email, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El email: {user_data.email} ya está en uso"
        )
    
    if service_user.get_user_by_username(user_data.username, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El nombre de usuario: {user_data.username} ya está en uso"
        )
    user_data.role = UserRole.USER # Aseguramos que el rol sea USER aunque venga otro en el request
    new_user = service_user.create_user(user_data, db)
    return new_user

# Endpoint para crear un nuevo admin (solo para admins)
@router.post('/create-admin', response_model=schema_user.UserResponse, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    user_data: schema_user.UserCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)):
    if service_user.get_user_by_email(user_data.email, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El email: {user_data.email} ya está en uso"
        )
    
    if service_user.get_user_by_username(user_data.username, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El nombre de usuario: {user_data.username} ya está en uso"
        )
    
    #Forzamos el rol admin aunque venga otro en el request
    user_data.role = UserRole.ADMIN

    new_user = service_user.create_user(user_data, db)
    return new_user

@router.patch('/update/{user_id}', response_model=schema_user.UserResponse, status_code=status.HTTP_200_OK)
def update_user(
    user_id: int,
    user_data: schema_user.UserUpdate,
    admin: User = Depends(require_admin),  # ← SOLO ADMINS
    db: Session = Depends(get_db)):
    """
    Actualizar un usuario.
    REQUIERE: Rol de administrador
    """
    user = service_user.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    updated_user = service_user.update_user(user_id, user_data, db)
    return updated_user

@router.delete('/delete/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),  # ← SOLO ADMINS
    db: Session = Depends(get_db)):
    """
    Eliminar un usuario.
    REQUIERE: Rol de administrador
    """
    user = service_user.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Prevenir que un admin se elimine a sí mismo
    if admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propia cuenta de administrador"
        )
    
    service_user.delete_user(user_id, db)
    return None  # 204 no retorna contenido