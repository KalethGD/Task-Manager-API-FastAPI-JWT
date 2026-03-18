from enum import Enum


class UserRole(str, Enum):
    """
    Roles de usuario en el sistema

    str: Hereda de str para que se serealice bien
    Enum: Define un conjunto cerrado de valores 
    """
    ADMIN = 'admin' #Administrador con todos los permisos
    USER = 'user'   #Usuario con permisos limitados