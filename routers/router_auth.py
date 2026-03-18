from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.config import get_settings
from core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token_payload,
)
from database import get_db
from models import User
from models.model_refresh_token import RefreshToken
from schemas import schema_auth
from services import service_user

router = APIRouter(prefix='/auth', tags=['auth'])

settings = get_settings()


# Endpoint para login de usuario
@router.post('/login', response_model=schema_auth.Token, status_code=status.HTTP_200_OK)
def login(credentials: schema_auth.LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint de login que retorna un par de tokens: access + refresh.
    - access_token: corta duración (15 min), se usa en cada request.
    - refresh_token: larga duración (7 días), solo para renovar el access token.
    """
    user = service_user.authenticate_user(credentials.email, credentials.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    access_token = create_access_token(data={'sub': user.email})
    refresh_token = create_refresh_token(data={'sub': user.email})

    # Guardar refresh token en BD
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    db.add(RefreshToken(token=refresh_token, user_id=user.id, expires_at=expires_at))
    db.commit()

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }


@router.post('/refresh', status_code=status.HTTP_200_OK, response_model=schema_auth.Token)
def refresh_token(body: schema_auth.RefreshRequest, db: Session = Depends(get_db)):
    """
    Renueva el par de tokens usando un refresh token válido.
    Implementa rotación: el refresh token usado se invalida y se emite uno nuevo.
    El usuario permanece autenticado sin interrupciones mientras esté activo.
    """
    # 1. Verificar que el JWT sea válido y sea de tipo refresh
    payload = verify_refresh_token_payload(body.refresh_token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido o expirado")

    # 2. Verificar que exista en BD y no esté revocado
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == body.refresh_token,
        RefreshToken.is_revoked == False  # noqa: E712
    ).first()

    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido o revocado")

    # 3. Verificar que el usuario siga activo
    email: str = payload.get('sub')
    user = db.query(User).filter(User.email == email).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado o inactivo")

    # 4. Rotación: revocar el refresh token usado
    db_token.is_revoked = True
    db.flush()

    # 5. Emitir nuevo par de tokens
    new_access_token = create_access_token(data={'sub': user.email})
    new_refresh_token = create_refresh_token(data={'sub': user.email})

    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    db.add(RefreshToken(token=new_refresh_token, user_id=user.id, expires_at=expires_at))
    db.commit()

    return {
        'access_token': new_access_token,
        'refresh_token': new_refresh_token,
        'token_type': 'bearer'
    }


@router.post('/logout', status_code=status.HTTP_200_OK)
def logout(body: schema_auth.RefreshRequest, db: Session = Depends(get_db)):
    """
    Cierra la sesión revocando el refresh token en BD.
    El access token expirará solo (en <= 15 min).
    """
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == body.refresh_token
    ).first()

    if db_token:
        db_token.is_revoked = True
        db.commit()

    return {'message': 'Logout exitoso'}
