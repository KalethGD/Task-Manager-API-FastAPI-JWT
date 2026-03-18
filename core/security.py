from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import get_settings

#configuracion de bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    """Hashea la contraseña usando bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que la contraseña en texto plano coincida con la hasheada en DB."""
    return pwd_context.verify(plain_password, hashed_password)

settings = get_settings()

# Empezamos la configuracion de JWT (JSON Web Tokens)
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Crea un token de acceso JWT con la data que le pases

    Ejemplo:
        token = create_access_token(data={"sub": "usuario@gmail.com"})
        retorna = "ajsdaGKGjasndNBnnsd"
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({'exp': expire, 'token_type': 'access'})

    #Crear el token
    encode_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encode_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Crea un refresh token JWT de larga duración.
    Incluye 'token_type': 'refresh' para diferenciarlo del access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({'exp': expire, 'token_type': 'refresh'})

    encode_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encode_jwt


def verify_access_token(token: str) -> dict | None:
    """
    Verifica que el token JWT sea valido y retorna la data dentro del token.
    Rechaza explícitamente los refresh tokens para evitar que se usen como access tokens.
    Si el token no es valido, retorna None.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        # Rechazar refresh tokens usados como access tokens
        if payload.get('token_type') == 'refresh':
            return None
        return payload
    except JWTError:
        return None # Token no valido o expirado


def verify_refresh_token_payload(token: str) -> dict | None:
    """
    Decodifica y valida un refresh token JWT.
    Solo acepta tokens con token_type == 'refresh'.
    Retorna el payload o None si es inválido.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get('token_type') != 'refresh':
            return None
        return payload
    except JWTError:
        return None