from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """ Esquema para iniciar Sesión """
    email: EmailStr
    password: str

class Token(BaseModel):
    """ Esquema para el Token de Autenticación """
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    """ Esquema para los datos del Token """
    email: EmailStr | None = None

class RefreshRequest(BaseModel):
    """ Esquema para solicitar un nuevo par de tokens """
    refresh_token: str