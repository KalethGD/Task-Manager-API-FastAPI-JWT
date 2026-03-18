from sqlalchemy.orm import Session

from core import security
from models import User
from schemas import schema_user


def get_users(db: Session) -> list[User]:
    """Retorna todos los usuarios de la base de datos."""
    return db.query(User).all()

def get_user_by_id(user_id: int, db: Session) -> User | None:
    """Retorna un usuario por su ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(email: str, db: Session) -> User | None:
    """Retorna un usuario por su email."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(username: str, db: Session) -> User | None:
    """Retorna un usuario por su nombre de usuario."""
    return db.query(User).filter(User.username == username).first()

def create_user(user_data: schema_user.UserCreate, db: Session) -> User:
    """ Crea un nuevo usuario en la base de datos."""
    try:
        user_dic = user_data.model_dump()
        user_dic['hashed_password'] = security.hash_password(user_dic.pop('password'))

        user = User(**user_dic)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise e
    
def authenticate_user(email: str, password: str, db: Session) -> User | None:
    """ Autentica a un usuario por su nombre de usuario y contraseña."""
    user = get_user_by_email(email, db)
    if not user:
        return None # Usuario no encontrado
    
    if not security.verify_password(password, user.hashed_password):
        return None # Contraseña incorrecta
    
    return user

def update_user(user_id: int, user_data: schema_user.UserUpdate, db: Session) -> User | None:
    """Actualiza un usuario existente en la base de datos."""
    try:
        user = get_user_by_id(user_id, db)
        if not user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == 'password':
                setattr(user, 'hashed_password', security.hash_password(value))
            else:
                setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise e

def delete_user(user_id: int, db: Session) -> bool:
    """Elimina un usuario de la base de datos."""
    try:
        user = get_user_by_id(user_id, db)
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e

